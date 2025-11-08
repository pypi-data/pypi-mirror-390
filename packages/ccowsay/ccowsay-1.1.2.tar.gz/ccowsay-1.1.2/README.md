# ccowsay

![screenshot](./screenshot.png)

<p align="center">
  <em>
    🐮 A tool for generating customizable ASCII art messages with speech bubbles and cow-style templates, supporting styled text using AnsiMarkup.
  </em>
</p>

## Features

* Custom `.ccow` templates define ASCII art structure.
* Styled text formatting (colors, bold, italic, underline) via [AnsiMarkup](https://pypi.org/project/ansimarkup/).
* Text alignment (left, center, right), word wrapping, and whitespace replacement.
* Dynamic template variables (eyes, tongue, etc.) that can be overridden.
* Simple configuration directory for templates and defaults.

## Installation

```bash
pipx install ccowsay
```

## Basic Usage

```bash
ccowsay "Hello World!"
```

For full details of supported tags and syntax see the [AnsiMarkup documentation](https://pypi.org/project/ansimarkup/).

## Command-Line Options

| Option                 | Description                                                                                | Default   |
| ---------------------- | -------------------------------------------------------------------------------------------| --------- |
| `-f, --ccow-format`    | Path or alias to a `.ccow` template                                                        | `@/cow.ccow` |
| `-a, --text-align`     | Text alignment: `left`, `center`, `right`                                                  | `left`    |
| `-w, --wrap-width`     | Max width before wrapping (use `-1` to disable wrapping)                                   | `40`      |
| `--replace-whitespace` | Replace tabs/newlines with spaces                                                          | `False`   |
| `-c, --corners`        | Four characters for bubble corners (TL, TR, BL, BR)                                        | `/ \ / \` |
| `-s, --sides`          | Four characters for bubble sides (top, bottom, left, right)                                | `\| - \| -` |
| `-v, --values`         | JSON string of template variable overrides                                                 | `{}`      |
| `-l, --list-formats`   | List available `.ccow` templates                                                           | —         |
| `--get`                | Download a .ccow template from a GitHub repository and save it to the user config directory| —         |       

## Custom Templates

Templates live in your config directory (e.g., `~/.config/ccowsay/`).
Each `.ccow` file has two parts: JSON metadata, then ASCII art, separated by `---`. Example:

```text
{
  "eyes": "oo",
  "tongue": "  "
}
---
{message}
        {backslash}   ^__^
         {backslash}  ({eyes})\_______
            (__)\       )\/\
             {tongue} ||----w |
                ||     ||
```

Override variables with `--values`, for example:

```bash
ccowsay -f "@/cow.ccow" -v '{"eyes": "xx", "tongue": "U "}' "I'm tired..."
```

### Coloring with XML-Style Tags

You can use **XML-style tags** from [ansimarkup](https://ansimarkup.readthedocs.io/) to add colors, bold, or italic text **inside your `.ccow` templates**.

> [!WARNING]
> **Do not** use these tags directly in messages passed to `ccowsay` — they are intended for ASCII art templates only.

Example inside a `.ccow` file:

```text
{
  "eyes": "oo",
  "tongue": "  "
}
---
<red>{message}</red>
        {backslash}   ^__^
         {backslash}  (<green>{eyes}</green>)\_______
            (__)\       )\/\
             {tongue} ||----w |
                ||     ||
```

This ensures that all colors and styles are applied safely when rendering the ASCII art.

## Using Templates from the Config Directory

Any `.ccow` file placed in your **user config directory** (usually `~/.config/ccowsay/`) can be referenced using the `@/` prefix.

For example:

```bash
ccowsay -f "@/cow.ccow" "Hello World!"
```

* `@/cow` refers to `cow.ccow` inside your config directory.
* This works for any custom template you add there.
* The default configuration also uses this syntax to load the built-in cow.

## Downloading Templates

Use `--get` flag to download and store `.ccow` files locally:

```bash
ccowsay --get user/repo/path/to/file.ccow
```

## Embedding in Python

```python
from ccowsay import ccowsay, TextAlign

ascii_art = ccowsay(
    "<green>Hello from code!</green>",
    open("cow.ccow").read(),
    text_align=TextAlign.CENTER,
    wrap_width=40,
    eyes="oO",
    tongue="U "
)
print(ascii_art)
```

## License

MIT License — free to use, modify, and distribute.
