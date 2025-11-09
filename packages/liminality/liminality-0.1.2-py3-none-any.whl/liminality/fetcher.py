"""
Fetcher Module - Smart Data Retrieval with Auto-Pagination
===========================================================

This module provides intelligent, high-performance data fetching capabilities
with automatic pagination, rate limiting, and progress tracking. Designed for
seamless bulk data retrieval without hitting API limits.

Features:
    - Automatic pagination for large historical datasets
    - Smart rate limiting with exponential backoff
    - Progress bars for long-running operations
    - Parallel fetching for multiple symbols
    - Data validation and gap detection
    - Memory-efficient chunked processing
    - Automatic retry on transient failures
    - Clean pandas DataFrame output

Example Usage:
    >>> from liminal import Fetcher
    >>> from datetime import datetime
    >>>
    >>> fetcher = Fetcher()
    >>>
    >>> # Fetch months of data automatically
    >>> df = fetcher.fetch_klines(
    ...     "BTCUSDT",
    ...     interval="1h",
    ...     start="2024-01-01",
    ...     end="2024-06-30"
    ... )
    >>>
    >>> # Fetch multiple symbols in parallel
    >>> data = fetcher.fetch_multi_klines(
    ...     ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
    ...     interval="1d",
    ...     start="2024-01-01"
    ... )

Author: Athen Traverne
License: MIT
"""

import time
import typing
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import pandas
from tqdm import tqdm

from .exceptions import LiminalError, validate
from .oracle import Oracle


