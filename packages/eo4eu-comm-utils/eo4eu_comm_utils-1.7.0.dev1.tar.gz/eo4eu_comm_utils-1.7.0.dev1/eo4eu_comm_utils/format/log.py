import logging
import datetime
import traceback
from eo4eu_base_utils.typing import Callable

from .interface import Formatter
from .term import TermFormatter

default_level_fmt_dict = {
    logging.DEBUG:    TermFormatter.default().blue(),
    logging.INFO:     TermFormatter.blue().bold(),
    logging.WARNING:  TermFormatter.yellow().bold(),
    logging.ERROR:    TermFormatter.red().bold(),
    logging.CRITICAL: TermFormatter.red().bold(),
}
default_date_fmt = TermFormatter.blue().bold()
default_level_fmt_dict_nocolor = {
    logging.DEBUG:    TermFormatter.default(),
    logging.INFO:     TermFormatter.default(),
    logging.WARNING:  TermFormatter.default(),
    logging.ERROR:    TermFormatter.default(),
    logging.CRITICAL: TermFormatter.default(),
}
default_date_fmt_nocolor = TermFormatter.default()
default_levelname_map = {
    "DEBUG":    "DBUG",
    "INFO":     "INFO",
    "WARNING":  "WARN",
    "ERROR":    "FAIL",
    "CRITICAL": "CRIT",
}


def _fmt_level(
    level_fmt_dict: dict[int,Formatter],
    pad_levelname: bool,
    level: int,
    levelname: str,
    padding: int = 8,
) -> str:
    pad = ""
    if pad_levelname:
        pad = " " * (padding - len(levelname))
    try:
        formatter = level_fmt_dict[level]
        return f"[{formatter.fmt(levelname)}]{pad}"
    except Exception:
        return levelname


def _fmt_date(date_fmt: Formatter, date_strftime_fmt: str, posix_time: float) -> str:
    return date_fmt.fmt(
        datetime.datetime.fromtimestamp(posix_time).strftime(
            date_strftime_fmt
        )
    )


def default_prefix_formatter(
    record: logging.LogRecord,
    level_fmt_dict: dict[int,Formatter]|None = None,
    date_fmt: Formatter|None = None,
    pad_levelname: bool = False,
    date_strftime_fmt: str = "%H:%M:%S",
    levelname_map: dict[str,str]|None = None,
    **kwargs
) -> list[str]:
    if level_fmt_dict is None:
        level_fmt_dict = default_level_fmt_dict
    if date_fmt is None:
        date_fmt = default_date_fmt

    levelname = record.levelname
    if levelname_map is not None and levelname in levelname_map:
        levelname = levelname_map[levelname]

    return [
        _fmt_level(level_fmt_dict, pad_levelname, record.levelno, levelname),
        _fmt_date(date_fmt, date_strftime_fmt, record.created),
    ]


class LogFormatter(logging.Formatter):
    """A custom formatter for logs. This class is an ugly jenga 
    tower of a variety of different options; aside from making 
    logs prettier, it also has an option to print tracebacks on 
    specific log messages (e.g. warnings) for debug purposes.

    :param separator: The string put between the entries in the log message prefix
    :type separator: str
    :param use_color: Whether or not to add color to the output
    :type use_color: bool
    :param prefix_formatter: A function which takes the incoming logging.LogRecord and returns a list of strings to be joined by `separator` to make the prefix
    :type prefix_formatter: Callable[[logging.LogRecord], list[str]]|None
    :param prefix_formatter_kwargs: The keyword arguments to the `prefix_formatter` function
    :type prefix_formatter_kwargs: dict|None
    :param print_traceback: Whether or not to print the stack trace whenever a message with level `traceback_level` or higher is received
    :type print_traceback: bool
    :param traceback_level: The log level at which to print tracebacks, if `print_traceback` is True (default: logging.WARNING)
    :type traceback_level: int
    :param block_dashes: The number of dashes to add above and below traceback messages
    :type block_dashes: int
    :param add_name: Add the filename to the prefix
    :type add_name: bool
    :param add_path: Add the full file path to the prefix
    :type add_path: bool
    :param before message: String to add to the end of the prefix
    :type before_message: str
    """

    def __init__(
        self,
        separator: str = " - ",
        use_color: bool = True,
        prefix_formatter: Callable[[logging.LogRecord],list[str]]|None = None,
        prefix_formatter_kwargs: dict|None = None,
        print_traceback: bool = False,
        traceback_level: int = logging.WARNING,
        block_dashes: int = 35,
        add_name: bool = True,
        add_path: bool = False,
        before_message: str = ": "
    ):
        if prefix_formatter is None:
            prefix_formatter = default_prefix_formatter
        if prefix_formatter_kwargs is None:
            prefix_formatter_kwargs = {
                "levelname_map": default_levelname_map,
            }
        if not use_color:
            prefix_formatter_kwargs["level_fmt_dict"] = default_level_fmt_dict_nocolor
            prefix_formatter_kwargs["date_fmt"] = default_date_fmt_nocolor

        self.separator = separator
        self.prefix_formatter = prefix_formatter
        self.prefix_formatter_kwargs = prefix_formatter_kwargs
        self.print_traceback = print_traceback
        self.traceback_level = traceback_level
        self.block_dashes = block_dashes
        self.add_name = add_name
        self.add_path = add_path
        self.before_message = before_message

    def _dashline(self, msg: str) -> str:
        dash_str = "-" * self.block_dashes
        return f"{dash_str}{msg}{dash_str}"

    def _block(self, title: str, msg: str) -> list[str]:
        if self.block_dashes <= 0:
            return [msg]
        return [
            "",
            self._dashline(f" BEGIN {title} "),
            msg,
            self._dashline(f"  END {title}  "),
        ]

    def format(self, record: logging.LogRecord) -> str:
        """Convert a log record to a string. This method makes sure 
        this class fulfills the logging.LogFormatter interface

        :param record: The input log record
        :type record: logging.LogRecord
        :rtype: str
        """
        desc = self.prefix_formatter(record, **self.prefix_formatter_kwargs)
        if self.add_name:
            desc.append(record.name)
        if self.add_path:
            desc.append(f"{record.pathname}:{record.funcName}:{record.lineno}")

        msg = ""
        try:
            msg = str(record.msg % record.args)
        except Exception:
            msg = str(record.msg)

        blurbs = [msg]
        if all([
            self.print_traceback,
            record.levelno >= self.traceback_level
        ]):
            exc_str = traceback.format_exc()
            if not exc_str.startswith("NoneType: None"):
                blurbs.extend(self._block("EXCEPTION", exc_str))

        lines = []
        for blurb in blurbs:
            lines.extend(blurb.split("\n"))

        prefix = self.separator.join(desc) + self.before_message
        return prefix + f"\n{prefix}".join(lines)
