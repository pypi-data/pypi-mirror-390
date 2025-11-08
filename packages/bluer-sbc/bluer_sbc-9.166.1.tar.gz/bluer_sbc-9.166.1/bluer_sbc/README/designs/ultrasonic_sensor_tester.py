from bluer_objects import README
from bluer_objects.README.items import ImageItems

from bluer_sbc.README.designs.consts import assets2
from bluer_sbc.README.design import design_doc


image_template = assets2 + "ultrasonic-sensor-tester/{}?raw=true"

marquee = README.Items(
    [
        {
            "name": "ultrasonic-sensor-tester",
            "marquee": image_template.format("00.jpg"),
            "url": "./bluer_sbc/docs/ultrasonic-sensor-tester.md",
        }
    ]
)

items = ImageItems({image_template.format(f"{index:02}.jpg"): "" for index in range(6)})

docs = [
    design_doc(
        "ultrasonic-sensor-tester",
        items,
    )
]
