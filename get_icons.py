from requests import get

icons = [
"twitter",
"vk",
"instagram",
"telegram",
"facebook",
"devdotto",
"patreon",
"paypal",
"opencollective",
"qiwi",
]

for i in icons:
    res = get(f"https://simpleicons.org/icons/{i}.svg")
    with open(f'icons/{i}.svg', 'w') as svg:
        svg.write(res.text)