class Fetcher:
    """
    Smart data fetcher with auto-pagination and rate limiting.

    Wraps Oracle with intelligent fetching capabilities for large datasets.
    Handles pagination, rate limits, and retries automatically.

    Attributes:
        oracle (Oracle): Underlying Oracle instance for API calls
        rate_limit_delay (float): Delay between requests in seconds
        max_retries (int): Maximum retry attempts for failed requests
        retry_delay (int): Initial delay for exponential backoff
        show_progress (bool): Whether to show progress bars
        parallel_workers (int): Number of parallel workers for multi-symbol fetching

    Example:
        >>> fetcher = Fetcher()
        >>> fetcher = Fetcher(rate_limit_delay=0.5, max_retries=5)
    """

    oracle: Oracle
    rate_limit_delay: float = 0.2  # 200ms between requests
    max_retries: int = 3
    retry_delay: int = 1
    show_progress: bool = True
    parallel_workers: int = 4

    # Binance rate limits
    MAX_KLINES_PER_REQUEST: int = 1000
    MAX_TRADES_PER_REQUEST: int = 1000

    def __init__(
        self,
        oracle: Oracle | None = None,
        rate_limit_delay: float = 0.2,
        max_retries: int = 3,
        show_progress: bool = True,
        parallel_workers: int = 4,
    ) -> None:
        """
        Initialize Fetcher with optional custom Oracle.

        Args:
            oracle (Oracle, optional): Custom Oracle instance. Creates new if not provided.
            rate_limit_delay (float, optional): Delay between requests. Defaults to 0.2s.
            max_retries (int, optional): Max retry attempts. Defaults to 3.
            show_progress (bool, optional): Show progress bars. Defaults to True.
            parallel_workers (int, optional): Parallel workers for multi-symbol. Defaults to 4.

        Example:
            >>> oracle = Oracle(endpoint="https://api1.binance.com")
            >>> fetcher = Fetcher(oracle=oracle, rate_limit_delay=0.5)
        """
        self.oracle = oracle if oracle else Oracle()
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.show_progress = show_progress
        self.parallel_workers = parallel_workers

    def _parse_time(self, time_str: str | int | datetime) -> int:
        """
        Parse time string/datetime to Unix timestamp in milliseconds.

        Args:
            time_str (str | int | datetime): Time in various formats:
                - ISO string: "2024-01-01", "2024-01-01 12:00:00"
                - Unix timestamp (ms): 1704067200000
                - datetime object

        Returns:
            int: Unix timestamp in milliseconds

        Example:
            >>> self._parse_time("2024-01-01")
            1704067200000
            >>> self._parse_time(datetime(2024, 1, 1))
            1704067200000
        """
        if isinstance(time_str, int):
            return time_str

        if isinstance(time_str, datetime):
            return int(time_str.timestamp() * 1000)

        # Parse string
        try:
            # Try ISO format first
            if "T" in time_str or " " in time_str:
                dt = datetime.fromisoformat(time_str.replace("T", " "))
            else:
                dt = datetime.strptime(time_str, "%Y-%m-%d")

            return int(dt.timestamp() * 1000)
        except ValueError as e:
            raise LiminalError(
                f"Invalid time format: {time_str}. Use ISO format (YYYY-MM-DD) or datetime object"
            ) from e

    def _interval_to_ms(self, interval: str) -> int:
        """
        Convert interval string to milliseconds.

        Args:
            interval (str): Interval (1m, 1h, 1d, etc.)

        Returns:
            int: Interval duration in milliseconds

        Example:
            >>> self._interval_to_ms("1m")
            60000
            >>> self._interval_to_ms("1h")
            3600000
        """
        units = {
            "m": 60 * 1000,
            "h": 60 * 60 * 1000,
            "d": 24 * 60 * 60 * 1000,
            "w": 7 * 24 * 60 * 60 * 1000,
            "M": 30 * 24 * 60 * 60 * 1000,  # Approximate
        }

        # Extract number and unit
        num = int(interval[:-1])
        unit = interval[-1]

        if unit not in units:
            raise LiminalError(f"Invalid interval unit: {unit}")

        return num * units[unit]

    def _retry_request(self, func: typing.Callable, *args, **kwargs) -> typing.Any:
        """
        Execute request with exponential backoff retry logic.

        Args:
            func (callable): Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Any: Function return value

        Raises:
            LiminalError: If all retry attempts fail
        """
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                return result
            except LiminalError as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)  # Exponential backoff
                    if self.show_progress:
                        tqdm.write(
                            f"[Fetcher] Request failed, retrying in {delay}s... ({attempt + 1}/{self.max_retries})"
                        )
                    time.sleep(delay)
                else:
                    raise LiminalError(
                        f"Failed after {self.max_retries} attempts: {e}"
                    ) from e

    def fetch_klines(
        self,
        symbol: str,
        interval: str,
        start: str | int | datetime | None = None,
        end: str | int | datetime | None = None,
        limit: int | None = None,
    ) -> pandas.DataFrame:
        """
        Fetch klines with automatic pagination for large date ranges.

        Automatically handles pagination when requesting data beyond the 1000
        candle limit. Shows progress bar for long operations.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            interval (str): Kline interval (1m, 5m, 1h, 1d, etc.)
            start (str | int | datetime, optional): Start time. If not provided,
                fetches most recent candles.
            end (str | int | datetime, optional): End time. Defaults to now.
            limit (int, optional): Maximum number of candles. If not provided,
                fetches all data between start and end.

        Returns:
            pandas.DataFrame: Klines with columns: open_time, open, high, low,
                close, volume, close_time, quote_asset_volume, num_trades,
                taker_buy_base_volume, taker_buy_quote_volume

        Raises:
            LiminalError: If symbol/interval invalid or request fails

        Example:
            >>> # Fetch 6 months of hourly data (automatically paginated)
            >>> df = fetcher.fetch_klines(
            ...     "BTCUSDT",
            ...     interval="1h",
            ...     start="2024-01-01",
            ...     end="2024-06-30"
            ... )
            >>>
            >>> # Fetch last 500 candles
            >>> df = fetcher.fetch_klines("BTCUSDT", interval="1m", limit=500)
            >>>
            >>> # Fetch from specific date to now
            >>> df = fetcher.fetch_klines("BTCUSDT", interval="1d", start="2024-01-01")
        """
        validate(Oracle.is_valid_symbol(symbol), "Invalid symbol")
        validate(Oracle.is_valid_interval(interval), "Invalid interval")

        # If limit specified without start/end, just fetch directly
        if limit and not start and not end:
            return self._retry_request(
                self.oracle.klines,
                symbol=symbol,
                interval=interval,
                limit=min(limit, self.MAX_KLINES_PER_REQUEST),
            )

        # Parse times
        start_ms = self._parse_time(start) if start else None
        end_ms = self._parse_time(end) if end else int(time.time() * 1000)

        # Calculate number of requests needed
        if start_ms:
            interval_ms = self._interval_to_ms(interval)
            total_candles = (end_ms - start_ms) // interval_ms

            if limit:
                total_candles = min(total_candles, limit)

            num_requests = (total_candles // self.MAX_KLINES_PER_REQUEST) + 1
        else:
            num_requests = 1

        # Fetch data in chunks
        all_data = []
        current_start = start_ms

        progress_bar = None
        if self.show_progress and num_requests > 1:
            progress_bar = tqdm(
                total=num_requests, desc=f"Fetching {symbol} {interval}", unit="req"
            )

        try:
            while True:
                # Fetch chunk
                chunk = self._retry_request(
                    self.oracle.klines,
                    symbol=symbol,
                    interval=interval,
                    start_time=current_start if current_start else 0,
                    end_time=end_ms,
                    limit=self.MAX_KLINES_PER_REQUEST,
                )

                if chunk.empty:
                    break

                all_data.append(chunk)

                if progress_bar:
                    progress_bar.update(1)

                # Check if we have all data
                if limit and sum(len(df) for df in all_data) >= limit:
                    break

                # Check if we reached the end
                if len(chunk) < self.MAX_KLINES_PER_REQUEST:
                    break

                # Update start time for next request
                current_start = int(chunk["close_time"].iloc[-1]) + 1

                # Rate limiting
                time.sleep(self.rate_limit_delay)

        finally:
            if progress_bar:
                progress_bar.close()

        # Combine all chunks
        if not all_data:
            return pandas.DataFrame()

        df = pandas.concat(all_data, ignore_index=True)

        # Remove duplicates (can happen at boundaries)
        df = df.drop_duplicates(subset=["open_time"], keep="first")

        # Apply limit if specified
        if limit:
            df = df.head(limit)

        # Sort by time
        df = df.sort_values("open_time").reset_index(drop=True)

        return df

    def fetch_trades(
        self,
        symbol: str,
        start_time: str | int | datetime | None = None,
        end_time: str | int | datetime | None = None,
        limit: int | None = None,
    ) -> pandas.DataFrame:
        """
        Fetch trades with automatic pagination.

        Retrieves trade history with automatic pagination for large datasets.

        Args:
            symbol (str): Trading pair symbol (e.g., "BTCUSDT")
            start_time (str | int | datetime, optional): Start time
            end_time (str | int | datetime, optional): End time
            limit (int, optional): Maximum number of trades

        Returns:
            pandas.DataFrame: Trades with columns: id, price, qty, quoteQty,
                time, isBuyerMaker, isBestMatch

        Example:
            >>> # Fetch last hour of trades
            >>> trades = fetcher.fetch_trades(
            ...     "BTCUSDT",
            ...     start_time="2024-06-01 12:00:00",
            ...     end_time="2024-06-01 13:00:00"
            ... )
        """
        validate(Oracle.is_valid_symbol(symbol), "Invalid symbol")

        # Simple case: no pagination needed
        if limit and limit <= self.MAX_TRADES_PER_REQUEST and not start_time:
            return self._retry_request(self.oracle.trades, symbol=symbol, limit=limit)

        # For historical trades with time range, use aggregate trades
        if start_time or end_time:
            start_ms = self._parse_time(start_time) if start_time else 0
            end_ms = self._parse_time(end_time) if end_time else int(time.time() * 1000)

            all_data = []

            progress_bar = None
            if self.show_progress:
                progress_bar = tqdm(desc=f"Fetching {symbol} trades", unit="req")

            try:
                while True:
                    chunk = self._retry_request(
                        self.oracle.aggregate_trades,
                        symbol=symbol,
                        start_time=start_ms,
                        end_time=end_ms,
                        limit=self.MAX_TRADES_PER_REQUEST,
                    )

                    if chunk.empty:
                        break

                    all_data.append(chunk)

                    if progress_bar:
                        progress_bar.update(1)

                    if limit and sum(len(df) for df in all_data) >= limit:
                        break

                    if len(chunk) < self.MAX_TRADES_PER_REQUEST:
                        break

                    # Update start time
                    start_ms = int(chunk["timestamp_ms"].iloc[-1]) + 1

                    time.sleep(self.rate_limit_delay)

            finally:
                if progress_bar:
                    progress_bar.close()

            if not all_data:
                return pandas.DataFrame()

            df = pandas.concat(all_data, ignore_index=True)

            if limit:
                df = df.head(limit)

            return df

        # Just fetch recent trades
        return self._retry_request(
            self.oracle.trades, symbol=symbol, limit=limit if limit else 500
        )

    def fetch_multi_klines(
        self,
        symbols: list[str],
        interval: str,
        start: str | int | datetime | None = None,
        end: str | int | datetime | None = None,
        limit: int | None = None,
    ) -> dict[str, pandas.DataFrame]:
        """
        Fetch klines for multiple symbols in parallel.

        Uses thread pool for concurrent fetching, significantly faster than
        sequential requests.

        Args:
            symbols (list[str]): List of trading pair symbols
            interval (str): Kline interval
            start (str | int | datetime, optional): Start time
            end (str | int | datetime, optional): End time
            limit (int, optional): Maximum candles per symbol

        Returns:
            dict[str, pandas.DataFrame]: Dictionary mapping symbols to their klines

        Example:
            >>> # Fetch data for multiple symbols
            >>> data = fetcher.fetch_multi_klines(
            ...     ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
            ...     interval="1h",
            ...     start="2024-01-01",
            ...     limit=1000
            ... )
            >>>
            >>> btc_df = data["BTCUSDT"]
            >>> eth_df = data["ETHUSDT"]
        """
        validate(len(symbols) > 0, "No symbols provided")

        results = {}

        progress_bar = None
        if self.show_progress:
            progress_bar = tqdm(
                total=len(symbols), desc="Fetching multiple symbols", unit="symbol"
            )

        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(
                    self.fetch_klines,
                    symbol=symbol,
                    interval=interval,
                    start=start,
                    end=end,
                    limit=limit,
                ): symbol
                for symbol in symbols
            }

            # Collect results as they complete
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    results[symbol] = future.result()
                    if progress_bar:
                        progress_bar.update(1)
                except Exception as e:
                    if self.show_progress:
                        tqdm.write(f"[Fetcher] Failed to fetch {symbol}: {e}")
                    results[symbol] = pandas.DataFrame()

        if progress_bar:
            progress_bar.close()

        return results

    def detect_gaps(self, df: pandas.DataFrame, interval: str) -> list[tuple[int, int]]:
        """
        Detect missing candles (gaps) in kline data.

        Identifies time gaps where data is missing based on expected interval.

        Args:
            df (pandas.DataFrame): Klines DataFrame
            interval (str): Expected interval

        Returns:
            list[tuple[int, int]]: List of (start_time, end_time) gaps in milliseconds

        Example:
            >>> df = fetcher.fetch_klines("BTCUSDT", "1h", start="2024-01-01", limit=1000)
            >>> gaps = fetcher.detect_gaps(df, "1h")
            >>> if gaps:
            ...     print(f"Found {len(gaps)} gaps in data")
        """
        if df.empty:
            return []

        interval_ms = self._interval_to_ms(interval)
        gaps = []

        for i in range(len(df) - 1):
            current_time = df["close_time"].iloc[i]
            next_time = df["open_time"].iloc[i + 1]

            expected_next = current_time + 1

            if next_time - expected_next > interval_ms:
                gaps.append((current_time + 1, next_time - 1))

        return gaps

    def fill_gaps(
        self, symbol: str, df: pandas.DataFrame, interval: str
    ) -> pandas.DataFrame:
        """
        Fill detected gaps in kline data by fetching missing candles.

        Args:
            symbol (str): Trading pair symbol
            df (pandas.DataFrame): Existing klines DataFrame with gaps
            interval (str): Kline interval

        Returns:
            pandas.DataFrame: Complete DataFrame with gaps filled

        Example:
            >>> df = fetcher.fetch_klines("BTCUSDT", "1h", start="2024-01-01")
            >>> gaps = fetcher.detect_gaps(df, "1h")
            >>> if gaps:
            ...     df = fetcher.fill_gaps("BTCUSDT", df, "1h")
        """
        gaps = self.detect_gaps(df, interval)

        if not gaps:
            return df

        if self.show_progress:
            print(f"[Fetcher] Filling {len(gaps)} gaps...")

        all_data = [df]

        for start_ms, end_ms in gaps:
            gap_data = self.fetch_klines(
                symbol=symbol, interval=interval, start=start_ms, end=end_ms
            )

            if not gap_data.empty:
                all_data.append(gap_data)

        # Combine and deduplicate
        df_complete = pandas.concat(all_data, ignore_index=True)
        df_complete = df_complete.drop_duplicates(subset=["open_time"], keep="first")
        df_complete = df_complete.sort_values("open_time").reset_index(drop=True)

        return df_complete

    def get_available_date_range(
        self, symbol: str, interval: str
    ) -> tuple[datetime, datetime]:
        """
        Get the available date range for a symbol.

        Fetches earliest and latest available candles to determine data availability.

        Args:
            symbol (str): Trading pair symbol
            interval (str): Kline interval

        Returns:
            tuple[datetime, datetime]: (earliest_date, latest_date)

        Example:
            >>> start, end = fetcher.get_available_date_range("BTCUSDT", "1h")
            >>> print(f"Data available from {start} to {end}")
        """
        # Get earliest candle
        earliest = self._retry_request(
            self.oracle.klines, symbol=symbol, interval=interval, limit=1
        )

        # Get latest candle
        latest = self._retry_request(
            self.oracle.klines, symbol=symbol, interval=interval, limit=1
        )

        if earliest.empty or latest.empty:
            raise LiminalError(f"No data available for {symbol}")

        earliest_dt = datetime.fromtimestamp(earliest["open_time"].iloc[0] / 1000)
        latest_dt = datetime.fromtimestamp(latest["close_time"].iloc[-1] / 1000)

        return earliest_dt, latest_dt
