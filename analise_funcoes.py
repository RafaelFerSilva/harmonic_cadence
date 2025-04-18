import requests
import re
from collections import Counter

# Escalas e graus
MAJOR_SCALE = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
MINOR_SCALE = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
DEGREES_MAJOR = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']
DEGREES_MINOR = ['i', 'ii°', 'III', 'iv', 'v', 'VI', 'VII']

# Funções harmônicas detalhadas
HARMONIC_FUNCTIONS = {
    'T': {
        'name': 'Tônica',
        'description': 'Centro tonal, ponto de repouso e resolução',
        'degrees': ['I', 'i', 'vi', 'vi7', 'VI', 'VI7', 'iii', 'III']
    },
    'SD': {
        'name': 'Subdominante',
        'description': 'Prepara a dominante, criando movimento e expectativa',
        'degrees': ['IV', 'iv', 'ii', 'iim7', 'II', 'II7']
    },
    'D': {
        'name': 'Dominante',
        'description': 'Cria tensão e pede resolução para a tônica',
        'degrees': ['V', 'V7', 'v', 'v7', 'vii°', 'vii°7']
    },
    'D2': {
        'name': 'Segunda Cadencial',
        'description': 'Acorde menor com sétima que precede a dominante (II-V-I)',
        'degrees': ['ii', 'iim7']
    },
    'SubV': {
        'name': 'Substituto de Dominante',
        'description': 'Dominante substituto (bII7), resolve na tônica por movimento cromático',
        'degrees': ['bII7']
    },
    'Sub2': {
        'name': 'Substituto do IIm7',
        'description': 'Acorde meio-tom acima do IIm7, usado para aproximação cromática',
        'degrees': ['biii']
    },
    'Dsec': {
        'name': 'Dominante Secundário',
        'description': 'Dominante de outro grau que não a tônica',
        'degrees': ['V7/II', 'V7/III', 'V7/IV', 'V7/V', 'V7/VI', 'V7/VII']
    },
    'Emp': {
        'name': 'Empréstimo Modal',
        'description': 'Acordes vindos do modo paralelo',
        'degrees': ['bVI', 'bVII', 'IVm']
    },
    'Dim': {
        'name': 'Diminuto de Passagem',
        'description': 'Acorde diminuto que liga acordes vizinhos',
        'degrees': ['vii°', '#iv°']
    },
    'Crom': {
        'name': 'Aproximação Cromática',
        'description': 'Acordes meio-tom acima ou abaixo do alvo',
        'degrees': []
    }
}

# Modos para empréstimo modal
MODES = {
    'maior': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
    'menor_natural': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb'],
    'menor_harmonica': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'B'],
    'menor_melodica': ['C', 'D', 'Eb', 'F', 'G', 'A', 'B'],
    'dórico': ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb'],
    'frígio': ['C', 'Db', 'Eb', 'F', 'G', 'Ab', 'Bb'],
    'lídio': ['C', 'D', 'E', 'F#', 'G', 'A', 'B'],
    'mixolídio': ['C', 'D', 'E', 'F', 'G', 'A', 'Bb'],
    'lócrio': ['C', 'Db', 'Eb', 'F', 'Gb', 'Ab', 'Bb']
}

MODE_NAMES_PT = {
    'maior': 'Maior paralela',
    'menor_natural': 'Menor natural paralela',
    'menor_harmonica': 'Menor harmônica paralela',
    'menor_melodica': 'Menor melódica paralela',
    'dórico': 'Modo dórico',
    'frígio': 'Modo frígio',
    'lídio': 'Modo lídio',
    'mixolídio': 'Modo mixolídio',
    'lócrio': 'Modo lócrio'
}

