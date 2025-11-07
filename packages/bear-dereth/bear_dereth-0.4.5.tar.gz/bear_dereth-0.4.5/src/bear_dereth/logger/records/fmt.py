"""Format strings for log records."""

from __future__ import annotations

from enum import StrEnum

from funcy_bear.ops.strings.dot_template import DotTemplate, cache_unique
from funcy_bear.tools import SimpooQueue


class FormatCompiler:
    """A class that compiles format strings using string.Template."""

    def __init__(self, fmt: str) -> None:
        """Initialize the FormatCompiler with a format string."""
        self.template = DotTemplate(fmt)
        self._key_cache: set[str] | None = None
        self.queue: SimpooQueue = SimpooQueue()

    @property
    def key_cache(self) -> set[str]:
        """Get the cached set of unique keys used in the format string."""
        if self._key_cache is None:
            self._key_cache = cache_unique(self.template)
        return self._key_cache

    def compile(self, **subs) -> str:
        """Compile the format string with the given subs."""
        return self.template.safe_substitute(
            subs,
            self.key_cache,
            self.queue,
        )


class Keyword(StrEnum):
    """Available template keywords for log formatting."""

    TIMESTAMP = "timestamp"  # both date and time
    TIME = "time"
    DATE = "date"
    TZ = "tz"

    MSG = "msg"
    LEVEL = "level"

    CALLER_FUNCTION = "caller_function"
    FILENAME = "filename"
    FULLPATH = "fullpath"
    RELATIVE_PATH = "relative_path"
    PYTHON_PATH = "python_path"
    LINE_NUMBER = "line_number"
    CODE_LINE = "code_line"

    EXCEPTION = "exception"
    EXCEPTION_CLASS = "exception_class"
    EXCEPTION_DETAILS = "exception_details"

    # These should not have a $ prefix when used in format strings
    SPACE = " "
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    LEFT_CURLY = "{"
    RIGHT_CURLY = "}"
    PIPE = "|"
    COMMA = ","
    NEW_LINE = "\n"


IGNORE_CHARS: set[Keyword] = {
    Keyword.SPACE,
    Keyword.LEFT_BRACKET,
    Keyword.RIGHT_BRACKET,
    Keyword.LEFT_CURLY,
    Keyword.RIGHT_CURLY,
    Keyword.PIPE,
    Keyword.COMMA,
    Keyword.NEW_LINE,
}


class FormatConstructor:
    """A class that helps to construct format strings for log records."""

    def __init__(self, words: list[Keyword] | FormatList | None = None) -> None:
        """Initialize the FormatConstructor with a list of words.

        Args:
            words: An ordered dictionary mapping positions to keyword strings.
        """
        if words is None:
            words = []
        self.words: FormatList[Keyword] = FormatList(words) if isinstance(words, list) else words

    def build(self, *words) -> str:
        """Build the format string from the ordered words.

        Returns:
            A constructed format string.
        """
        format_parts: list[str] = []
        if not self.words and words:
            self.words.extend(words)

        for word in self.words:
            if word not in IGNORE_CHARS:
                format_parts.append(f"${word}")
            else:
                format_parts.append(word)
        self.words.clear()
        return "".join(format_parts)

    def __call__(self, *args, **kwargs) -> str:
        """Allow the instance to be called directly to build the format string."""
        return self.build(*args, **kwargs)


class FormatList[T = Keyword](list[T | Keyword]):
    """A specialized list to hold format keywords in order."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize the Format OrderedDict."""
        super().__init__(*args, **kwargs)

    def add_words(self, *words) -> None:
        """Add a word to the format at the specified position.

        Args:
            position: The position index for the word.
            word: The keyword string to add.
        """
        for w in words:
            if isinstance(w, (list | tuple)):
                self.add_words(*w)
            elif isinstance(w, Keyword):
                self.append(w)
            elif isinstance(w, str) and w in Keyword.__members__.values():
                self.append(Keyword(w))


# if __name__ == "__main__":
#     # Example usage

#     manual_list: list[Keyword] = [
#         Keyword.TIMESTAMP,
#         Keyword.SPACE,
#         Keyword.PIPE,
#         Keyword.LEVEL,
#         Keyword.PIPE,
#         Keyword.SPACE,
#         Keyword.MSG,
#     ]

#     words: list[str] = [
#         "timestamp",
#         " ",
#         "|",
#         "level",
#         "|",
#         " ",
#         "msg",
#     ]

#     word_list: FormatList[Keyword] = FormatList()
#     word_list.add_words(*words)

#     constructor = FormatConstructor(word_list)

#     format_string: str = constructor.build()
#     format_string2: str = constructor.build(*manual_list)
#     format_string3: str = constructor(*manual_list)
#     print(format_string)  # Output: $timestamp |$level| $msg
#     print(format_string2)  # Output: $timestamp |$level| $msg
#     print(format_string3)  # Output: $timestamp |$level| $msg
#     assert format_string == format_string2
#     assert format_string == format_string3
