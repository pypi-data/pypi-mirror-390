from bluer_objects.README.items import ImageItems
from bluer_sbc.parts.db import db_of_parts
from bluer_sbc.parts.consts import parts_url_prefix

from bluer_ugv.README.swallow.consts import (
    swallow_assets2,
    swallow_electrical_designs,
)
from bluer_ugv.designs.swallow.parts import dict_of_parts
from bluer_ugv.README.swallow.digital.design import mechanical, ultrasonic_sensor
from bluer_ugv.swallow.session.classical.keyboard.keys import ControlKeys


docs = (
    [
        {
            "path": "../docs/swallow/digital/design",
        },
        {
            "path": "../docs/swallow/digital/design/computers.md",
        },
        {
            "path": "../docs/swallow/digital/design/operation.md",
            "cols": 2,
            "items": ImageItems(
                {
                    f"{swallow_assets2}/20251019_121811.jpg": "",
                    f"{swallow_assets2}/20251019_121842.jpg": "",
                }
            ),
            "macros": {
                "keys:::": ControlKeys.as_table(),
            },
        },
        {
            "path": "../docs/swallow/digital/design/parts.md",
            "items": db_of_parts.as_images(
                dict_of_parts,
                reference=parts_url_prefix,
            ),
            "macros": {
                "parts:::": db_of_parts.as_list(
                    dict_of_parts,
                    reference=parts_url_prefix,
                    log=False,
                ),
            },
        },
        {
            "path": "../docs/swallow/digital/design/terraform.md",
            "items": ImageItems(
                {
                    f"{swallow_assets2}/20250611_100917.jpg": "",
                    f"{swallow_assets2}/lab.png": "",
                    f"{swallow_assets2}/lab2.png": "",
                }
            ),
        },
        {
            "path": "../docs/swallow/digital/design/steering-over-current-detection.md",
            "items": ImageItems(
                {
                    f"{swallow_electrical_designs}/steering-over-current.png": f"{swallow_electrical_designs}/steering-over-current.svg",
                }
            ),
        },
        {
            "path": "../docs/swallow/digital/design/rpi-pinout.md",
        },
    ]
    + mechanical.docs
    + ultrasonic_sensor.docs
)
