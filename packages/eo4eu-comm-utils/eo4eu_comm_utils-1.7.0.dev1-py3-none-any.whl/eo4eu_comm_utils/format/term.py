from eo4eu_base_utils.typing import Self


class TermFormatter:
    """A formatter which adds predetermined terminal escape codes 
    for color and style to the output

    :param color: The color escape code
    :type color: int|None
    :param style: The style escape code
    :type style: int|None
    """

    def __init__(self,
        color: int|None = None,
        style: int|None = None
    ):
        self.color = color
        self.style = style
        self._formatter = None

    def _create_formatter(self):
        esc_code = "\033["
        color = "" if self.color is None else str(self.color)
        style = "" if self.style is None else f";{self.style}"
        if color == "" and style == "":
            self._formatter = lambda s: s
        else:
            self._formatter = lambda s: f"{esc_code}{color}{style}m{s}{esc_code}0m"

    def fmt(self, input: str) -> str:
        """Format a string to have the given 
        color and style

        :param input: The input string
        :type input: str
        :rtype: str
        """
        if self._formatter is None:
            self._create_formatter()
        return self._formatter(input)

    def bold(self) -> Self:
        """Makes a `TermFormatter` with the same color 
        and bold style

        :rtype: TermFormatter
        """
        return TermFormatter(
            color = self.color,
            style = 1
        )

    @classmethod
    def default(cls) -> Self:
        """Makes a `TermFormatter` with no color/style

        :rtype: TermFormatter
        """
        return TermFormatter()

    @classmethod
    def red(cls) -> Self:
        """Makes a `TermFormatter` with red color and no style

        :rtype: TermFormatter
        """
        return TermFormatter(color = 31)

    @classmethod
    def green(cls) -> Self:
        """Makes a `TermFormatter` with red green and no style

        :rtype: TermFormatter
        """
        return TermFormatter(color = 32)

    @classmethod
    def yellow(cls) -> Self:
        """Makes a `TermFormatter` with yellow color and no style

        :rtype: TermFormatter
        """
        return TermFormatter(color = 33)

    @classmethod
    def blue(cls) -> Self:
        """Makes a `TermFormatter` with blue color and no style

        :rtype: TermFormatter
        """
        return TermFormatter(color = 34)

    @classmethod
    def cyan(cls) -> Self:
        """Makes a `TermFormatter` with cyan color and no style

        :rtype: TermFormatter
        """
        return TermFormatter(color = 37)
