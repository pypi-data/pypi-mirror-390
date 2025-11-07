"""A common error handler interface for loggers."""

from typing import Any

from bear_dereth.logger.records.stack_info import StackInfo


class ErrorHandler:
    """A common error handler interface for loggers."""

    def __init__(self, error: Any | None = None) -> None:
        """Initialize the ErrorHandler with a backup error logger."""
        from bear_dereth.logger.basic_logger.simple_logger import SimpleLogger  # noqa: PLC0415

        self.error: SimpleLogger = error or SimpleLogger()

    def __call__(self, *msg, name: str, error: Exception) -> None:
        """Handle errors from handlers. Override to customize error handling."""
        stack: StackInfo = StackInfo.from_current_stack()
        code_context: str = (
            stack.code_context[stack.index] if stack.code_context and stack.index is not None else "<unknown>"
        )

        self.error(
            *msg,
            related_name=name,
            caller_function=stack.caller_function,
            code_context=code_context.strip(),
            filename=stack.filename,
            line_number=stack.line_number,
            error_class=type(error).__name__,
            error_text=f"'{error!s}'",
            stack_value=stack.stack_value,
        )
