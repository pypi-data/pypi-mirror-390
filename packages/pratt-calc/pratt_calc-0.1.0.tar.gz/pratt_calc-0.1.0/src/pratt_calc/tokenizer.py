import re
from collections.abc import Callable, Generator

from more_itertools import peekable

# See docstring for 'tokenize'.
type Token = int | str
type Stream = peekable[Token]
type tokenizer = Callable[[str], Generator[Token]]


def _stream(fn: tokenizer) -> Callable[[str], Stream]:
    """Convert the tokenizer's generator into a peekable."""

    def wrapper(raw_expression: str) -> Stream:
        gen = fn(raw_expression)

        return peekable(gen)

    return wrapper


@_stream
def tokenize(raw_expression: str) -> Generator[Token]:
    """Tokenize RAW_EXPRESSION.

    Integers are yielded as Python ints; everything else is yielded as
    its original string representation.

    """

    pattern = re.compile(r"\s*((\d+)|(.))")

    for mo in re.finditer(pattern, raw_expression):
        token = mo.group(1)

        if token.isdigit():
            yield int(token)
        else:
            yield token

    yield "eof"
