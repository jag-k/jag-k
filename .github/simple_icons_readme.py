import re
from pathlib import Path
from typing import TypeVar
from urllib.error import HTTPError

from urllib.request import urlopen
from http.client import HTTPResponse


PROJECT_PATH = Path(__file__).absolute().parent.parent
ICONS_PATH = PROJECT_PATH / "icons"
README_PATH = PROJECT_PATH / "README.md"

# <si-devtdotto alt="Jag_k Dev.to"/>
SIMPLE_ICON_RE = re.compile(
    r"<si-(?P<icon>\w+)(?: alt=\"(?P<alt>.*?)\")?/?>"
)

with open(README_PATH, 'r', encoding='utf-8') as readme_file:
    README_CONTENT = readme_file.read().replace('<!--', '-->').split('-->')

_T = TypeVar('_T', bound=str)


def matcher(match: re.Match[_T]) -> _T:
    print(match)
    icon = match.group('icon')
    alt = match.group('alt')
    try:
        icon_req: HTTPResponse = urlopen(
            f"https://simpleicons.org/icons/{icon}.svg"
        )
    except HTTPError:
        print(f"Icon {icon} not found")
        return match.group(0)
    icon_path = ICONS_PATH / f"{icon}.svg"
    dark_icon_path = ICONS_PATH / f"{icon}.dark.svg"

    icon_data = icon_req.read().decode('utf-8')

    with open(icon_path, 'w', encoding='utf-8') as f:
        f.write(icon_data.replace('<svg', '<svg style="fill: #000"'))

    with open(dark_icon_path, 'w', encoding='utf-8') as f:
        f.write(icon_data.replace('<svg', '<svg style="fill: #fff"'))

    alt_attr = f' alt="{alt}"' if alt else ''
    return (
            f'<!--<si-{icon}{alt_attr}/>-->' +
            ''.join(
                f'<img width="32px" src="icons/{icon}{src}"{alt_attr}/>'
                for src in [
                    ".svg#gh-light-mode-only",
                    ".dark.svg#gh-dark-mode-only",
                ]
            )
    )


def replacer():
    for i, content in enumerate(README_CONTENT):
        if i % 2:
            yield f"<!--{content}-->"
            continue
        yield SIMPLE_ICON_RE.sub(matcher, content)


def main():
    res = ''.join(replacer())
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(res)


if __name__ == '__main__':
    main()
