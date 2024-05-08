# pip install cairosvg httpx PyYAML
import re
from pathlib import Path

import cairosvg
import httpx
import yaml
from yaml.loader import SafeLoader

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

with open(PROJECT_PATH / 'links.yml', 'r') as f:
    LINKS_DATA = yaml.load(f, Loader=SafeLoader)


def download_icon(icon_name: str):
    svg = httpx.get(f"https://api.iconify.design/{icon_name}.svg", params={"color": "currentColor"}).text
    (ICONS_PATH / f"{icon_name}.svg").write_text(svg)

    (ICONS_PATH / f"{icon_name}.png").write_bytes(
        cairosvg.svg2png(
            svg.replace('fill="currentColor"', 'fill="black"').encode("utf-8"),
            parent_width=24,
            parent_height=24,
            output_height=120,
            output_width=120,
        )
    )

    (ICONS_PATH / f"{icon_name}.dark.png").write_bytes(
        cairosvg.svg2png(
            svg.replace('fill="currentColor"', 'fill="white"').encode("utf-8"),
            parent_width=24,
            parent_height=24,
            output_height=120,
            output_width=120,
        )
    )


def generate_links(section_type: str = None):
    for data in LINKS_DATA.get(section_type, LINKS_DATA.values()):
        if not (ICONS_PATH / f"{data['icon']}.png").exists():
            download_icon(data["icon"])
        yield (
            f'<a href="{data["link"]}">'
            f'<picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="icons/{data["icon"]}.dark.png">'
            f'<img alt="{data["alt"]}" src="icons/{data["icon"]}.png" width="32px" height="32px">'
            f'</picture>'
            f'{data["alt"]}'
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
    README_PATH.write_text(''.join(regenerate_readme()))


if __name__ == '__main__':
    main()
