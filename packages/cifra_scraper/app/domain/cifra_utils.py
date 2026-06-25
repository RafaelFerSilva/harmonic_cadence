
import re
import unicodedata

def clean_text(text: str) -> str:
    text = text.strip()
    text = unicodedata.normalize('NFC', text)
    return text

def decode_unicode_escape(text: str) -> str:
    if "\\u" in text:  # Verifica se há sequências de escape
        try:
            return bytes(text, 'utf-8').decode('unicode_escape')
        except Exception:
            pass  # Ignora erros (ex: sequências inválidas)
    return text

def is_tablature_line(line: str) -> bool:
    tab_pattern = re.compile(r'^[eEbBgGdDaA]\|[-0-9xX/\|\s]*\|?$')
    return bool(tab_pattern.match(line))

def is_chord_only_line(line: str) -> bool:
    # Adiciona suporte a acentos e outros caracteres
    chord_pattern = re.compile(
        r'^([A-G][#b]?(?:m|maj|min|sus|dim|aug|add)?\d*(?:/[A-G][#b]?)?\s*)+$',
        re.IGNORECASE | re.UNICODE  # Flags para Unicode
    )
    return bool(chord_pattern.match(line.strip()))

def is_section_marker(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith('[') and stripped.endswith(']')

def has_lyrics(line: str) -> bool:
    chord_pattern = re.compile(r'[A-G][#b]?(?:m|maj|min|sus|dim|aug|add)?\d*(?:/[A-G][#b]?)?')
    cleaned = chord_pattern.sub('', line)
    cleaned = re.sub(r'[\(\)\[\]\/\-_\s]', '', cleaned)
    return bool(cleaned)

def should_keep_line(line: str) -> bool:
    ignore_patterns = [
        r'^tom:$',
        r'^Parte \d+ de \d+$',
        r'^[eEbBgGdDaA]\|[-0-9xX/\|\s]*\|?$',
        r'^\s*$',
    ]
    cleaned_line = line.strip()

    if not cleaned_line:
        return False

    for pattern in ignore_patterns:
        if re.match(pattern, cleaned_line):
            return False

    if is_chord_only_line(cleaned_line) and not has_lyrics(cleaned_line):
        return is_section_marker(cleaned_line)

    return True

def process_cifra_line(line: str) -> str | None:
    decoded_line = decode_unicode_escape(line)  # Primeiro decodifica escapes
    cleaned_line = clean_text(decoded_line)     # Depois normaliza
    if not should_keep_line(cleaned_line):
        return None
    return cleaned_line  # Retorna o texto já limpo

def clean_cifra_lines(lines: list[str]) -> list[str]:
    cleaned_lines = []
    prev_processed = None
    for line in lines:
        processed = process_cifra_line(line)
        if processed is None:
            continue
        if processed == prev_processed:
            continue  # Remove duplicatas consecutivas
        cleaned_lines.append(processed)
        prev_processed = processed
    return cleaned_lines