MODE_HARMONY = {
    'maior':      ['maj7', 'm7', 'm7', 'maj7', '7', 'm7', 'm7b5'],
    'menor_natural': ['m7', 'm7b5', 'maj7', 'm7', 'm7', 'maj7', '7'],
    'menor_harmonica': ['m(maj7)', 'm7b5', 'maj7#5', 'm7', '7', 'maj7', 'dim7'],
    'menor_melodica': ['m(maj7)', 'm7', 'maj7#5', '7', '7', 'm7b5', 'm7b5'],
    'dórico':     ['m7', 'm7', 'maj7', '7', 'm7', 'm7b5', 'maj7'],
    'frígio':     ['m7', 'maj7', '7', 'm7', 'm7b5', 'maj7', '7'],
    'lídio':      ['maj7', '7', 'm7', 'm7', 'maj7', 'm7b5', 'm7'],
    'mixolídio':  ['7', 'm7', 'm7', 'maj7', 'm7', 'm7b5', 'maj7'],
    'lócrio':     ['m7b5', 'maj7', 'm7', 'm7', 'maj7', '7', 'm7']
}

chord_pattern = re.compile(
    r'([A-G][#b]?'
    r'(?:m|maj|min|sus|dim|aug|add|M|°)?'
    r'(?:7|9|11|13)?'
    r'(?:\(.*?\))?'
    r'(?:/[A-G][#b]?)?)'
)

def is_minor_chord(chord):
    minor_patterns = [
        'm', 'min', 'm7', 'm9', 'm11', 'm13', 'm6', 'm4', 'm2',
        'm7(5-)', 'm7(b5)', 'dim', '°'
    ]
    return any(pat in chord and 'maj' not in chord for pat in minor_patterns)

def get_chord_quality(chord):
    if is_minor_chord(chord):
        return 'minor'
    return 'major'

def get_chord_root(chord):
    match = re.match(r'^([A-G][#b]?)', chord)
    return match.group(1) if match else None

def get_chord_root_and_quality(chord):
    match = re.match(r'^([A-G][#b]?)', chord)
    if match:
        root = match.group(1)
        quality = get_chord_quality(chord)
        return root, quality
    return None, None

def get_scale(key, mode):
    if mode == 'major':
        idx = MAJOR_SCALE.index(key[0])
        scale = MAJOR_SCALE[idx:] + MAJOR_SCALE[:idx]
        if len(key) > 1:
            scale[0] = key
        return scale, DEGREES_MAJOR
    else:
        idx = MINOR_SCALE.index(key[0])
        scale = MINOR_SCALE[idx:] + MINOR_SCALE[:idx]
        if len(key) > 1:
            scale[0] = key
        return scale, DEGREES_MINOR

def chord_to_degree(chord, key, mode):
    root = get_chord_root(chord)
    scale, degrees = get_scale(key, mode)
    if root in scale:
        degree = degrees[scale.index(root)]
        return degree
    return None

def normalize_note(note):
    replacements = {
        'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#',
        'Ab': 'G#', 'Bb': 'A#'
    }
    return replacements.get(note, note)

def get_interval(note1, note2):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    n1 = notes.index(normalize_note(note1))
    n2 = notes.index(normalize_note(note2))
    return (n2 - n1) % 12

def transpose_note(note, interval):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    n = notes.index(normalize_note(note))
    return notes[(n + interval) % 12]

def transpose_scale(scale, key):
    base_note = 'C'
    interval = get_interval(base_note, key)
    return [transpose_note(note, interval) for note in scale]

def build_harmonic_field(mode_name, key):
    scale = MODES[mode_name]
    harmony = MODE_HARMONY.get(mode_name)
    if not harmony:
        return "Campo harmônico não disponível"
    transposed_scale = transpose_scale(scale, key)
    degrees = DEGREES_MAJOR if mode_name == 'maior' else DEGREES_MINOR
    if len(transposed_scale) < 7:
        transposed_scale += [''] * (7 - len(transposed_scale))
    if len(harmony) < 7:
        harmony += [''] * (7 - len(harmony))
    if len(degrees) < 7:
        degrees += [''] * (7 - len(degrees))
    field = []
    for deg, note, chord_type in zip(degrees, transposed_scale, harmony):
        if note:
            field.append(f"{deg}: {note}{chord_type}")
    return " | ".join(field)

def is_dominant_seventh(chord):
    return '7' in chord and not is_minor_chord(chord)

def is_chromatic_approach(prev_chord, chord, next_chord):
    root = get_chord_root(chord)
    next_root = get_chord_root(next_chord)
    if not root or not next_root:
        return False
    interval = abs(get_interval(root, next_root))
    return interval == 1

