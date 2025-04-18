from typing import List

from harmonic_cadence.domain.constants import (
    CHROMATIC_NOTES,
    DEGREES_MAJOR,
    DEGREES_MINOR,
    MODE_HARMONY,
    MODE_NAMES_PT,
    MODES,
    NOTE_REPLACEMENTS,
)


def normalize_note(note: str) -> str:
    """Normaliza uma nota para sua forma padrão."""
    return NOTE_REPLACEMENTS.get(note, note)


def get_interval(note1: str, note2: str) -> int:
    """Calcula o intervalo entre duas notas em semitons."""
    n1 = CHROMATIC_NOTES.index(normalize_note(note1))
    n2 = CHROMATIC_NOTES.index(normalize_note(note2))
    return (n2 - n1) % 12


def transpose_note(note: str, interval: int) -> str:
    """Transpõe uma nota por um determinado intervalo."""
    n = CHROMATIC_NOTES.index(normalize_note(note))
    return CHROMATIC_NOTES[(n + interval) % 12]


def transpose_scale(scale: List[str], key: str) -> List[str]:
    """Transpõe uma escala para a tonalidade desejada."""
    base_note = "C"
    interval = get_interval(base_note, key)
    return [transpose_note(note, interval) for note in scale]


def build_harmonic_field(mode_name: str, key: str) -> str:
    """Constrói o campo harmônico de um modo na tonalidade desejada."""
    scale = MODES[mode_name]
    harmony = MODE_HARMONY.get(mode_name, [])
    transposed_scale = transpose_scale(scale, key)
    degrees = DEGREES_MAJOR if mode_name == "maior" else DEGREES_MINOR

    # Garante que todas as listas tenham 7 elementos
    if len(transposed_scale) < 7:
        transposed_scale += [""] * (7 - len(transposed_scale))
    if len(harmony) < 7:
        harmony += [""] * (7 - len(harmony))
    if len(degrees) < 7:
        degrees += [""] * (7 - len(degrees))

    field = []
    for deg, note, chord_type in zip(degrees, transposed_scale, harmony):
        if note:
            field.append(f"{deg}: {note}{chord_type}")
    return " | ".join(field)


def describe_modal_borrowing(chord_root: str, key: str) -> str:
    """
    Identifica possíveis origens modais para um acorde fora do campo harmônico principal.
    Retorna uma string descritiva das origens possíveis.
    """
    if chord_root == key:
        return "-"

    possible_sources = []
    for mode_name, scale in MODES.items():
        transposed_scale = transpose_scale(scale, key)
        if chord_root in transposed_scale:
            possible_sources.append(mode_name)

    if not possible_sources:
        return "Origem não identificada"

    descriptions = []
    for mode_name in possible_sources:
        nome = MODE_NAMES_PT.get(mode_name, mode_name)
        escala = " ".join(transpose_scale(MODES[mode_name], key))
        campo = build_harmonic_field(mode_name, key)
        descriptions.append(f"{nome} de {key}: [{escala}] | Campo harmônico: {campo}")

    return " || ".join(descriptions)
