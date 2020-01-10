from jsonschema import validate


ABSOLVENTENFEIER = {
    'type': 'object',
    'properties': {
        'course': {
            'type': 'string',
            'enum': ['Physik', 'Medizinphysik', 'Lehramt'],
            'label': 'Studiengang',
            'error_hint': 'Triff bitte eine Auswahl.',
        },
        'degree': {
            'type': 'string',
            'enum': ['Bachelor', 'Master', 'Promotion'],
            'label': 'Abschluss',
            'error_hint': 'Triff bitte eine Auswahl.',
        },
        'chair': {
            'type': 'string',
            'enum': 'E1 E2 E3 E4 E5 E6 T1 T2 T3 T4 Beschleunigerphysik Extern'.split(' '),
            'label': 'Lehrstuhl',
            'error_hint': 'Triff bitte eine Auswahl.',
        },
        'guests': {
            'type': 'integer',
            'minimum': 1,
            'maximum': 8,
            'default': 1,
            'label': 'Anzahl der Gäste (inklusive dir)',
            'error_hint': (
                'Mit wie vielen Personen wirst du erscheinen '
                '(inklusive dir)?  Momentan darfst du bis zu 7 andere Gäste '
                'mitbringen.',
            ),
        },
        'title': {
            'type': 'string',
            'label': 'Titel der Arbeit',
            'format': 'latex',
            'error_hint': 'Bitte gib hier den Titel deiner Abschlussarbeit ein.',
        },
        'valid_exam_date': {
            'type': 'boolean',
            'label': 'Meine letzte Prüfung war im Jahr 2018.',
            'error_hint': (
                'Falls du deine letzte Prüfung im Jahr 2019 hattest '
                'oder noch haben wirst, bist du herzlich zur Absolventenfeier '
                '2019 eingeladen, die Anfang 2020 stattfinden wird.',
            ),
            'const': True,
        },
        'allow_contact': {
            'type': 'boolean',
            'label': (
                'Ich bin über die Absolventenfeier hinaus damit '
                'einverstanden, per E-Mail von PeP et al. e.V.  auf dem Laufenden '
                'gehalten zu werden.<br /><span className=help-block"><small>'
                'Zu diesem Zweck wird deine E-Mail-Adresse von einigen Mitgliedern '
                'des PeP-Vorstandes einsehbar sein. Die Adresse wird an keine '
                'Dritten weitergegeben.  </small></span>'
            ),
        },
    },
    'required': ['degree', 'chair', 'guests', 'title'],
}


# meta schema to validate other schemata, taken from https://json-schema.org/specification.html#meta-schemas
META_SCHEMA = {
    '$schema': 'https://json-schema.org/draft/2019-09/schema',
    '$id': 'https://json-schema.org/draft/2019-09/schema',
    '$vocabulary': {
        'https://json-schema.org/draft/2019-09/vocab/core': True,
        'https://json-schema.org/draft/2019-09/vocab/applicator': True,
        'https://json-schema.org/draft/2019-09/vocab/validation': True,
        'https://json-schema.org/draft/2019-09/vocab/meta-data': True,
        'https://json-schema.org/draft/2019-09/vocab/format': False,
        'https://json-schema.org/draft/2019-09/vocab/content': True
    },
    '$recursiveAnchor': True,

    'title': 'Core and Validation specifications meta-schema',
    'allOf': [
        {'$ref': 'meta/core'},
        {'$ref': 'meta/applicator'},
        {'$ref': 'meta/validation'},
        {'$ref': 'meta/meta-data'},
        {'$ref': 'meta/format'},
        {'$ref': 'meta/content'}
    ],
    'type': 'object',
    'properties': {
        'definitions': {
            '$comment': 'While no longer an official keyword as it is replaced by $defs, this keyword is retained in the meta-schema to prevent incompatible extensions as it remains in common use.',
            'type': 'object',
            'additionalProperties': {'$recursiveRef': '#'},
            'default': {}
        },
        'dependencies': {
            '$comment': '"dependencies" is no longer a keyword, but schema authors should avoid redefining it to facilitate a smooth transition to "dependentSchemas" and "dependentRequired"',
            'type': 'object',
            'additionalProperties': {
                'anyOf': [
                    {'$recursiveRef': '#'},
                    {'$ref': 'meta/validation#/$defs/stringArray'}
                ]
            }
        }
    }
}


if __name__ == '__main__':
    validate(ABSOLVENTENFEIER, META_SCHEMA)
    print('All schemata validated successfully')