def describe_modal_borrowing(chord_root, key, mode):
    if chord_root == key:
        return "-"
    possible_sources = []
    for mode_name, scale in MODES.items():
        transposed_scale = transpose_scale(scale, key)
        if chord_root in transposed_scale:
            possible_sources.append(mode_name)
    if not possible_sources:
        return "Origem não identificada"
    descs = []
    for mode_name in possible_sources:
        nome = MODE_NAMES_PT.get(mode_name, mode_name)
        escala = " ".join(transpose_scale(MODES[mode_name], key))
        campo = build_harmonic_field(mode_name, key)
        descs.append(f"{nome} de {key}: [{escala}] | Campo harmônico: {campo}")
    return " || ".join(descs)

def analyze_chord_function(chord, prev_chord, next_chord, key, mode):
    root = get_chord_root(chord)
    degree = chord_to_degree(chord, key, mode)

    # 1. Função clássica diatônica
    for func_code, func_info in HARMONIC_FUNCTIONS.items():
        if degree in func_info['degrees']:
            return (func_code, func_info['name'], func_info['description'])

    # 2. Segunda Cadencial (II-V-I)
    if degree in HARMONIC_FUNCTIONS['D2']['degrees'] and next_chord and chord_to_degree(next_chord, key, mode) in ['V', 'V7']:
        return ('D2', HARMONIC_FUNCTIONS['D2']['name'], HARMONIC_FUNCTIONS['D2']['description'])

    # 3. Dominante Secundário
    if is_dominant_seventh(chord) and next_chord:
        target_chord = next_chord
        target_root = get_chord_root(target_chord)
        if target_root and get_interval(root, target_root) == 7:
            target_degree = chord_to_degree(target_chord, key, mode)
            return ('Dsec', f"{HARMONIC_FUNCTIONS['Dsec']['name']} (V7/{target_degree})", HARMONIC_FUNCTIONS['Dsec']['description'])

    # 4. Substituto de Dominante (SubV7)
    if is_dominant_seventh(chord) and get_interval(root, key) == 1:
        return ('SubV', HARMONIC_FUNCTIONS['SubV']['name'], HARMONIC_FUNCTIONS['SubV']['description'])

    # 5. Diminuto de Passagem
    if 'dim' in chord.lower() or '°' in chord:
        return ('Dim', HARMONIC_FUNCTIONS['Dim']['name'], HARMONIC_FUNCTIONS['Dim']['description'])

    # 6. Empréstimo Modal
    if degree is None:
        return ('Emp', HARMONIC_FUNCTIONS['Emp']['name'], HARMONIC_FUNCTIONS['Emp']['description'])

    # 7. Aproximação Cromática
    if prev_chord and next_chord and is_chromatic_approach(prev_chord, chord, next_chord):
        return ('Crom', HARMONIC_FUNCTIONS['Crom']['name'], HARMONIC_FUNCTIONS['Crom']['description'])

    return ('Outro', 'Função não identificada', 'Acorde com função harmônica não classificada')

def guess_key(chords):
    if not chords:
        return None, None
    first_chord = chords[0]
    first_root, first_quality = get_chord_root_and_quality(first_chord)
    chord_qualities = {'major': 0, 'minor': 0}
    roots_count = Counter()
    for chord in chords:
        root, quality = get_chord_root_and_quality(chord)
        if root and quality:
            chord_qualities[quality] += 1
            roots_count[root] += 1
    total_chords = len(chords)
    minor_ratio = chord_qualities['minor'] / total_chords if total_chords > 0 else 0
    if first_quality == 'minor' or minor_ratio > 0.3:
        most_common_root = roots_count.most_common(1)[0][0]
        return most_common_root, 'minor'
    return first_root, 'major'

