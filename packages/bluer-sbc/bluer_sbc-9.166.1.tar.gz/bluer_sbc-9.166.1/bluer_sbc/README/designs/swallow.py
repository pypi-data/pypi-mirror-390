from bluer_objects import README
from bluer_objects.README.items import ImageItems

from bluer_sbc.README.designs.consts import assets2
from bluer_sbc.README.design import design_doc


image_template = assets2 + "swallow/design/v5/{}?raw=true"

marquee = README.Items(
    [
        {
            "name": "swallow",
            "marquee": image_template.format("01.jpg"),
            "url": "./bluer_sbc/docs/swallow.md",
        }
    ]
)

items = ImageItems(
    {image_template.format(f"{index+1:02}.jpg"): "" for index in range(6)}
)

parts = {
    "BTS7960": "2 x",
    "connector": "2 females",
    "white-terminal": "8 x",
    "nuts-bolts-spacers": "M3: ({})".format(
        " + ".join(
            [
                "8 x 25 mm spacer",
                "4 x 30 mm spacer",
                "4 x nut",
            ]
        )
    ),
    "solid-cable-1-15": "20 cm x (red + black/blue)",
}

docs = [
    design_doc(
        "swallow",
        items,
        parts,
    )
]
