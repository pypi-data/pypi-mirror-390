"""
A tool for generating customizable ASCII art messages with speech bubbles and cow-style templates, supporting styled text using AnsiMarkup.
"""

import enum
import json
import sys
import textwrap
from pathlib import Path

import ansimarkup
import appdirs
import cli_box
import click
import requests


DEFAULT_CORNERS = ("/", "\\", "/", "\\")
DEFAULT_SIDES = ("-", "|", "-", "|")

CONFIG_DIR = Path(appdirs.user_config_dir("ccowsay"))
CONFIG_DIR.mkdir(exist_ok=True)

CONFIG_FILE = CONFIG_DIR / "ccowsay.conf"

COW_CCOW_FILE = CONFIG_DIR / "cow.ccow"


def ensure_config_and_default_ccow_file() -> None:
    """
    Ensure config and default `.ccow` file
    """

    if not CONFIG_FILE.is_file():
        with open(CONFIG_FILE, "w") as config_file:
            json.dump({"default_format": "@/cow.ccow"}, config_file)

    if not COW_CCOW_FILE.is_file():
        fetch_ccow("cow.ccow")


class TextAlign(enum.Enum):
    """
    An enum representing align positions
    """

    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"


def fetch_ccow(ccow_file: str) -> Path:
    """
    Download a .ccow file from a GitHub repository and store it locally.

    Example:
        fetch_ccow("cow.ccow")
    Returns:
        Path: The local path to the saved .ccow file.
    """

    url = "https://raw.githubusercontent.com/ashkanfeyzollahi/ccows/main/" + ccow_file

    filename = Path(ccow_file).name
    dest = CONFIG_DIR / filename

    response = requests.get(url)

    if response.status_code != 200:
        raise

    downloaded_content = response.content

    dest.write_bytes(downloaded_content)

    return dest


def ccowsay(
    message: str,
    ccow_format: str,
    text_align: TextAlign = TextAlign.LEFT,
    wrap_width: int = 50,
    replace_whitespace: bool = False,
    corners: tuple[str, str, str, str] = DEFAULT_CORNERS,
    sides: tuple[str, str, str, str] = DEFAULT_SIDES,
    **values,
) -> str:
    """
    Generate a formatted ASCII art message using a customizable cow template.

    This function wraps a text message inside a speech or thought bubble,
    applies optional alignment and word wrapping, substitutes variables defined
    in a custom `.ccow` format, and returns the full rendered ASCII art as a string.

    Args:
        message (str):
            The message text to display inside the speech bubble.
        ccow_format (str):
            The name or content of the `.ccow` template defining the ASCII art structure.
        text_align (TextAlign, optional):
            Horizontal alignment for text inside the bubble (e.g., LEFT, CENTER, RIGHT).
            Defaults to `TextAlign.LEFT`.
        wrap_width (int, optional):
            The maximum line width before wrapping text.
            Use a negative value (e.g., `-1`) to disable wrapping.
            Defaults to `50`.
        replace_whitespace (bool, optional):
            If True, replaces whitespace characters (e.g., tabs, newlines) with spaces
            before rendering. Defaults to `False`.
        corners (tuple[str, str, str, str], optional):
            Characters used for the four bubble corners in the order:
            (top-left, top-right, bottom-left, bottom-right).
            Defaults to `DEFAULT_CORNERS`.
        sides (tuple[str, str, str, str], optional):
            Characters used for the bubble sides in the order:
            (top, bottom, left, right).
            Defaults to `DEFAULT_SIDES`.
        **values:
            Additional key-value pairs for custom template variables defined in the
            `.ccow` format (e.g., eyes, tongue, color).

    Returns:
        str:
            The complete rendered ASCII art string, ready for printing or further processing.
    """

    ccow_format_sections = ccow_format.split("\n---\n", 1)
    ccow_format_json_data = json.loads(ccow_format_sections[0])
    ccow_format_json_data.update(values)

    if message is None:
        message = sys.stdin.read()

    if wrap_width >= 0:
        message = "\n".join(
            textwrap.wrap(
                message, replace_whitespace=replace_whitespace, width=wrap_width
            )
        )

    return ansimarkup.parse(
        ccow_format_sections[1].format(
            backslash="\\",
            message=cli_box.box(
                message,
                corners=corners,
                sides=sides,
                align=text_align.value,
            ),
            slash="/",
            **ccow_format_json_data,
        )
    )


@click.command()
@click.argument("message", required=False)
@click.option("-l", "--list-formats", is_flag=True)
@click.option("-f", "--ccow-format", default=None)
@click.option(
    "-a", "--text-align", default=TextAlign.LEFT, type=click.Choice(TextAlign)
)
@click.option("-w", "--wrap-width", default=40, type=int)
@click.option("--replace-whitespace", is_flag=True)
@click.option("-c", "--corners", default=DEFAULT_CORNERS, nargs=4)
@click.option("-s", "--sides", default=DEFAULT_SIDES, nargs=4)
@click.option(
    "-v",
    "--values",
    default="{}",
)
@click.option(
    "--get",
)
def main(
    message: str,
    list_formats: bool,
    ccow_format: None | str,
    text_align: TextAlign,
    wrap_width: int,
    replace_whitespace: bool,
    corners: tuple[str, str, str, str],
    sides: tuple[str, str, str, str],
    values: str,
    get: None | str,
) -> None:
    """
    A tool for generating customizable ASCII art messages with speech bubbles and cow-style templates, supporting styled text using AnsiMarkup.
    """

    ensure_config_and_default_ccow_file()

    with open(CONFIG_FILE) as config_file:
        config: dict[str, str] = json.load(config_file)

    if list_formats:
        print(f"Here are the .ccow formats in found in {str(CONFIG_DIR.absolute())!r}:")
        for ccow_format_file in CONFIG_DIR.glob("*.ccow"):
            print(ccow_format_file.stem, end=" ")
        return

    if get is not None:
        fetch_ccow(get)
        return

    if ccow_format is None:
        ccow_format = config["default_format"]

    if ccow_format.startswith("@/"):
        ccow_format = (CONFIG_DIR / ccow_format[2:]).read_text()
    else:
        ccow_format = Path(ccow_format).read_text()

    print(
        ccowsay(
            message,
            ccow_format,
            text_align,
            wrap_width,
            replace_whitespace,
            corners,
            sides,
            **json.loads(values),
        )
    )


if __name__ == "__main__":
    main()
