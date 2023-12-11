from jsonschema import validate

ABSOLVENTENFEIER = {
    "type": "object",
    "properties": {
        "course": {
            "type": "string",
            "enum": ["Physik", "Medizinphysik", "Lehramt"],
            "label": "Studiengang",
            "error_hint": "Triff bitte eine Auswahl.",
        },
        "degree": {
            "type": "string",
            "enum": ["Bachelor", "Master", "Promotion"],
            "label": "Abschluss",
            "error_hint": "Triff bitte eine Auswahl.",
        },
        "chair": {
            "type": "string",
            "enum": "E1 E2 E3 E4 E5 E6 T1 T2 T3 T4 Beschleunigerphysik Extern".split(
                " "
            ),
            "label": "Lehrstuhl",
            "error_hint": "Triff bitte eine Auswahl.",
        },
        "guests": {
            "type": "integer",
            "minimum": 1,
            "maximum": 8,
            "default": 1,
            "label": "Anzahl der Gäste (inklusive dir)",
            "error_hint": (
                "Mit wie vielen Personen wirst du erscheinen "
                "(inklusive dir)?  Momentan darfst du bis zu 7 andere Gäste "
                "mitbringen."
            ),
        },
        "title": {
            "type": "string",
            "label": "Titel der Arbeit",
            "format": "latex",
            "error_hint": "Bitte gib hier den Titel deiner Abschlussarbeit ein.",
        },
        "valid_exam_date": {
            "type": "boolean",
            "label": "Meine letzte Prüfung war im Jahr 2018.",
            "error_hint": (
                "Falls du deine letzte Prüfung im Jahr 2019 hattest "
                "oder noch haben wirst, bist du herzlich zur Absolventenfeier "
                "2019 eingeladen, die Anfang 2020 stattfinden wird."
            ),
            "const": True,
        },
        "allow_contact": {
            "type": "boolean",
            "label": (
                "Ich bin über die Absolventenfeier hinaus damit "
                "einverstanden, per E-Mail von PeP et al. e.V.  auf dem Laufenden "
                'gehalten zu werden.<br /><span className=help-block"><small>'
                "Zu diesem Zweck wird deine E-Mail-Adresse von einigen Mitgliedern "
                "des PeP-Vorstandes einsehbar sein. Die Adresse wird an keine "
                "Dritten weitergegeben.  </small></span>"
            ),
        },
    },
    "required": ["degree", "chair", "guests", "title"],
}


TOOLBOX = {
    "type": "object",
    "properties": {
        "toolbox": {
            "type": "boolean",
            "label": "Ich möchte an der ersten Woche teilnehmen (Python/Make/Git)",
        },
        "latex": {
            "type": "boolean",
            "label": "Ich möchte an der zweiten Woche teilnehmen (LaTeX)",
        },
        "os": {
            "type": "string",
            "enum": [
                "Windows",
                "macOS",
                "Debian/Ubuntu/Mint",
                "Fedora/RedHat",
                "ArchLinux",
                "Was exotisches",
            ],
            "label": "Betriebssystem",
        },
        "skill": {
            "type": "string",
            "format": "radio",
            "label": "Programmier-Erfahrung",
            "enum": [
                "Noch nie programmiert",
                "Schon mal programmiert, aber noch nicht in Python",
                "Schon mal programmiert, auch in Python",
            ],
        },
        "languages": {
            "type": "object",
            "label": "Programmiersprachen",
            "properties": {
                "c": {"type": "boolean"},
                "cpp": {"type": "boolean", "label": "C++"},
                "python": {"type": "boolean"},
                "javascript": {"type": "boolean", "label": "JavaScript"},
                "java": {"type": "boolean"},
                "haskell": {"type": "boolean"},
                "pascal": {"type": "boolean"},
                "fortran": {"type": "boolean"},
                "other": {"type": "string", "label": "Weitere"},
            },
        },
        "toolbox_interests": {
            "type": "object",
            "label": "Mich interessiert besonders (1. Woche)",
            "properties": {
                "git": {
                    "type": "boolean",
                    "label": "Zusammenarbeiten / Versionskontrolle mit Git",
                },
                "python": {
                    "type": "boolean",
                    "label": "Versuchsauswertung mit Python / Numpy / Scipy",
                },
                "make": {
                    "type": "boolean",
                    "label": "Automatisierung/Reproduzierbarkeit mit Make",
                },
                "cli": {"type": "boolean", "label": "Umgang mit der Kommandozeile"},
                "plotting": {
                    "type": "boolean",
                    "label": "Qualitativ hochwertige Grafiken mit Matplotlib",
                },
                "uncertainties": {
                    "type": "boolean",
                    "label": "Automatisierung von Fehlerrechnung und symbolisches Rechnen",
                },
            },
        },
        "latex_level": {
            "type": "string",
            "label": "Erfahrung mit LaTeX",
            "format": "radio",
            "enum": ["Noch nie gehört", "Schon mal ausprobiert", "TeXpert"],
        },
        "latex_interests": {
            "type": "object",
            "label": "Mich interessiert besonders (2. Woche)",
            "properties": {
                "text": {"type": "boolean", "label": "Textsatz"},
                "math": {"type": "boolean", "label": "Formelsatz"},
                "toc": {
                    "type": "boolean",
                    "label": "Automatisierung von Inhalts- und anderen Verzeichnissen",
                },
                "bib": {
                    "type": "boolean",
                    "label": "Korrektes Zitieren und Literaturverzeichniss",
                },
                "tikz": {"type": "boolean", "label": "Zeichnungen mit TikZ"},
                "beamer": {"type": "boolean", "label": "Präsentationen mit Beamer"},
            },
        },
        "other_interesets": {"type": "string", "label": "Mich interessiert außerdem"},
        "remarks": {
            "type": "string",
            "label": "Weitere Anmerkungen (z.B. Terminkollisionen)",
        },
    },
}


SOMMERAKADEMIE = {
    "type": "object",
    "properties": {
        "phone": {
            "type": "string",
            "label": """
            Mobiltelefon<br/>
            <span><small>
              Wir benötigen die Telefonnummer, um dich im Notfall kontaktieren
              zu können. Die Nummer wird im Anschluss der Akademie gelöscht.
            </small></span>
            """,
        },
        "semester": {
            "type": "integer",
            "minimum": 0,
            "label": "Semester",
        },
        "course": {
            "type": "string",
            "enum": ["Physik", "Medizinphysik", "Lehramt"],
            "label": "Studiengang",
            "error_hint": "Triff bitte eine Auswahl.",
        },
        "nutrition": {
            "type": "string",
            "enum": ["Fleisch ok", "Vegetarisch", "Vegan"],
            "label": "Ernährung",
        },
        "intolerances": {
            "type": "string",
            "label": "Unverträglichkeiten",
        },
        "arrival_by_myself": {
            "type": "boolean",
            "label": "Eigenanreise",
        },
        "comments": {
            "type": "string",
            "label": "Sonstige Anmerkungen",
            "format": "multiline",
        },
    },
    "required": ["phone"],
}


if __name__ == "__main__":
    validate(ABSOLVENTENFEIER, META_SCHEMA)  # noqa
    print("All schemata validated successfully")