def analyze_cadences(degree_seq, mode, all_chords):
    if mode == 'major':
        authentic = ('V', 'I')
        plagal = ('IV', 'I')
        deceptive = ('V', 'vi')
    else:
        authentic = ('v', 'i')
        plagal = ('iv', 'i')
        deceptive = ('V', 'VI')

    unique_cadences = {
        'Autêntica': set(),
        'Plagal': set(),
        'Interrompida': set(),
        'Meia-cadência': set()
    }

    for i in range(len(degree_seq) - 1):
        pair = (degree_seq[i], degree_seq[i+1])
        chord_pair = f"{all_chords[i]} → {all_chords[i+1]}"
        if pair == authentic:
            unique_cadences['Autêntica'].add(chord_pair)
        elif pair == plagal:
            unique_cadences['Plagal'].add(chord_pair)
        elif pair == deceptive:
            unique_cadences['Interrompida'].add(chord_pair)
        elif degree_seq[i+1] in ('V', 'v'):
            unique_cadences['Meia-cadência'].add(chord_pair)
    return unique_cadences

def analyze_functions_from_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        print(f"\nAnalisando: {data.get('name')} - {data.get('artist')}\n")
        cifra_lines = data.get("cifra", [])

        print("Linhas da cifra:")
        for line in cifra_lines:
            print(f"Linha original: {line}")
        print("\n")

        all_chords = []
        for line in cifra_lines:
            matches = chord_pattern.findall(line)
            if matches:
                all_chords.extend(matches)
        all_chords = [c if isinstance(c, str) else c[0] for c in all_chords]
        if not all_chords:
            print("Nenhum acorde encontrado na cifra.")
            return

        print("Acordes únicos encontrados:")
        unique_chords = sorted(set(all_chords))
        chord_qualities = {'major': 0, 'minor': 0}
        for chord in unique_chords:
            root, quality = get_chord_root_and_quality(chord)
            if quality in chord_qualities:
                chord_qualities[quality] += 1
            print(f"{chord}: {quality}")

        key, mode = guess_key(all_chords)
        if not key:
            print("Não foi possível determinar a tonalidade.")
            return
        print(f"\nTonalidade sugerida: {key} {('maior' if mode == 'major' else 'menor')}")
        print(f"Razão de acordes menores (únicos): {(chord_qualities['minor'] / len(unique_chords)):.2%}")

        print("\nAnálise harmônica (acordes únicos):")
        print("\nAcorde\t\tFunção\t\t\t\tDescrição\t\t\tQualidade\tOrigem do Empréstimo")
        print("-" * 140)

        chord_analysis = {}
        for i, chord in enumerate(all_chords):
            if chord not in chord_analysis:
                prev_chord = all_chords[i-1] if i > 0 else None
                next_chord = all_chords[i+1] if i < len(all_chords)-1 else None
                func_code, func_name, func_desc = analyze_chord_function(
                    chord, prev_chord, next_chord, key, mode)
                root, quality = get_chord_root_and_quality(chord)

                if func_code == 'Emp':
                    borrowing_source = describe_modal_borrowing(root, key, mode)
                else:
                    borrowing_source = "-"

                chord_analysis[chord] = {
                    'function': func_name,
                    'description': func_desc,
                    'quality': quality,
                    'borrowing': borrowing_source
                }

        for chord in sorted(chord_analysis.keys()):
            analysis = chord_analysis[chord]
            print(f"{chord:<12}\t"
                  f"{analysis['function']:<28}\t"
                  f"{analysis['description']:<28}\t"
                  f"{analysis['quality']:<8}\t"
                  f"{analysis['borrowing']}")

        # Sequência de graus para análise de cadências
        degree_seq = [chord_to_degree(chord, key, mode) if chord_to_degree(chord, key, mode) else '-'
                      for chord in all_chords]

        print("\nCadências encontradas:")
        cadences = analyze_cadences(degree_seq, mode, all_chords)
        found_cadences = False
        for cadence_type, chord_pairs in cadences.items():
            if chord_pairs:
                found_cadences = True
                print(f"\n{cadence_type}:")
                for pair in sorted(chord_pairs):
                    print(f"  {pair}")
        if not found_cadences:
            print("Nenhuma cadência típica identificada.")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a API: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    # Exemplo: Garota de Ipanema (Tom Jobim)
    artist = "tom-jobim"
    song = "garota-de-ipanema"
    api_url = f"http://localhost:3000/artists/{artist}/songs/{song}"
    print(f"Consultando API: {api_url}")
    analyze_functions_from_api(api_url)