from typing import Dict, List

# Escalas e graus básicos
MAJOR_SCALE = ["C", "D", "E", "F", "G", "A", "B"]
MINOR_SCALE = ["A", "B", "C", "D", "E", "F", "G"]
DEGREES_MAJOR = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
DEGREES_MINOR = ["i", "ii°", "III", "iv", "v", "VI", "VII"]

# Funções harmônicas detalhadas
HARMONIC_FUNCTIONS: Dict[str, Dict[str, str | List[str]]] = {
    "T": {
        "name": "Tônica",
        "description": "Centro tonal, ponto de repouso e resolução",
        "degrees": ["I", "i", "vi", "vi7", "VI", "VI7", "iii", "III"],
    },
    "SD": {
        "name": "Subdominante",
        "description": "Prepara a dominante, criando movimento e expectativa",
        "degrees": ["IV", "iv", "ii", "iim7", "II", "II7"],
    },
    "D": {
        "name": "Dominante",
        "description": "Cria tensão e pede resolução para a tônica",
        "degrees": ["V", "V7", "v", "v7", "vii°", "vii°7"],
    },
    "D2": {
        "name": "Segunda Cadencial",
        "description": "Acorde menor com sétima que precede a dominante (II-V-I)",
        "degrees": ["ii", "iim7"],
    },
    "SubV": {
        "name": "Substituto de Dominante",
        "description": "Dominante substituto (bII7), resolve na tônica por movimento cromático",
        "degrees": ["bII7"],
    },
    "Sub2": {
        "name": "Substituto do IIm7",
        "description": "Acorde meio-tom acima do IIm7, usado para aproximação cromática",
        "degrees": ["biii"],
    },
    "Dsec": {
        "name": "Dominante Secundário",
        "description": "Dominante de outro grau que não a tônica",
        "degrees": ["V7/II", "V7/III", "V7/IV", "V7/V", "V7/VI", "V7/VII"],
    },
    "Emp": {
        "name": "Empréstimo Modal",
        "description": "Acordes vindos do modo paralelo",
        "degrees": ["bVI", "bVII", "IVm"],
    },
    "Dim": {
        "name": "Diminuto de Passagem",
        "description": "Acorde diminuto que liga acordes vizinhos",
        "degrees": ["vii°", "#iv°"],
    },
    "Crom": {
        "name": "Aproximação Cromática",
        "description": "Acordes meio-tom acima ou abaixo do alvo",
        "degrees": [],
    },
}

# Modos e suas escalas
MODES = {
    "maior": ["C", "D", "E", "F", "G", "A", "B"],
    "menor_natural": ["C", "D", "Eb", "F", "G", "Ab", "Bb"],
    "menor_harmonica": ["C", "D", "Eb", "F", "G", "Ab", "B"],
    "menor_melodica": ["C", "D", "Eb", "F", "G", "A", "B"],
    "dórico": ["C", "D", "Eb", "F", "G", "A", "Bb"],
    "frígio": ["C", "Db", "Eb", "F", "G", "Ab", "Bb"],
    "lídio": ["C", "D", "E", "F#", "G", "A", "B"],
    "mixolídio": ["C", "D", "E", "F", "G", "A", "Bb"],
    "lócrio": ["C", "Db", "Eb", "F", "Gb", "Ab", "Bb"],
}

# Nomes dos modos em português
MODE_NAMES_PT = {
    "maior": "Maior paralela",
    "menor_natural": "Menor natural paralela",
    "menor_harmonica": "Menor harmônica paralela",
    "menor_melodica": "Menor melódica paralela",
    "dórico": "Modo dórico",
    "frígio": "Modo frígio",
    "lídio": "Modo lídio",
    "mixolídio": "Modo mixolídio",
    "lócrio": "Modo lócrio",
}

# Campo harmônico dos modos
MODE_HARMONY = {
    "maior": ["maj7", "m7", "m7", "maj7", "7", "m7", "m7b5"],
    "menor_natural": ["m7", "m7b5", "maj7", "m7", "m7", "maj7", "7"],
    "menor_harmonica": ["m(maj7)", "m7b5", "maj7#5", "m7", "7", "maj7", "dim7"],
    "menor_melodica": ["m(maj7)", "m7", "maj7#5", "7", "7", "m7b5", "m7b5"],
    "dórico": ["m7", "m7", "maj7", "7", "m7", "m7b5", "maj7"],
    "frígio": ["m7", "maj7", "7", "m7", "m7b5", "maj7", "7"],
    "lídio": ["maj7", "7", "m7", "m7", "maj7", "m7b5", "m7"],
    "mixolídio": ["7", "m7", "m7", "maj7", "m7", "m7b5", "maj7"],
    "lócrio": ["m7b5", "maj7", "m7", "m7", "maj7", "7", "m7"],
}

# Padrões de cadência
CADENCE_PATTERNS = {
    "major": {
        "authentic": ("V", "I"),
        "plagal": ("IV", "I"),
        "deceptive": ("V", "vi"),
        "half": ("*", "V"),  # * significa qualquer grau
    },
    "minor": {
        "authentic": ("V", "i"),
        "plagal": ("iv", "i"),
        "deceptive": ("V", "VI"),
        "half": ("*", "v"),
    },
}

# Substituições de notas para normalização
NOTE_REPLACEMENTS = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}

# Notas cromáticas
CHROMATIC_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
