"""A set of utility functions for time handling in logging."""

from datetime import datetime
from typing import TYPE_CHECKING

from bear_epoch_time import DATE_FORMAT, DT_FORMAT_WITH_SECONDS, PT_TIME_ZONE, TIME_FORMAT_WITH_SECONDS, EpochTimestamp
from bear_epoch_time.tz import TimeZoneType, get_local_timezone

if TYPE_CHECKING:
    from zoneinfo import ZoneInfo


class TimeHelper:
    """A helper class for managing time-related operations in logging."""

    def __init__(
        self,
        fullfmt: str = DT_FORMAT_WITH_SECONDS,
        datefmt: str = DATE_FORMAT,
        timefmt: str = TIME_FORMAT_WITH_SECONDS,
        tz: TimeZoneType | None = None,
    ) -> None:
        """Initialize the TimeHelper with default formats and timezone."""
        self.fullfmt: str = fullfmt
        self.datefmt: str = datefmt
        self.timefmt: str = timefmt
        self.tz: ZoneInfo = get_local_timezone()
        self.tz_pref: TimeZoneType = tz or self.tz or PT_TIME_ZONE

    @property
    def now(self) -> EpochTimestamp:
        """Get the current time as an EpochTimestamp object."""
        return EpochTimestamp.now()

    def date(self, timestamp: EpochTimestamp | None = None) -> str:
        """Get the current date as a formatted string."""
        if timestamp is None:
            timestamp = self.now
        return timestamp.date_str(fmt=self.datefmt, tz=self.tz_pref)

    def time(self, timestamp: EpochTimestamp | None = None) -> str:
        """Get the current time as a formatted string."""
        if timestamp is None:
            timestamp = self.now
        return timestamp.time_str(fmt=self.timefmt, tz=self.tz_pref)

    def timestamp(self, timestamp: EpochTimestamp | None = None) -> str:
        """Get the full timestamp as a formatted string."""
        if timestamp is None:
            timestamp = self.now
        return timestamp.to_string(fmt=self.fullfmt, tz=self.tz_pref)

    def get_all(self, timestamp: EpochTimestamp | None = None) -> tuple[str, str, str]:
        """Get the current timestamp, date, and time as formatted strings.

        Args:
            timestamp: The EpochTimestamp to format. If None, uses the current time.

        Returns:
            A tuple of formatted timestamp strings (timestamp, date, time).
        """
        if timestamp is None:
            timestamp = self.now
        return (
            timestamp.to_string(fmt=self.fullfmt, tz=self.tz_pref),
            timestamp.to_string(fmt=self.datefmt, tz=self.tz_pref),
            timestamp.to_string(fmt=self.timefmt, tz=self.tz_pref),
        )

    def get_time(self, fmt: str = TIME_FORMAT_WITH_SECONDS, tz: TimeZoneType = PT_TIME_ZONE) -> str:
        """Get the current time as a formatted string.

        Args:
            fmt: The format string to use for the time.
            tz: The timezone to use for formatting.

        Returns:
            The formatted time string.
        """
        tz = tz or self.tz
        return self.now.to_string(fmt=fmt, tz=tz)

    def get_date(self, fmt: str = DATE_FORMAT, tz: TimeZoneType = PT_TIME_ZONE) -> str:
        """Get the current date as a formatted string.

        Args:
            fmt: The format string to use for the date.
            tz: The timezone to use for formatting.

        Returns:
            The formatted date string.
        """
        tz = tz or self.tz
        return self.now.to_string(fmt=fmt, tz=tz)

    def get_timestamp(self, fmt: str = DT_FORMAT_WITH_SECONDS, tz: TimeZoneType = PT_TIME_ZONE) -> str:
        """Get the current full timestamp as a formatted string.

        Args:
            fmt: The format string to use for the timestamp.
            tz: The timezone to use for formatting.

        Returns:
            The formatted timestamp string.
        """
        fmt = fmt or self.fullfmt
        tz = tz or self.tz
        return self.now.to_string(fmt=fmt, tz=tz)

    def get_datetime(self) -> datetime:
        """Get the current datetime with local timezone if available."""
        dt: datetime = self.now.to_datetime
        return dt.astimezone(self.tz) if self.tz else dt
