"""
Stream Module - Real-time Binance WebSocket Data Streaming
===========================================================

This module provides high-performance WebSocket connections for real-time
market data streaming. Supports multiple streams, automatic reconnection,
and clean async/callback patterns.

Features:
    - Trade streams (real-time executed trades)
    - Kline/Candlestick streams (live OHLCV updates)
    - Ticker streams (24hr rolling window statistics)
    - Order book depth streams (real-time market depth)
    - Aggregate trade streams (compressed trade data)
    - Mini ticker streams (lightweight price updates)
    - Individual and combined streams
    - Automatic reconnection on disconnect
    - Thread-safe callback handling

Example Usage:
    >>> from liminal import Stream
    >>>
    >>> def handle_trade(trade):
    ...     print(f"Trade: {trade['p']} @ {trade['q']}")
    >>>
    >>> stream = Stream()
    >>> stream.subscribe_trades("BTCUSDT", callback=handle_trade)
    >>> stream.start()  # Blocks until stopped
    >>>
    >>> # Or use context manager
    >>> with Stream() as stream:
    ...     stream.subscribe_klines("BTCUSDT", "1m", callback=handle_kline)
    ...     stream.run()

Author: Athen Traverne
License: MIT
"""

import json
import threading
import time
import typing
from collections import defaultdict
from enum import Enum

import websocket

from .exceptions import LiminalError, validate


class StreamType(Enum):
    """WebSocket stream types supported by Binance."""

    TRADE = "trade"
    KLINE = "kline"
    MINI_TICKER = "miniTicker"
    TICKER = "ticker"
    DEPTH = "depth"
    AGG_TRADE = "aggTrade"
    BOOK_TICKER = "bookTicker"


