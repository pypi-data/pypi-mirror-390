"""
Oracle Module - Real-Time Market Data Retrieval Module
===================================================

A lightweight, high-performance interface for retrieving cryptocurrency spot market data.
Provides seamless access to price feeds, order book depth, trade execution history,
OHLCV candlesticks, and comprehensive market statistics.

Built for quantitative analysis and algorithmic trading, Oracle delivers clean pandas
DataFrames with strongly-typed columns, ready for immediate analysis and modeling.

Example Usage:
    >>> from liminal import Oracle
    >>> oracle = Oracle()
    >>>
    >>> # Get current price
    >>> price_data = oracle.price("BTCUSDT")
    >>>
    >>> # Get candlestick data
    >>> klines = oracle.klines("BTCUSDT", interval="1h", limit=100)
    >>>
    >>> # Get order book
    >>> orderbook = oracle.orderbook("BTCUSDT", depth=100)

Author: Athen Traverne
License: MIT
"""

import re
import typing

import httpx
import orjson
import pandas

from .exceptions import LiminalError, validate


class Oracle:
    """
    Binance Spot Market Data Oracle.

    A lightweight client for retrieving and analyzing Binance spot market data.
    Provides clean, typed pandas DataFrames for necessary market data endpoints.

    Attributes:
        url (str): Full API URL (endpoint + suffix)
        endpoint (str): Base Binance API endpoint
        suffix (str): API version suffix (/api/v3)
        timeout (int): HTTP request timeout in seconds

    Example:
        >>> oracle = Oracle()  # Uses default endpoint
        >>> oracle = Oracle(endpoint="https://api1.binance.com")  # Custom endpoint
        >>> oracle.configure_timeout(30)  # Set 30 second timeout
    """

    url: str
    endpoint: str = "https://api.binance.com"
    suffix: str = "/api/v3"
    timeout: int = 10

    def __init__(self, endpoint: str = "") -> None:
        """
        Initialize Oracle with optional custom endpoint.

        Validates endpoint connectivity on initialization. Raises error if
        the endpoint is not responding.

        Args:
            endpoint (str, optional): Custom Binance API endpoint.
                Uses default "https://api.binance.com" if not provided.

        Raises:
            LiminalError: If the endpoint is not responding or invalid.

        Example:
            >>> oracle = Oracle()
            >>> oracle = Oracle(endpoint="https://api-gcp.binance.com")
        """
        if endpoint:
            self.endpoint = endpoint

        self.url = f"{self.endpoint}{self.suffix}"
        validate(self.status(), f"[Server] Endpoint: {self.endpoint} is not responding")

    def build(self, path: str) -> str:
        """
        Build full API URL from path.

        Args:
            path (str): API endpoint path (e.g., "ticker/price")

        Returns:
            str: Complete URL with base endpoint and path

        Example:
            >>> oracle.build("ticker/price")
            'https://api.binance.com/api/v3/ticker/price'
        """
        return f"{self.url}/{path}"

    def sequence(self, params: list[str]) -> str:
        """
        Convert list of parameters to JSON string format.

        Used internally for multi-symbol queries that require JSON array format.

        Args:
            params (list[str]): List of parameters (typically symbols)

        Returns:
            str: JSON-encoded string

        Example:
            >>> oracle.sequence(["BTCUSDT", "ETHUSDT"])
            '["BTCUSDT","ETHUSDT"]'
        """
        return orjson.dumps(params).decode("utf-8")

    def status(self) -> bool:
        """
        Check if API endpoint is responding.

        Sends a ping request to verify endpoint connectivity.

        Returns:
            bool: True if endpoint is responding, False otherwise

        Example:
            >>> if oracle.status():
            ...     print("API is online")
        """
        try:
            self.request("ping")
        except LiminalError:
            return False
        else:
            return True

    def configure_timeout(self, timeout: int) -> None:
        """
        Configure HTTP request timeout.

        Args:
            timeout (int): Timeout in seconds (must be positive)

        Raises:
            LiminalError: If timeout is not positive

        Example:
            >>> oracle.configure_timeout(30)  # 30 second timeout
        """
        validate(timeout > 0, "Timeout cannot be negative")
        self.timeout = timeout

    def request(self, path: str, payload: dict | None = None) -> typing.Any:
        """
        Make HTTP GET request to Binance API.

        Internal method that handles all API communication, error handling,
        and response parsing.

        Args:
            path (str): API endpoint path
            payload (dict | None, optional): Query parameters

        Returns:
            typing.Any: Parsed JSON response (dict or list)

        Raises:
            LiminalError: If API returns error or request fails

        Example:
            >>> data = oracle.request("time")
            >>> data = oracle.request("ticker/price", {"symbol": "BTCUSDT"})
        """
        response = httpx.get(self.build(path), params=payload, timeout=self.timeout)

        if not response.is_success:
            error = response.json()
            raise LiminalError(
                f"[Server] Error code: {error['code']}; Error: {error['msg']}"
            )

        return orjson.loads(response.content)

    def get_server_time(self) -> int:
        """
        Get current Binance server time.

        Returns:
            int: Unix timestamp in milliseconds

        Example:
            >>> server_time = oracle.get_server_time()
            >>> print(server_time)
            1699123456789
        """
        data = self.request("time")
        return data["serverTime"]

    def exchange_info(self, symbol: str | list[str]) -> dict:
        """
        Get exchange trading rules and symbol information.

        Retrieves comprehensive information about trading symbols including
        filters, permissions, price precision, and quantity limits.

        Args:
            symbol (str | list[str]): Single symbol or list of symbols

        Returns:
            dict: Exchange information containing symbol details, filters, etc.

        Raises:
            LiminalError: If symbol is invalid or empty list provided

        Example:
            >>> # Single symbol
            >>> info = oracle.exchange_info("BTCUSDT")
            >>>
            >>> # Multiple symbols
            >>> info = oracle.exchange_info(["BTCUSDT", "ETHUSDT"])
        """
        payload = {}

        if isinstance(symbol, list):
            validate(len(symbol) > 0, "No params provided")
            [validate(Oracle.is_valid_symbol(s), "Invalid symbol") for s in symbol]
            payload["symbols"] = self.sequence(symbol)

        else:
            validate(Oracle.is_valid_symbol(symbol), "Invalid symbol")
            payload["symbol"] = symbol

        data = self.request("exchangeInfo", payload)
        return data

    def orderbook(self, symbol: str, depth: int = 100) -> pandas.DataFrame:
        """
        Get current order book (market depth) for a symbol.

        Returns bids and asks with prices and quantities. Results are combined
        into a single DataFrame with a 'side' column indicating bid/ask.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            depth (int, optional): Number of price levels (max 5000). Defaults to 100.

        Returns:
            pandas.DataFrame: Order book with columns:
                - price (float): Price level
                - qty (float): Quantity at price level
                - side (str): "bids" or "asks"

        Raises:
            LiminalError: If symbol is invalid or depth exceeds 5000

        Example:
            >>> orderbook = oracle.orderbook("BTCUSDT", depth=20)
            >>> top_bid = orderbook[orderbook['side'] == 'bids'].iloc[0]
            >>> print(f"Best bid: {top_bid['price']} @ {top_bid['qty']}")
        """
        validate(Oracle.is_valid_symbol(symbol), "Invalid symbol")
        validate(depth <= 5000, "Orderbook depth can be maximum 5000")

        payload = {"symbol": symbol, "limit": depth}

        data = self.request("depth", payload)

        columns = ["price", "qty"]

        bids = pandas.DataFrame(data["bids"], columns=columns).astype(float)
        asks = pandas.DataFrame(data["asks"], columns=columns).astype(float)

        bids["side"] = "bids"
        asks["side"] = "asks"

        return pandas.concat([bids, asks])

    def trades(self, symbol: str, limit: int = 500) -> pandas.DataFrame:
        """
        Get recent trades for a symbol.

        Retrieves the most recent trades executed on the exchange.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            limit (int, optional): Number of trades to retrieve (max 1000).
                Defaults to 500.

        Returns:
            pandas.DataFrame: Recent trades with columns including:
                - id: Trade ID
                - price (float): Trade price
                - qty (float): Trade quantity
                - quoteQty (float): Quote asset quantity
                - time: Trade timestamp
                - isBuyerMaker: Whether buyer is maker
                - isBestMatch: Whether trade is best price match

        Raises:
            LiminalError: If symbol is invalid or limit exceeds 1000

        Example:
            >>> trades = oracle.trades("BTCUSDT", limit=100)
            >>> avg_price = trades['price'].mean()
            >>> total_volume = trades['qty'].sum()
        """
        validate(Oracle.is_valid_symbol(symbol), "Invalid symbol")
        validate(limit <= 1000, "Trades limit can be maximum 1000")

        payload = {"symbol": symbol, "limit": limit}

        data = self.request("trades", payload)

        df = pandas.DataFrame(data)
        df[["price", "qty", "quoteQty"]] = df[["price", "qty", "quoteQty"]].astype(
            float
        )

        return df

    def historical_trades(
        self, symbol: str, from_id: int = 0, limit: int = 500
    ) -> pandas.DataFrame:
        """
        Get historical trades from a specific trade ID.

        Retrieves older trades starting from a specified trade ID. Useful for
        building comprehensive trade history datasets.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            from_id (int, optional): Trade ID to start from. Defaults to 0 (earliest).
            limit (int, optional): Number of trades (max 1000). Defaults to 500.

        Returns:
            pandas.DataFrame: Historical trades with same structure as trades()

        Raises:
            LiminalError: If symbol is invalid or limit exceeds 1000

        Example:
            >>> # Get trades starting from specific ID
            >>> trades = oracle.historical_trades("BTCUSDT", from_id=1000000, limit=500)
        """
        validate(Oracle.is_valid_symbol(symbol), "Invalid symbol")
        validate(limit <= 1000, "Trades limit can be maximum 1000")

        payload = {"symbol": symbol, "limit": limit}

        if from_id:
            payload["fromId"] = from_id

        data = self.request("historicalTrades", payload)

        df = pandas.DataFrame(data)
        df[["price", "qty", "quoteQty"]] = df[["price", "qty", "quoteQty"]].astype(
            float
        )

        return df

    def aggregate_trades(
        self,
        symbol: str,
        from_id: int = 0,
        start_time: int = 0,
        end_time: int = 0,
        limit: int = 500,
    ) -> pandas.DataFrame:
        """
        Get compressed, aggregate trades.

        Aggregates multiple trades that occurred at the same time, price, and
        side into single entries. More efficient for analyzing trade flow.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            from_id (int, optional): Aggregate trade ID to start from
            start_time (int, optional): Start timestamp in milliseconds
            end_time (int, optional): End timestamp in milliseconds
            limit (int, optional): Number of trades (max 1000). Defaults to 500.

        Returns:
            pandas.DataFrame: Aggregate trades with columns:
                - agg_trade_id: Aggregate trade ID
                - price (float): Trade price
                - quantity (float): Total quantity
                - first_trade_id: First trade ID in aggregate
                - last_trade_id: Last trade ID in aggregate
                - timestamp_ms: Trade timestamp
                - is_buyer_maker: Whether buyer was maker
                - best_price_match: Whether trade was best price match

        Raises:
            LiminalError: If symbol is invalid or limit exceeds 1000

        Example:
            >>> # Get last hour of aggregate trades
            >>> end = int(time.time() * 1000)
            >>> start = end - (60 * 60 * 1000)
            >>> agg_trades = oracle.aggregate_trades("BTCUSDT", start_time=start, end_time=end)
        """
        validate(Oracle.is_valid_symbol(symbol), "Invalid symbol")
        validate(limit <= 1000, "Trades limit can be maximum 1000")

        payload = {"symbol": symbol, "limit": limit}

        if from_id:
            payload["fromId"] = from_id
        if start_time:
            payload["startTime"] = start_time
        if end_time:
            payload["endTime"] = end_time

        data = self.request("aggTrades", payload)

        df = pandas.DataFrame(data)

        df = df.rename(
            columns={
                "a": "agg_trade_id",
                "p": "price",
                "q": "quantity",
                "f": "first_trade_id",
                "l": "last_trade_id",
                "T": "timestamp_ms",
                "m": "is_buyer_maker",
                "M": "best_price_match",
            }
        )

        df["price"] = df["price"].astype(float)
        df["quantity"] = df["quantity"].astype(float)

        return df

    def klines(
        self,
        symbol: str,
        interval: str,
        start_time: int = 0,
        end_time: int = 0,
        timezone: str = "0",
        limit: int = 500,
    ) -> pandas.DataFrame:
        """
        Get candlestick/kline data (OHLCV).

        Retrieves historical price data in candlestick format. Essential for
        technical analysis and backtesting strategies.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            interval (str): Candlestick interval. Valid values:
                1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
            start_time (int, optional): Start timestamp in milliseconds
            end_time (int, optional): End timestamp in milliseconds
            timezone (str, optional): Timezone offset (e.g., "0", "8", "-5:30").
                Defaults to "0" (UTC).
            limit (int, optional): Number of candlesticks (max 1000). Defaults to 500.

        Returns:
            pandas.DataFrame: Candlestick data with columns:
                - open_time (int): Open timestamp in milliseconds
                - open (float): Opening price
                - high (float): Highest price
                - low (float): Lowest price
                - close (float): Closing price
                - volume (float): Base asset volume
                - close_time (int): Close timestamp in milliseconds
                - quote_asset_volume (float): Quote asset volume
                - num_trades (int): Number of trades
                - taker_buy_base_volume (float): Taker buy base asset volume
                - taker_buy_quote_volume (float): Taker buy quote asset volume

        Raises:
            LiminalError: If symbol/interval/timezone invalid or limit exceeds 1000

        Example:
            >>> # Get 1-hour candlesticks
            >>> klines = oracle.klines("BTCUSDT", interval="1h", limit=168)  # 1 week
            >>>
            >>> # Calculate simple moving average
            >>> klines['sma_20'] = klines['close'].rolling(20).mean()
            >>>
            >>> # Get data with timezone
            >>> klines = oracle.klines("BTCUSDT", interval="1d", timezone="8")  # UTC+8
        """
        validate(Oracle.is_valid_symbol(symbol), "Invalid symbol")
        validate(Oracle.is_valid_interval(interval), "Invalid interval")
        validate(Oracle.is_valid_timezone(timezone), "Invalid timezone")

        validate(limit <= 1000, "Trades limit can be maximum 1000")

        payload = {
            "symbol": symbol,
            "limit": limit,
            "interval": interval,
            "timeZone": timezone,
        }

        if start_time:
            payload["startTime"] = start_time
        if end_time:
            payload["endTime"] = end_time

        data = self.request("klines", payload)

        columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "num_trades",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
            "ignore",
        ]

        numeric_cols = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_asset_volume",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
        ]

        df = pandas.DataFrame(data, columns=columns)
        df[numeric_cols] = df[numeric_cols].astype(float)

        df["num_trades"] = df["num_trades"].astype(int)
        df["open_time"] = df["open_time"].astype(int)
        df["close_time"] = df["close_time"].astype(int)

        df = df.drop(columns=["ignore"])
        return df

    def average_price(self, symbol: str) -> dict:
        """
        Get current average price for a symbol.

        Returns the average price calculated over a recent time window.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")

        Returns:
            dict: Average price data with keys:
                - mins: Time window in minutes
                - price: Average price as string

        Raises:
            LiminalError: If symbol is invalid

        Example:
            >>> avg = oracle.average_price("BTCUSDT")
            >>> print(f"5-min avg: {avg['price']}")
        """
        validate(Oracle.is_valid_symbol(symbol), "Invalid symbol")

        payload = {"symbol": symbol}

        data = self.request("avgPrice", payload)
        return data

    def twenty_four_stats(
        self, symbol: str | list[str], type: str = "FULL"
    ) -> dict | list:
        """
        Get 24-hour rolling window price change statistics.

        Provides comprehensive statistics including price change, volume, high/low,
        and other metrics over the last 24 hours.

        Args:
            symbol (str | list[str]): Single symbol or list of symbols
            type (str, optional): Statistics type - "FULL" or "MINI".
                FULL includes all fields, MINI includes subset. Defaults to "FULL".

        Returns:
            dict | list: Statistics dict for single symbol, or list of dicts for multiple.
                FULL type includes: symbol, priceChange, priceChangePercent,
                weightedAvgPrice, openPrice, highPrice, lowPrice, lastPrice,
                volume, quoteVolume, openTime, closeTime, firstId, lastId, count

                MINI type includes: symbol, openPrice, highPrice, lowPrice,
                lastPrice, volume, quoteVolume, openTime, closeTime, firstId,
                lastId, count

        Raises:
            LiminalError: If symbol invalid, empty list, or type not FULL/MINI

        Example:
            >>> # Single symbol
            >>> stats = oracle.twenty_four_stats("BTCUSDT")
            >>> print(f"24h change: {stats['priceChangePercent']}%")
            >>>
            >>> # Multiple symbols (MINI for efficiency)
            >>> stats = oracle.twenty_four_stats(["BTCUSDT", "ETHUSDT"], type="MINI")
        """
        validate(type == "FULL" or type == "MINI", "Invalid type")

        payload = {}

        if isinstance(symbol, list):
            validate(len(symbol) > 0, "No params provided")
            [validate(Oracle.is_valid_symbol(s), "Invalid symbol") for s in symbol]
            payload["symbols"] = self.sequence(symbol)

        else:
            validate(Oracle.is_valid_symbol(symbol), "Invalid symbol")
            payload["symbol"] = symbol

        payload.update({"type": type})

        data = self.request("ticker/24hr", payload)
        return data

    def price(self, symbol: str | list[str]) -> dict | list:
        """
        Get latest price for symbol(s).

        Simple, fast method to retrieve current trading prices.

        Args:
            symbol (str | list[str]): Single symbol or list of symbols

        Returns:
            dict | list: Price dict for single symbol, or list of dicts for multiple.
                Each dict contains:
                - symbol: Trading pair symbol
                - price: Current price as string

        Raises:
            LiminalError: If symbol is invalid or empty list provided

        Example:
            >>> # Single symbol
            >>> price_data = oracle.price("BTCUSDT")
            >>> print(f"BTC: ${price_data['price']}")
            >>>
            >>> # Multiple symbols
            >>> prices = oracle.price(["BTCUSDT", "ETHUSDT", "BNBUSDT"])
            >>> for p in prices:
            ...     print(f"{p['symbol']}: ${p['price']}")
        """
        payload = {}

        if isinstance(symbol, list):
            validate(len(symbol) > 0, "No params provided")
            [validate(Oracle.is_valid_symbol(s), "Invalid symbol") for s in symbol]
            payload["symbols"] = self.sequence(symbol)

        else:
            validate(Oracle.is_valid_symbol(symbol), "Invalid symbol")
            payload["symbol"] = symbol

        data = self.request("ticker/price", payload)
        return data

    @staticmethod
    def available_endpoints() -> list[str]:
        """
        Get list of available Binance API endpoints.

        Returns different regional endpoints that can be used for load balancing
        or reduced latency.

        Returns:
            list[str]: List of available Binance API endpoint URLs

        Example:
            >>> endpoints = Oracle.available_endpoints()
            >>> for endpoint in endpoints:
            ...     oracle = Oracle(endpoint=endpoint)
            ...     if oracle.status():
            ...         print(f"{endpoint} is online")
        """
        return [
            "https://api.binance.com",
            "https://api-gcp.binance.com",
            "https://api1.binance.com",
            "https://api2.binance.com",
            "https://api3.binance.com",
            "https://api4.binance.com",
        ]

    @staticmethod
    def is_valid_symbol(symbol: str) -> bool:
        """
        Validate if symbol format is correct.

        Symbols must be 1-20 characters, uppercase alphanumeric with optional
        hyphens, underscores, or periods.

        Args:
            symbol (str): Symbol to validate

        Returns:
            bool: True if valid, False otherwise

        Example:
            >>> Oracle.is_valid_symbol("BTCUSDT")  # True
            >>> Oracle.is_valid_symbol("BTC-USDT")  # True
            >>> Oracle.is_valid_symbol("btcusdt")  # False (lowercase)
            >>> Oracle.is_valid_symbol("BTC USDT")  # False (space)
        """
        return bool(re.match(r"^[A-Z0-9-_.]{1,20}$", symbol))

    @staticmethod
    def is_valid_interval(interval: str) -> bool:
        """
        Validate if candlestick interval is supported.

        Args:
            interval (str): Interval to validate

        Returns:
            bool: True if valid, False otherwise

        Valid intervals:
            Minutes: 1m, 3m, 5m, 15m, 30m
            Hours: 1h, 2h, 4h, 6h, 8h, 12h
            Days: 1d, 3d
            Week: 1w
            Month: 1M

        Example:
            >>> Oracle.is_valid_interval("1h")   # True
            >>> Oracle.is_valid_interval("5m")   # True
            >>> Oracle.is_valid_interval("2m")   # False (not supported)
        """
        intervals = {
            "1m",
            "3m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "6h",
            "8h",
            "12h",
            "1d",
            "3d",
            "1w",
            "1M",
        }

        return interval in intervals

    @staticmethod
    def is_valid_timezone(tz: str) -> bool:
        """
        Validate timezone offset format.

        Supports both hour-only and hour:minute formats with optional +/- prefix.
        Valid range: -12 to +14 hours (standard UTC offsets).

        Args:
            tz (str): Timezone to validate

        Returns:
            bool: True if valid, False otherwise

        Valid formats:
            - "0", "5", "-5" (hour only)
            - "5:30", "-5:30", "+5:30" (hour:minute)

        Restrictions:
            - Hours: -12 to +14
            - Minutes: 00 to 59
            - UTC+14:00 and UTC-12:00 cannot have non-zero minutes

        Example:
            >>> Oracle.is_valid_timezone("0")      # True (UTC)
            >>> Oracle.is_valid_timezone("5:30")   # True (IST)
            >>> Oracle.is_valid_timezone("-8")     # True (PST)
            >>> Oracle.is_valid_timezone("15")     # False (out of range)
            >>> Oracle.is_valid_timezone("14:30")  # False (14 can't have minutes)
        """
        if re.fullmatch(r"-?\d{1,2}", tz):
            hours = int(tz)
            return -12 <= hours <= 14

        match = re.fullmatch(r"([+-]?\d{1,2}):([0-5]\d)", tz)
        if match:
            hours, minutes = int(match[1]), int(match[2])
            if -12 <= hours <= 14:
                if (hours == 14 and minutes != 0) or (hours == -12 and minutes != 0):
                    return False

                return True

        return False
