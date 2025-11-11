from typing import Tuple

import click


@click.group()
def entry():
    pass


@entry.command()
def themes():
    from .themes import get_themes

    click.echo("Available themes:")
    for name in get_themes():
        click.echo(f"  {name}")


# TODO: The formatter (and theme) can be determined automatically
# Use click to decode the value passed (I think)

@entry.command()
@click.option("--plain", "-p", is_flag=True, flag_value=True, help="Display the coin flip as plain text")
@click.option("--theme", "-t", type=str, default='default', help="Name of the display theme to use")
def flip(plain: bool, theme: str):
    from .roll import Roll
    from .output import TextFormatter, ArtFormatter
    from .themes import get_theme

    if plain:
        fmt = TextFormatter()
    else:
        t = get_theme(theme)
        fmt = ArtFormatter(t)

    letters = {1: 'H', 2: 'T'}

    v = Roll("d2").roll()[0]

    out = fmt.text(letters[v])
    click.echo(out)


@entry.command()
@click.argument("s", type=str, nargs=-1, required=True)
@click.option("--add", "-a", is_flag=True, flag_value=True, help="Add up the dice and display a total")
@click.option("--plain", "-p", is_flag=True, flag_value=True, help="Display the roll as plain text")
@click.option("--theme", "-t", type=str, default='default', help="Name of the display theme to use")
def roll(s: Tuple[str, ...], add: bool, plain: bool, theme: str):
    from .roll import Roll
    from .output import TextFormatter, ArtFormatter
    from .themes import get_theme

    if plain:
        fmt = TextFormatter()
    else:
        t = get_theme(theme)
        fmt = ArtFormatter(t)

    in_str = ' '.join(s)

    r = Roll()
    r.parse(in_str)

    vs = r.roll()

    out = ' '.join(str(v) for v in vs)
    if add:
        out += f'\n= {str(sum(vs))}'

    fmt_out = fmt.text(out)
    click.echo(fmt_out)