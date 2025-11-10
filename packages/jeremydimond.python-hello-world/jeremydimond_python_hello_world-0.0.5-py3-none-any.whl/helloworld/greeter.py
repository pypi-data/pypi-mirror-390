import sys


def say_hello(name: str = None) -> str:
    return f'Hello, {name}!' if name else 'Hello!'


def main_cli():  # pragma: no cover
    print(say_hello() if len(sys.argv) < 2 else f'{say_hello(name=sys.argv[1])}')
