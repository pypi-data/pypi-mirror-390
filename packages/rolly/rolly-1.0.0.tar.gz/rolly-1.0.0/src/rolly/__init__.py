from .roll import (
    Roll as Roll,
)

from .output import (
    Formatter as Formatter,
    ArtFormatter as ArtFormatter,
    TextFormatter as TextFormatter,
)

from .themes import (
    Theme as Theme,
    get_theme as get_theme,
)


# CLI interface for Rolly

def main():
    import click

    from .cli import entry

    try:
        entry()
    except RuntimeError as e:
        click.echo(e)