class Stream:
    """
    Real-time WebSocket data streaming client.

    Manages WebSocket connections to Binance for real-time market data.
    Supports multiple concurrent streams with individual callbacks.

    Attributes:
        endpoint (str): WebSocket base endpoint
        ws (websocket.WebSocketApp): WebSocket connection object
        subscriptions (dict): Active stream subscriptions
        running (bool): Whether stream is currently active
        callbacks (dict): Registered callback functions
        reconnect (bool): Whether to auto-reconnect on disconnect
        reconnect_delay (int): Seconds to wait before reconnecting

    Example:
        >>> stream = Stream()
        >>> stream.subscribe_trades("BTCUSDT", callback=print)
        >>> stream.start()
    """

    endpoint: str = "wss://stream.binance.com:9443"
    ws: typing.Optional[websocket.WebSocketApp] = None
    subscriptions: dict[str, dict] = {}
    running: bool = False
    callbacks: dict[str, list] = defaultdict(list)
    reconnect: bool = True
    reconnect_delay: int = 5
    _thread: typing.Optional[threading.Thread] = None
    _lock: threading.Lock

    def __init__(self, endpoint: str = "", reconnect: bool = True) -> None:
        """
        Initialize Stream with optional custom endpoint.

        Args:
            endpoint (str, optional): Custom WebSocket endpoint.
                Uses default Binance endpoint if not provided.
            reconnect (bool, optional): Enable automatic reconnection.
                Defaults to True.

        Example:
            >>> stream = Stream()  # Default endpoint
            >>> stream = Stream(reconnect=False)  # No auto-reconnect
        """
        if endpoint:
            self.endpoint = endpoint

        self.reconnect = reconnect
        self.subscriptions = {}
        self.callbacks = defaultdict(list)
        self._lock = threading.Lock()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.stop()

    def _build_stream_name(
        self, symbol: str, stream_type: StreamType, interval: str | None = None
    ) -> str:
        """
        Build stream name according to Binance format.

        Args:
            symbol (str): Trading pair symbol
            stream_type (StreamType): Type of stream
            interval (str, optional): For kline streams (e.g., "1m", "1h")

        Returns:
            str: Formatted stream name

        Example:
            >>> self._build_stream_name("BTCUSDT", StreamType.TRADE)
            'btcusdt@trade'
            >>> self._build_stream_name("BTCUSDT", StreamType.KLINE, "1h")
            'btcusdt@kline_1h'
        """
        symbol_lower = symbol.lower()

        if stream_type == StreamType.KLINE:
            validate(interval is not None, "Interval required for kline streams")
            return f"{symbol_lower}@{stream_type.value}_{interval}"
        else:
            return f"{symbol_lower}@{stream_type.value}"

    def _build_ws_url(self, streams: list[str]) -> str:
        """
        Build WebSocket URL for single or combined streams.

        Args:
            streams (list[str]): List of stream names

        Returns:
            str: Complete WebSocket URL

        Example:
            >>> self._build_ws_url(["btcusdt@trade"])
            'wss://stream.binance.com:9443/ws/btcusdt@trade'
            >>> self._build_ws_url(["btcusdt@trade", "ethusdt@trade"])
            'wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade'
        """
        if len(streams) == 1:
            return f"{self.endpoint}/ws/{streams[0]}"
        else:
            combined = "/".join(streams)
            return f"{self.endpoint}/stream?streams={combined}"

    def _on_message(self, ws, message: str) -> None:
        """
        Handle incoming WebSocket messages.

        Parses messages and dispatches to registered callbacks.

        Args:
            ws: WebSocket connection object
            message (str): Raw JSON message from server
        """
        try:
            data = json.loads(message)

            # Handle combined stream format
            if "stream" in data:
                stream_name = data["stream"]
                stream_data = data["data"]
            else:
                # Single stream format - determine stream from event type
                stream_data = data
                if "e" in data:
                    event_type = data["e"]
                    symbol = data.get("s", "").lower()

                    if event_type == "trade":
                        stream_name = f"{symbol}@trade"
                    elif event_type == "kline":
                        interval = data["k"]["i"]
                        stream_name = f"{symbol}@kline_{interval}"
                    elif event_type == "24hrTicker":
                        stream_name = f"{symbol}@ticker"
                    elif event_type == "24hrMiniTicker":
                        stream_name = f"{symbol}@miniTicker"
                    elif event_type == "aggTrade":
                        stream_name = f"{symbol}@aggTrade"
                    elif event_type == "depthUpdate":
                        stream_name = f"{symbol}@depth"
                    else:
                        stream_name = None
                else:
                    stream_name = None

            # Dispatch to callbacks
            if stream_name and stream_name in self.callbacks:
                with self._lock:
                    for callback in self.callbacks[stream_name]:
                        try:
                            callback(stream_data)
                        except Exception as e:
                            print(f"[Stream] Error in callback for {stream_name}: {e}")

        except json.JSONDecodeError as e:
            print(f"[Stream] Failed to parse message: {e}")
        except Exception as e:
            print(f"[Stream] Error handling message: {e}")

    def _on_error(self, ws, error) -> None:
        """
        Handle WebSocket errors.

        Args:
            ws: WebSocket connection object
            error: Error object or message
        """
        print(f"[Stream] WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg) -> None:
        """
        Handle WebSocket connection close.

        Attempts reconnection if enabled.

        Args:
            ws: WebSocket connection object
            close_status_code: Status code from server
            close_msg: Close message from server
        """
        print(f"[Stream] Connection closed: {close_status_code} - {close_msg}")
        self.running = False

        if self.reconnect and len(self.subscriptions) > 0:
            print(f"[Stream] Reconnecting in {self.reconnect_delay} seconds...")
            time.sleep(self.reconnect_delay)
            self._connect()

    def _on_open(self, ws) -> None:
        """
        Handle WebSocket connection open.

        Args:
            ws: WebSocket connection object
        """
        print("[Stream] WebSocket connection opened")
        self.running = True

    def _connect(self) -> None:
        """
        Establish WebSocket connection with current subscriptions.

        Creates WebSocket connection and starts listening for messages.
        """
        if len(self.subscriptions) == 0:
            raise LiminalError("No active subscriptions. Subscribe to streams first.")

        # Build URL with all active streams
        streams = list(self.subscriptions.keys())
        url = self._build_ws_url(streams)

        print(f"[Stream] Connecting to: {url}")

        # Create WebSocket connection
        self.ws = websocket.WebSocketApp(
            url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open,
        )

        # Run WebSocket
        self.ws.run_forever()

    def subscribe_trades(
        self, symbol: str, callback: typing.Callable[[dict], None]
    ) -> None:
        """
        Subscribe to real-time trade stream.

        Receives every trade executed on the exchange in real-time.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            callback (callable): Function to handle trade data

        Trade data format:
            {
                "e": "trade",           # Event type
                "E": 1672515782136,     # Event time
                "s": "BTCUSDT",         # Symbol
                "t": 12345,             # Trade ID
                "p": "50000.00",        # Price
                "q": "0.001",           # Quantity
                "b": 88,                # Buyer order ID
                "a": 50,                # Seller order ID
                "T": 1672515782136,     # Trade time
                "m": true,              # Is buyer maker?
                "M": true               # Ignore
            }

        Example:
            >>> def handle_trade(data):
            ...     print(f"Trade: {data['p']} @ {data['q']}")
            >>>
            >>> stream.subscribe_trades("BTCUSDT", callback=handle_trade)
        """
        stream_name = self._build_stream_name(symbol, StreamType.TRADE)

        with self._lock:
            self.subscriptions[stream_name] = {
                "symbol": symbol,
                "type": StreamType.TRADE,
            }
            self.callbacks[stream_name].append(callback)

        print(f"[Stream] Subscribed to {stream_name}")

    def subscribe_klines(
        self, symbol: str, interval: str, callback: typing.Callable[[dict], None]
    ) -> None:
        """
        Subscribe to real-time candlestick/kline stream.

        Receives kline updates as they form in real-time.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            interval (str): Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
            callback (callable): Function to handle kline data

        Kline data format:
            {
                "e": "kline",               # Event type
                "E": 1672515782136,         # Event time
                "s": "BTCUSDT",             # Symbol
                "k": {
                    "t": 1672515780000,     # Kline start time
                    "T": 1672515839999,     # Kline close time
                    "s": "BTCUSDT",         # Symbol
                    "i": "1m",              # Interval
                    "f": 100,               # First trade ID
                    "L": 200,               # Last trade ID
                    "o": "50000.00",        # Open price
                    "c": "50100.00",        # Close price
                    "h": "50200.00",        # High price
                    "l": "49900.00",        # Low price
                    "v": "10.0",            # Base asset volume
                    "n": 100,               # Number of trades
                    "x": false,             # Is kline closed?
                    "q": "500000.00",       # Quote asset volume
                    "V": "5.0",             # Taker buy base volume
                    "Q": "250000.00",       # Taker buy quote volume
                    "B": "0"                # Ignore
                }
            }

        Example:
            >>> def handle_kline(data):
            ...     k = data['k']
            ...     if k['x']:  # Kline is closed
            ...         print(f"Closed: O:{k['o']} H:{k['h']} L:{k['l']} C:{k['c']}")
            >>>
            >>> stream.subscribe_klines("BTCUSDT", "1m", callback=handle_kline)
        """
        stream_name = self._build_stream_name(symbol, StreamType.KLINE, interval)

        with self._lock:
            self.subscriptions[stream_name] = {
                "symbol": symbol,
                "type": StreamType.KLINE,
                "interval": interval,
            }
            self.callbacks[stream_name].append(callback)

        print(f"[Stream] Subscribed to {stream_name}")

    def subscribe_ticker(
        self, symbol: str, callback: typing.Callable[[dict], None]
    ) -> None:
        """
        Subscribe to 24hr rolling window ticker statistics.

        Receives ticker updates every second with 24hr statistics.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            callback (callable): Function to handle ticker data

        Ticker data format:
            {
                "e": "24hrTicker",          # Event type
                "E": 1672515782136,         # Event time
                "s": "BTCUSDT",             # Symbol
                "p": "100.00",              # Price change
                "P": "0.20",                # Price change percent
                "w": "50000.00",            # Weighted average price
                "x": "49900.00",            # First trade price
                "c": "50000.00",            # Last price
                "Q": "10.0",                # Last quantity
                "b": "49999.00",            # Best bid price
                "B": "5.0",                 # Best bid quantity
                "a": "50001.00",            # Best ask price
                "A": "5.0",                 # Best ask quantity
                "o": "49900.00",            # Open price
                "h": "50200.00",            # High price
                "l": "49800.00",            # Low price
                "v": "1000.0",              # Total traded base volume
                "q": "50000000.00",         # Total traded quote volume
                "O": 1672429382136,         # Statistics open time
                "C": 1672515782136,         # Statistics close time
                "F": 100,                   # First trade ID
                "L": 200,                   # Last trade ID
                "n": 100                    # Total number of trades
            }

        Example:
            >>> def handle_ticker(data):
            ...     print(f"{data['s']}: {data['c']} ({data['P']}%)")
            >>>
            >>> stream.subscribe_ticker("BTCUSDT", callback=handle_ticker)
        """
        stream_name = self._build_stream_name(symbol, StreamType.TICKER)

        with self._lock:
            self.subscriptions[stream_name] = {
                "symbol": symbol,
                "type": StreamType.TICKER,
            }
            self.callbacks[stream_name].append(callback)

        print(f"[Stream] Subscribed to {stream_name}")

    def subscribe_mini_ticker(
        self, symbol: str, callback: typing.Callable[[dict], None]
    ) -> None:
        """
        Subscribe to mini ticker (lightweight 24hr statistics).

        Similar to ticker but with fewer fields for reduced bandwidth.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            callback (callable): Function to handle mini ticker data

        Mini ticker data format:
            {
                "e": "24hrMiniTicker",      # Event type
                "E": 1672515782136,         # Event time
                "s": "BTCUSDT",             # Symbol
                "c": "50000.00",            # Close price
                "o": "49900.00",            # Open price
                "h": "50200.00",            # High price
                "l": "49800.00",            # Low price
                "v": "1000.0",              # Total traded base volume
                "q": "50000000.00"          # Total traded quote volume
            }

        Example:
            >>> def handle_mini(data):
            ...     print(f"{data['s']}: {data['c']}")
            >>>
            >>> stream.subscribe_mini_ticker("BTCUSDT", callback=handle_mini)
        """
        stream_name = self._build_stream_name(symbol, StreamType.MINI_TICKER)

        with self._lock:
            self.subscriptions[stream_name] = {
                "symbol": symbol,
                "type": StreamType.MINI_TICKER,
            }
            self.callbacks[stream_name].append(callback)

        print(f"[Stream] Subscribed to {stream_name}")

    def subscribe_depth(
        self, symbol: str, callback: typing.Callable[[dict], None], levels: int = 20
    ) -> None:
        """
        Subscribe to order book depth updates.

        Receives partial order book updates as they occur.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            callback (callable): Function to handle depth data
            levels (int, optional): Depth levels (5, 10, or 20). Defaults to 20.

        Depth data format:
            {
                "e": "depthUpdate",         # Event type
                "E": 1672515782136,         # Event time
                "s": "BTCUSDT",             # Symbol
                "U": 157,                   # First update ID
                "u": 160,                   # Final update ID
                "b": [                      # Bids to update
                    ["50000.00", "10.0"],   # [Price, Quantity]
                    ["49999.00", "5.0"]
                ],
                "a": [                      # Asks to update
                    ["50001.00", "8.0"],
                    ["50002.00", "3.0"]
                ]
            }

        Example:
            >>> def handle_depth(data):
            ...     print(f"Bids: {len(data['b'])}, Asks: {len(data['a'])}")
            >>>
            >>> stream.subscribe_depth("BTCUSDT", callback=handle_depth)
        """
        validate(levels in [5, 10, 20], "Depth levels must be 5, 10, or 20")

        stream_name = f"{symbol.lower()}@depth{levels}"

        with self._lock:
            self.subscriptions[stream_name] = {
                "symbol": symbol,
                "type": StreamType.DEPTH,
                "levels": levels,
            }
            self.callbacks[stream_name].append(callback)

        print(f"[Stream] Subscribed to {stream_name}")

    def subscribe_agg_trades(
        self, symbol: str, callback: typing.Callable[[dict], None]
    ) -> None:
        """
        Subscribe to aggregate trade stream.

        Aggregates trades that occur at the same time, price, and side.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            callback (callable): Function to handle aggregate trade data

        Aggregate trade data format:
            {
                "e": "aggTrade",            # Event type
                "E": 1672515782136,         # Event time
                "s": "BTCUSDT",             # Symbol
                "a": 12345,                 # Aggregate trade ID
                "p": "50000.00",            # Price
                "q": "10.0",                # Quantity
                "f": 100,                   # First trade ID
                "l": 105,                   # Last trade ID
                "T": 1672515782136,         # Trade time
                "m": true,                  # Is buyer maker?
                "M": true                   # Ignore
            }

        Example:
            >>> def handle_agg(data):
            ...     print(f"Agg Trade: {data['p']} @ {data['q']}")
            >>>
            >>> stream.subscribe_agg_trades("BTCUSDT", callback=handle_agg)
        """
        stream_name = self._build_stream_name(symbol, StreamType.AGG_TRADE)

        with self._lock:
            self.subscriptions[stream_name] = {
                "symbol": symbol,
                "type": StreamType.AGG_TRADE,
            }
            self.callbacks[stream_name].append(callback)

        print(f"[Stream] Subscribed to {stream_name}")

    def unsubscribe(
        self, symbol: str, stream_type: StreamType, interval: str | None = None
    ) -> None:
        """
        Unsubscribe from a specific stream.

        Args:
            symbol (str): Trading pair symbol
            stream_type (StreamType): Type of stream to unsubscribe from
            interval (str, optional): For kline streams

        Example:
            >>> stream.unsubscribe("BTCUSDT", StreamType.TRADE)
            >>> stream.unsubscribe("BTCUSDT", StreamType.KLINE, "1m")
        """
        stream_name = self._build_stream_name(symbol, stream_type, interval)

        with self._lock:
            if stream_name in self.subscriptions:
                del self.subscriptions[stream_name]
                if stream_name in self.callbacks:
                    del self.callbacks[stream_name]
                print(f"[Stream] Unsubscribed from {stream_name}")
            else:
                print(f"[Stream] Not subscribed to {stream_name}")

    def start(self) -> None:
        """
        Start WebSocket stream (blocking).

        Connects to WebSocket and starts receiving data. This method blocks
        until stop() is called or connection is closed.

        Example:
            >>> stream = Stream()
            >>> stream.subscribe_trades("BTCUSDT", callback=print)
            >>> stream.start()  # Blocks here
        """
        self._connect()

    def start_async(self) -> None:
        """
        Start WebSocket stream in background thread (non-blocking).

        Useful when you need to run the stream while doing other work.

        Example:
            >>> stream = Stream()
            >>> stream.subscribe_trades("BTCUSDT", callback=print)
            >>> stream.start_async()  # Returns immediately
            >>> # Do other work...
            >>> stream.stop()
        """
        if self._thread and self._thread.is_alive():
            print("[Stream] Already running")
            return

        self._thread = threading.Thread(target=self._connect, daemon=True)
        self._thread.start()
        print("[Stream] Started in background thread")

    def stop(self) -> None:
        """
        Stop WebSocket stream and close connection.

        Example:
            >>> stream.stop()
        """
        if self.ws:
            self.reconnect = False  # Prevent reconnection
            self.ws.close()
            self.running = False
            print("[Stream] Stopped")

    def is_running(self) -> bool:
        """
        Check if stream is currently active.

        Returns:
            bool: True if stream is running, False otherwise

        Example:
            >>> if stream.is_running():
            ...     print("Stream is active")
        """
        return self.running

    def get_subscriptions(self) -> dict[str, dict]:
        """
        Get all active subscriptions.

        Returns:
            dict: Dictionary of active stream subscriptions

        Example:
            >>> subs = stream.get_subscriptions()
            >>> print(f"Active streams: {list(subs.keys())}")
        """
        with self._lock:
            return self.subscriptions.copy()
