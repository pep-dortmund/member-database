from jsonschema import validate


ABSOLVENTENFEIER = {
    'type': 'object',
    'properties': {
        'chair': {'type': 'string', 'enum': ['E5']},
        'guests': {'type': 'integer', 'minimum': 1, 'maximum': 8, 'default': 1},
        'title': {'type': 'string'},
        'valid_exam_date': {'type': 'boolean', 'default': False},
        'allow_contact': {'type': 'boolean', 'default': False},
    },
    'required': ['name', 'email', 'chair'],
}


# meta schema to validate other schemata, taken from https://json-schema.org/specification.html#meta-schemas
META_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2019-09/schema",
    "$id": "https://json-schema.org/draft/2019-09/schema",
    "$vocabulary": {
        "https://json-schema.org/draft/2019-09/vocab/core": True,
        "https://json-schema.org/draft/2019-09/vocab/applicator": True,
        "https://json-schema.org/draft/2019-09/vocab/validation": True,
        "https://json-schema.org/draft/2019-09/vocab/meta-data": True,
        "https://json-schema.org/draft/2019-09/vocab/format": False,
        "https://json-schema.org/draft/2019-09/vocab/content": True
    },
    "$recursiveAnchor": True,

    "title": "Core and Validation specifications meta-schema",
    "allOf": [
        {"$ref": "meta/core"},
        {"$ref": "meta/applicator"},
        {"$ref": "meta/validation"},
        {"$ref": "meta/meta-data"},
        {"$ref": "meta/format"},
        {"$ref": "meta/content"}
    ],
    "type": ["object", "boolean"],
    "properties": {
        "definitions": {
            "$comment": "While no longer an official keyword as it is replaced by $defs, this keyword is retained in the meta-schema to prevent incompatible extensions as it remains in common use.",
            "type": "object",
            "additionalProperties": { "$recursiveRef": "#" },
            "default": {}
        },
        "dependencies": {
            "$comment": "\"dependencies\" is no longer a keyword, but schema authors should avoid redefining it to facilitate a smooth transition to \"dependentSchemas\" and \"dependentRequired\"",
            "type": "object",
            "additionalProperties": {
                "anyOf": [
                    { "$recursiveRef": "#" },
                    { "$ref": "meta/validation#/$defs/stringArray" }
                ]
            }
        }
    }
}


if __name__ == '__main__':
    validate(ABSOLVENTENFEIER, META_SCHEMA)
