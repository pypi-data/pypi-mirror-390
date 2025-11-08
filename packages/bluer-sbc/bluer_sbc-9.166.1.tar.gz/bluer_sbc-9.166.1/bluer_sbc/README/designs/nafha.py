from bluer_objects import README
from bluer_objects.README.items import ImageItems

from bluer_sbc.README.designs.consts import assets2
from bluer_sbc.README.design import design_doc

image_template = assets2 + "nafha/{}?raw=true"

marquee = README.Items(
    [
        {
            "name": "nafha",
            "marquee": image_template.format("01.png"),
            "url": "./bluer_sbc/docs/nafha",
        }
    ]
)

items = ImageItems(
    {
        image_template.format(f"{filename}"): ""
        for filename in [f"{index+1:02}.png" for index in range(4)]
        + [
            "20251028_123428.jpg",
            "20251028_123438.jpg",
            "20251103_215221.jpg",
            "20251103_215248.jpg",
            "20251103_215253.jpg",
            "20251103_215257.jpg",
            "20251103_215301.jpg",
            "20251103_215319.jpg",
        ]
    },
)

parts = {
    "dsn-vc288": "",
    "charging-port": "",
    "pwm-manual-dc-motor-controller": "",
    "heater-element": "12 V, 4.5 Ω, 32 w",
}

docs = [
    design_doc(
        "nafha",
        items,
        parts,
        own_folder=True,
        parts_reference="../parts",
    ),
    {
        "path": "../docs/nafha/parts-v1.md",
    },
    {
        "path": "../docs/nafha/parts-v2.md",
    },
]
