from bluer_objects.README.items import ImageItems

from bluer_ugv.README.ugvs.db import dict_of_ugvs
from bluer_ugv.README.validations.db import dict_of_validations

docs = [
    {
        "path": f"../docs/UGVs/{ugv_name}.md",
        "items": ImageItems({item: "" for item in info.get("items", [])}),
        "macros": {
            "validations:::": [
                "validations: {}".format(
                    ", ".join(
                        sorted(
                            [
                                f"[`{validation_name}`](../validations/{validation_name}.md)"
                                for validation_name, info in dict_of_validations.items()
                                if any(
                                    ugv_name_.startswith(f"{ugv_name}:")
                                    for ugv_name_ in info["ugv_name"]
                                )
                            ]
                        )
                    )
                ),
            ]
        },
    }
    for ugv_name, info in dict_of_ugvs.items()
]
