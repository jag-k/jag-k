import re
from http.client import HTTPResponse
from pathlib import Path
from typing import TypeVar
from urllib.error import HTTPError
from urllib.request import urlopen

# pip install PyYAML
import yaml
from yaml.loader import SafeLoader

# pip install cairosvg
import cairosvg

PROJECT_PATH = Path(__file__).absolute().parent.parent
ICONS_PATH = PROJECT_PATH / "icons"
README_PATH = PROJECT_PATH / "README.md"
DEV_PATH = PROJECT_PATH / "dev.md"

SECTION_LINK_START = re.compile(
    r'<!--START_SECTION:links(?: type=(?P<type>.+))?-->'
)
SECTION_LINK_END = re.compile(
    r'<!--END_SECTION:links-->'
)

# <si-devtdotto alt="Jag_k Dev.to"/>
SIMPLE_ICON_RE = re.compile(
    r"<si-(?P<icon>\w+)(?: alt=\"(?P<alt>.*?)\")?/?>"
)

with open(PROJECT_PATH / 'links.yml', 'r') as f:
    LINKS_DATA = yaml.load(f, Loader=SafeLoader)


def generate_links(section_type: str = None):
    for data in LINKS_DATA.get(section_type, [i for i in LINKS_DATA.values()]):
        yield (
            f'<a href="{data["link"]}">'
            f'<picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="icons/{data["icon"]}.dark.png">'
            f'<img alt="{data["alt"]}" src="icons/{data["icon"]}.png" width="32px" height="32px">'
            f'</picture>'
            f'</a>\n'
        )

def regenerate_readme():
    with open(README_PATH, 'r', encoding='utf-8') as readme_file:
        section_started = False
        for line in readme_file.readlines():
            if not section_started:
                yield line
            section_start_match = SECTION_LINK_START.match(line)
            section_end_match = SECTION_LINK_END.match(line)

            if section_start_match:
                section_type = section_start_match.groupdict().get('type', None)
                section_started = True
                yield from generate_links(section_type)
                yield '<br/>\n'
                continue
            if section_end_match:
                yield line
                section_started = False


def main():
    data = ''.join(regenerate_readme())
    # with open(DEV_PATH, 'w', encoding='utf-8') as f:
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(data)


if __name__ == '__main__':
    main()
