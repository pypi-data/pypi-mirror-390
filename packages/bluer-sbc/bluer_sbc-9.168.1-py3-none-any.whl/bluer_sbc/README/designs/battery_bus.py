from bluer_objects import README
from bluer_objects.README.items import ImageItems
from bluer_objects.README.consts import assets_url
from bluer_objects.README.consts import designs_url

from bluer_sbc.README.design import design_doc

assets2 = assets_url(
    suffix="battery-bus",
    volume=2,
)

marquee = README.Items(
    [
        {
            "name": "battery bus",
            "marquee": f"{assets2}/20251007_221902.jpg",
            "url": "./bluer_sbc/docs/battery-bus.md",
        }
    ]
)

items = ImageItems(
    {
        f"{assets2}/concept.png": "",
        designs_url(
            "battery-bus/electrical/wiring.png?raw=true",
        ): designs_url(
            "battery-bus/electrical/wiring.svg",
        ),
        f"{assets2}/20251007_221902.jpg": "",
        f"{assets2}/20251007_220642.jpg": "",
        f"{assets2}/20251007_220520.jpg": "",
        f"{assets2}/20251007_220601.jpg": "",
    }
)

parts = {
    "SLA-Battery": "",
    "on-off-switch": "",
    "charging-port": "",
    "dsn-vc288": "",
}


docs = [
    design_doc(
        "battery-bus",
        items,
        parts,
    )
]
