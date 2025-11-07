"""Quick Reference: Regular Expressions in Python"""

NORMAL_CHARACTERS = """
. or [^\\n\\r]    any character excluding a newline or carriage return
[A-Za-z]         alphabet
[a-z]            lowercase alphabet
[A-Z]            uppercase alphabet
\\d or [0-9]     digit
\\D or [^0-9]    non-digit
_                underscore
\\w or [A-Za-z0-9_]  alphabet, digit or underscore
\\W or [^A-Za-z0-9_] inverse of \\w
\\S              inverse of \\s
"""

WHITESPACE_CHARACTERS = """
space
\\t    tab
\\n    newline
\\r    carriage return
\\s    space, tab, newline or carriage return
"""

CHARACTER_SET = """
[xyz]       either x, y or z
[^xyz]      neither x, y nor z
[1-3]       either 1, 2 or 3
[^1-3]      neither 1, 2 nor 3

Think of a character set as an OR operation on the single characters that are enclosed between the square brackets.
Use ^ after the opening [ to "negate" the character set.
Within a character set, . means a literal period.
"""

ESCAPING = """
Characters that require escaping

Outside a character set:
\\.   period
\\^   caret
\\$   dollar sign
|     pipe
\\\\   backslash
\\/   forward slash
\\(   opening bracket
\\)   closing bracket
\\[   opening square bracket
\\]   closing square bracket
\\{   opening curly bracket
\\}   closing curly bracket

Inside a character set:
\\\\   backslash
\\]   closing square bracket

A ^ must be escaped only if it occurs immediately after the opening [ of the character set.
A - must be escaped only if it occurs between two alphabets or two digits.
"""

QUANTIFIERS = """
{2}      exactly 2
{2,}     at least 2
{2,7}    at least 2 but no more than 7
*        0 or more
+        1 or more
?        exactly 0 or 1

The quantifier goes after the expression to be quantified.
"""

BOUNDARIES = """
^   start of string
$   end of string
\\b  word boundary

How word boundary matching works:
- At the beginning of the string if the first character is \\w.
- Between two adjacent characters if the first is \\w and the second is \\W.
- At the end of the string if the last character is \\w.
"""

MATCHING = """
foo|bar        match either foo or bar
foo(?=bar)     match foo if it's before bar
foo(?!bar)     match foo if it's not before bar
(?<=bar)foo    match foo if it's after bar
(?<!bar)foo    match foo if it's not after bar
"""

GROUPING = """
(foo)          capturing group; match and capture foo
(?:foo)        non-capturing group; match foo without capturing
(foo)bar\\1    \\1 is a backreference to the 1st group; match foobarfoo
"""

EXAMPLES = """
# === Examples ===

# Match an email address
pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
# Example: "user.name+test@domain.co"

# Match a 5-digit ZIP code (US)
pattern = r"^\\d{5}$"
# Example: "90210"

# Match a phone number (simple version)
pattern = r"\\(?\\d{3}\\)?[- ]?\\d{3}[- ]?\\d{4}"
# Example: "(555) 123-4567" or "555-123-4567"

# Match a date in YYYY-MM-DD format
pattern = r"\\b\\d{4}-\\d{2}-\\d{2}\\b"
# Example: "2025-10-26"

# Match an IPv4 address
pattern = r"\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b"
# Example: "192.168.0.1"

# Match a simple URL
pattern = r"https?://[\\w.-]+(?:/[\\w./?%&=-]*)?"
# Example: "https://example.com/path?query=1"

# Match a word boundary
pattern = r"\\bcat\\b"
# Matches "cat" but not "concatenate" or "scatter"

# Match repeated words (using backreference)
pattern = r"\\b(\\w+)\\s+\\1\\b"
# Example: "bye bye" or "no no"

# Match any line that does NOT start with #
pattern = r"^(?!#).*"
# Useful for filtering config files or code comments

# Match a quoted string
pattern = r'"([^"\\\\]*(?:\\\\.[^"\\\\]*)*)"'
# Example: "Hello \"World\""
"""

DOCS: dict[str, str] = {
    "Normal Characters": NORMAL_CHARACTERS,
    "Whitespace Characters": WHITESPACE_CHARACTERS,
    "Character Set": CHARACTER_SET,
    "Escaping": ESCAPING,
    "Quantifiers": QUANTIFIERS,
    "Boundaries": BOUNDARIES,
    "Matching": MATCHING,
    "Grouping": GROUPING,
    "Examples": EXAMPLES,
}


def print_reference() -> None:
    """Print the regex quick reference."""
    from bear_dereth.reference._printer import syntax_print  # noqa: PLC0415

    syntax_print(DOCS, title="Regular Expressions Quick Reference", lang="python")


if __name__ == "__main__":
    print_reference()
