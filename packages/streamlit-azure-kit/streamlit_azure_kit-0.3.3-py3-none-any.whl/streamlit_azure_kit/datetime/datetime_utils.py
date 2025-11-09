"""
DateTime column expansion utilities.

Converts text-based UTC datetime columns into multiple format-specific columns
with unambiguous naming for reliable date/time operations.
"""

import logging
import pandas as pd
import pytz

logger = logging.getLogger(__name__)


def expand_datetime_column(
    df,
    column_name,
    source_is_text=False,
    round_to_second=True,
    errors='raise'
):
    """
    Expand a datetime column into 6 unambiguous format-specific columns.

    Transforms a single datetime column (text or datetime type) into multiple
    columns with format-explicit names that clearly indicate the data type and
    timezone. This eliminates confusion in date/time operations and reduces errors.

    Creates 6 columns:
    ------------------
    - {prefix}_pandas_datetime_utc  → pandas Timestamp (UTC) for vectorized operations
    - {prefix}_pandas_datetime_ny   → pandas Timestamp (NY) for vectorized operations
    - {prefix}_python_date_ny       → Python date object for date comparisons
    - {prefix}_python_time_ny       → Python time object for time comparisons
    - {prefix}_int_hour_ny          → Integer (0-23) for simple hour checks
    - {prefix}_iso_string_ny        → ISO format string for display/logging

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the datetime column to expand.
    column_name : str
        Name of the datetime column to expand. Can be text (VARCHAR) or datetime type.
    source_is_text : bool, default False
        If True, treats the column as text containing ISO format UTC datetime strings.
        If False, treats the column as a datetime64[ns] type.
    round_to_second : bool, default True
        If True, rounds datetime to nearest second, removing microsecond precision.
        Recommended to avoid microsecond comparison issues.
    errors : {'raise', 'coerce', 'ignore'}, default 'raise'
        How to handle datetime parsing errors:
        - 'raise': Raise exception on invalid datetime values
        - 'coerce': Convert invalid values to NaT (Not a Time)
        - 'ignore': Return original data if parsing fails

    Returns
    -------
    pd.DataFrame
        DataFrame with 6 new columns added. Original column is preserved.

    Examples
    --------
    Expand a text column from database:

    >>> df = pd.read_sql("SELECT * FROM orders", conn)
    >>> df = expand_datetime_column(df, 'created_at', source_is_text=True)
    >>> # Now has: created_pandas_datetime_utc, created_pandas_datetime_ny, etc.

    Use in method chaining:

    >>> df = (pd.read_sql("SELECT * FROM events", conn)
    ...       .pipe(expand_datetime_column, 'created_at', source_is_text=True))

    Usage examples with expanded columns:

    >>> # Date comparison
    >>> recent = df[df['created_python_date_ny'] > date(2025, 10, 1)]
    >>>
    >>> # Hour check
    >>> morning = df[df['created_int_hour_ny'] < 12]
    >>>
    >>> # Vectorized operations
    >>> next_week = df['created_pandas_datetime_ny'] + pd.Timedelta(days=7)
    >>>
    >>> # Display
    >>> print(f"Last update: {df['created_iso_string_ny'].iloc[0]}")

    Notes
    -----
    - Original column is preserved as-is (text columns remain text)
    - All operations use America/New_York timezone for local times
    - Microseconds are removed by default to avoid comparison issues
    - Column prefix is derived by removing '_at', '_utc', '_datetime_utc' suffixes
    - Works seamlessly with pandas method chaining (.pipe())
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")

    # Get prefix (remove common suffixes)
    prefix = column_name
    for suffix in ['_datetime_utc', '_utc', '_at']:
        if prefix.endswith(suffix):
            prefix = prefix.replace(suffix, '')
            break

    logger.debug(f"Expanding datetime column '{column_name}' with prefix '{prefix}'")

    # Parse datetime column into temporary series (don't mutate original)
    if source_is_text:
        logger.debug(f"Parsing text column '{column_name}' as UTC datetime")
        parsed_series = pd.to_datetime(df[column_name], utc=True, errors=errors)
    else:
        logger.debug(f"Converting column '{column_name}' to datetime")
        parsed_series = pd.to_datetime(df[column_name], errors=errors)

    # Round to second if requested (removes microseconds)
    if round_to_second:
        logger.debug(f"Rounding datetime to nearest second")
        parsed_series = parsed_series.dt.round('s')

    # Create timezone objects
    tz_utc = pytz.UTC
    tz_ny = pytz.timezone('America/New_York')

    # Column 1: UTC pandas datetime
    if parsed_series.dt.tz is None:
        # Naive datetime - assume UTC
        logger.debug(f"Localizing naive datetime to UTC")
        df[f'{prefix}_pandas_datetime_utc'] = parsed_series.dt.tz_localize(tz_utc)
    else:
        # Already has timezone - convert to UTC
        logger.debug(f"Converting timezone-aware datetime to UTC")
        df[f'{prefix}_pandas_datetime_utc'] = parsed_series.dt.tz_convert(tz_utc)

    # Column 2: NY pandas datetime (for vectorized operations)
    logger.debug(f"Creating NY timezone column")
    df[f'{prefix}_pandas_datetime_ny'] = df[f'{prefix}_pandas_datetime_utc'].dt.tz_convert(tz_ny)

    # Column 3: Python date object (for comparisons with date literals)
    logger.debug(f"Extracting date component")
    df[f'{prefix}_python_date_ny'] = df[f'{prefix}_pandas_datetime_ny'].dt.date

    # Column 4: Python time object (for time comparisons)
    logger.debug(f"Extracting time component")
    df[f'{prefix}_python_time_ny'] = df[f'{prefix}_pandas_datetime_ny'].dt.time

    # Column 5: Integer hour (for simple hour checks)
    logger.debug(f"Extracting hour component")
    df[f'{prefix}_int_hour_ny'] = df[f'{prefix}_pandas_datetime_ny'].dt.hour

    # Column 6: ISO string for display (NEW)
    logger.debug(f"Creating ISO string representation")
    df[f'{prefix}_iso_string_ny'] = df[f'{prefix}_pandas_datetime_ny'].dt.strftime('%Y-%m-%d %H:%M:%S')

    logger.info(f"Successfully expanded '{column_name}' into 6 format-specific columns")

    return df


def expand_all_datetime_columns(
    df,
    datetime_columns=None,
    source_is_text=False,
    round_to_second=True,
    errors='raise',
    drop_originals=False
):
    """
    Expand multiple datetime columns at once.

    Convenience function to expand multiple datetime columns in a single call.
    Can auto-detect datetime columns by common suffixes, or accept an explicit list.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing datetime columns to expand.
    datetime_columns : list of str, optional
        List of column names to expand. If None, auto-detects columns ending
        in '_at', '_datetime_utc', '_utc', or '_datetime'.
    source_is_text : bool, default False
        If True, treats columns as text containing ISO format UTC datetime strings.
    round_to_second : bool, default True
        If True, rounds datetimes to nearest second (removes microseconds).
    errors : {'raise', 'coerce', 'ignore'}, default 'raise'
        How to handle datetime parsing errors:
        - 'raise': Raise exception on invalid datetime values
        - 'coerce': Convert invalid values to NaT
        - 'ignore': Return original data if parsing fails
    drop_originals : bool, default False
        If True, drops original datetime columns after expansion.
        Use with caution - recommended to keep originals for debugging.

    Returns
    -------
    pd.DataFrame
        DataFrame with all datetime columns expanded.

    Examples
    --------
    Auto-detect and expand all datetime columns:

    >>> df = pd.read_sql("SELECT * FROM orders", conn)
    >>> df = expand_all_datetime_columns(df, source_is_text=True)
    >>> # Expands: created_at, updated_at, and any other *_at columns

    Explicitly specify columns to expand:

    >>> df = expand_all_datetime_columns(
    ...     df,
    ...     datetime_columns=['created_at', 'updated_at'],
    ...     source_is_text=True
    ... )

    Use in method chaining:

    >>> df = (pd.read_sql("SELECT * FROM sales", conn)
    ...       .pipe(expand_all_datetime_columns, source_is_text=True))

    Drop original columns after expansion:

    >>> df = expand_all_datetime_columns(
    ...     df,
    ...     source_is_text=True,
    ...     drop_originals=True  # Use with caution
    ... )

    Notes
    -----
    - Auto-detection looks for columns ending in: '_at', '_datetime_utc', '_utc', '_datetime'
    - All columns are expanded with the same parameters
    - For mixed scenarios (some text, some datetime), expand columns individually
    """
    # Auto-detect datetime columns if not specified
    if datetime_columns is None:
        datetime_columns = [
            col for col in df.columns
            if any(col.endswith(suffix) for suffix in ['_at', '_datetime_utc', '_utc', '_datetime'])
        ]
        logger.info(f"Auto-detected {len(datetime_columns)} datetime columns: {datetime_columns}")
    else:
        logger.info(f"Expanding {len(datetime_columns)} specified columns: {datetime_columns}")

    if not datetime_columns:
        logger.warning("No datetime columns found to expand")
        return df

    # Expand each column
    for col in datetime_columns:
        df = expand_datetime_column(
            df, col,
            source_is_text=source_is_text,
            round_to_second=round_to_second,
            errors=errors
        )

    # Optionally drop originals
    if drop_originals:
        logger.info(f"Dropping original datetime columns: {datetime_columns}")
        df = df.drop(columns=datetime_columns)

    return df
