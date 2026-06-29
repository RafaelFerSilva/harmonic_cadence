from typing import Dict, List

# Escalas e graus básicos
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
    "Daux": {
        "name": "Dominante Auxiliar",
        "description": "Dominante de um acorde de empréstimo modal, resolvendo "
        "5ª justa abaixo (Chediak p.99): o alvo é emprestado, não diatônico",
        "degrees": [],
    },
    "Dext": {
        "name": "Dominante Estendido",
        "description": "Dominante que resolve em OUTRO dominante por 4ª justa "
        "ascendente (ciclo de quintas); pertence à cadeia, não à tonalidade, "
        "logo não leva número romano (Chediak XXVIII(a), pp.107-108). "
        "Escala-acorde: mixolídio",
        "degrees": [],
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

PROGRESSIONS = [
    # Progressões clássicas
    ("II", "V", "I"),  # IIm-V-I - Fundamental no jazz e MPB
    ("I", "V", "VI", "IV"),  # Progressão "The Beatles" (I-V-VI-IV)
    ("I", "IV", "V"),  # Progressão básica I-IV-V
    ("I", "V7/II", "II", "V", "I"),  # Progressão com dominante secundário
    # Progressões de cadência
    ("V", "I"),  # Cadência autêntica
    ("IV", "V", "I"),  # Cadência plena
    ("II", "V"),  # Cadência de engano para II-V
    ("V", "VI"),  # Cadência de engano - maior
    ("v", "VI"),  # Cadência de engano - menor
    # Progressões do Jazz
    ("I", "VI", "II", "V"),  # Turnaround básico
    ("III", "VI", "II", "V"),  # Turnaround começando no III
    ("I", "I7", "IV", "IV#dim"),  # Início de Rhythm Changes
    ("I", "#Idim", "II", "V"),  # Aproximação cromática para o II
    ("I", "I7", "IV", "IVm"),  # Mudança maior-menor
    ("IIIm", "VIm", "IIm", "V"),  # Variação diatônica do Turnaround
    ("Imaj7", "VIm7", "IIm7", "V7"),  # Turnaround com sétimas
    ("IIm7", "V7", "IIm7", "V7"),  # Turnaround básico repetido
    ("I7", "IV7", "V7"),  # Progressão blues com sétimas
    ("I9", "II9", "V9"),  # Progressão de acordes com nona
    # Progressões da Bossa Nova/MPB
    ("Im", "VII", "VIm", "V"),  # Comum em Tom Jobim
    ("I", "I7", "IV", "IVm"),  # Movimento cromático interno
    ("I", "III", "IV", "V"),  # Movimento ascendente diatônico
    ("I", "bVII", "IV", "V"),  # Empréstimo modal (mixolídio)
    ("II", "bII", "I"),  # Aproximação cromática (Napolitano)
    # Progressões do Choro
    ("I", "I7", "IV", "IVm", "I", "V7"),  # Padrão típico do choro
    ("I", "bIIIdim", "IIm", "V7"),  # Passagem cromática típica
    ("I", "bVI", "bVII", "V7"),  # Progressão com empréstimo modal
    ("I", "V7/II", "II", "V7/V", "V"),  # Ciclo de quintas expandido
    # Progressões do Samba
    ("I", "IIm", "bIII", "II"),  # Modulação comum no samba
    ("Im", "IVm", "V7", "Im"),  # Padrão em tons menores
    ("I", "VI", "IIm", "V7"),  # Variação do turnaround no samba
    ("I", "bVII", "bIII", "bVI", "II", "V"),  # Base de muitos sambas modernos
    # Progressões de Forró/Baião/Xote
    ("I", "IV", "I", "V"),  # Base do baião tradicional
    ("I", "bVII", "IV", "I"),  # Modo mixolídio comum no nordeste
    ("I", "bIII", "IV", "V"),  # Influência modal nordestina
    # Progressões de Sertanejo
    ("I", "bVII", "bVI", "V"),  # Sertanejo com influência modal
    ("I", "IV", "I", "V"),  # Base de muitas músicas sertanejas
    ("I", "bVII", "I", "IV"),  # Empréstimo modal no sertanejo
    # Progressões de Axé
    ("I", "IV", "V", "IV"),  # Comum em marchinhas/axé
    ("I", "bIII", "IV", "V"),  # Influência modal no axé
    # Progressões por Ciclos
    ("I", "IV", "VII", "III"),  # Ciclo de quintas descendente
    ("I", "bVII", "bVI", "bV"),  # Ciclo de quintas em modo menor
    ("I", "IV", "VII", "III", "VI", "II", "V"),  # Ciclo de quintas completo
    ("I", "III", "V", "VII"),  # Movimento por terça ascendente
    ("I", "bIII", "bV", "bVII"),  # Movimento por terça descendente
    ("I", "V", "II", "VI"),  # Movimento por quinta ascendente
    ("I", "IV", "VII", "III"),  # Movimento por quinta descendente
    # Progressões de Modulação
    ("I", "bIII", "bVI", "V/bVI"),  # Modulação para o relativo menor
    ("I", "I7", "IV", "IV7", "VII", "VII7", "III"),  # Modulação por ciclo de quintas
    ("I", "#Idim", "II", "II7", "V/V", "V"),  # Modulação por aproximação cromática
    ("I", "bII", "V/bII", "bII"),  # Modulação napolitana
    # Progressões com Subdominante Menor
    ("I", "IVm", "V"),  # Subdominante menor clássica
    ("I", "IVm6", "V"),  # Subdominante menor com sexta
    ("Imaj7", "IVm6", "V7"),  # Variação jazz com sétima
    # Progressões Modais
    ("Im", "bVII", "bVI", "V"),  # Progressão dórica
    ("I", "bVII", "I"),  # Progressão mixolídia (forró/baião)
    ("Im", "bVI", "bVII", "Im"),  # Progressão eólia
    ("I", "II", "I"),  # Progressão lídia (rara mas presente em MPB)
    ("i", "bIII", "iv", "v"),  # Progressão eólica completa
    ("I", "bVI", "bVII", "V"),  # Empréstimo do modo mixolídio
    # Progressões com Substitutos Tritonais
    ("I", "bII7", "I"),  # Dominante substituto
    ("II", "bII7", "I"),  # Napolitano com substituto tritonal
    ("I", "IV", "bV7", "I"),  # Substituto do V7
    # Progressões de Contorno Cromático
    ("I", "I+", "IV", "IVm"),  # Linha cromática ascendente
    ("I", "I#", "IV", "IVm"),  # Notação alternativa para linha cromática
    ("I", "Imaj7", "I7", "IV", "IVm"),  # Movimento cromático na terça
    ("I", "#Im7b5", "IIm", "II#dim", "IIIm"),  # Linha cromática complexa
    ("I", "bVII", "V"),  # Aproximação cromática para o V
    # Progressões circulares (Coltrane)
    ("I", "bIII", "bV", "bVII"),  # Ciclo de terças maiores
    ("I", "III", "V", "VII"),  # Ciclo de terças diatônico
    ("I", "bVI", "bIII", "VII"),  # Giant Steps simplificado
    # Progressões com pedal
    ("I", "I/I", "IV/I", "V/I"),  # Acorde pedal na tônica
    ("I", "V/V", "I/V", "IV/V"),  # Acorde pedal na dominante
    # Progressões com Linha de Baixo Descendente
    ("I", "I/VII", "I/VI", "I/V"),  # Baixo descendente diatônico
    ("I", "VIIm7b5", "bVIImaj7", "VIm7"),  # Jazz com baixo cromático
    ("I", "VII", "VIIb", "VI"),  # Linha cromática pura
    # Progressões Avançadas do Jazz Moderno
    ("Imaj7", "bIIIm7", "bVImaj7", "bIImaj7"),  # Coltrane Changes
    ("I", "bV7", "bIImaj7", "IV7"),  # Substitutos não convencionais
    ("Imaj7", "#IVm7b5", "VII7b9", "IIIm"),  # Modulação não preparada
]

FUNCTION_PROGRESSIONS = [
    # Funções básicas
    ("T", "SD", "D", "T"),  # Ciclo básico completo
    ("T", "D", "T"),  # Ciclo básico simplificado
    ("T", "SD", "T"),  # Movimentação plagal
    # Funções com Variações
    ("T", "Tp", "SD", "D"),  # Tônica → Tônica paralela (relativa)
    ("T", "S", "Sp", "D"),  # Subdominante → Subdominante paralela
    ("T", "D", "Dp", "T"),  # Dominante → Dominante paralela
    # Funções com Preparações
    ("T", "SD", "(SG)", "D", "T"),  # Com Subdominante da Dominante
    ("T", "D/SD", "SD", "D", "T"),  # Com Dominante da Subdominante
    # Funções de Tonicização
    ("T", "D/VI", "VI", "D", "T"),  # Tonicização da relativa (VI)
    ("T", "D/V", "D", "T"),  # Tonicização da dominante
    ("T", "D/II", "II", "D", "T"),  # Tonicização do II
    # Funções em Modulação
    ("T", "D/SR", "SR", "D/DR", "DR"),  # Modulação para região da Subdominante
    ("T", "D/TR", "TR"),  # Modulação para região da Tônica Relativa
    # Funções de Empréstimo Modal
    ("T", "bSD", "D", "T"),  # Subdominante menor emprestada
    ("T", "bSR", "D", "T"),  # Subdominante relativo menor
    ("T", "bTR", "D", "T"),  # Tônica relativa bemol
    # Funções com Substitutos
    ("T", "sD", "T"),  # Dominante substituta
    ("T", "SD", "sD", "T"),  # Com dominante substituta após subdominante
    # Funções Mistas
    ("T", "(TR-SD)", "D", "T"),  # Acordes com função dupla
    ("T", "(DR-SD)", "D", "T"),  # Dominante-Subdominante
]

PROGRESSION_CATEGORIES = {
    # Progressões clássicas
    "II-V-I": "Cadência jazz",
    "V-I": "Cadência autêntica",
    "IV-V-I": "Cadência plena",
    "I-IV-V": "Progressão básica",
    "I-V-VI-IV": "Progressão circular pop",
    "I-VI-IV-V": "Progressão circular",
    "I-V7/II-II-V-I": "Progressão regional (samba/choro)",
    # Turnarounds
    "I-VI-II-V": "Turnaround jazz",
    "III-VI-II-V": "Turnaround jazz variante",
    "IIIm-VIm-IIm-V": "Turnaround diatônico",
    "Imaj7-VIm7-IIm7-V7": "Turnaround com sétimas",
    "IIm7-V7-IIm7-V7": "Turnaround repetido",
    # Cadências
    "II-V": "Semicadência",
    "V-VI": "Cadência de engano (maior)",
    "v-VI": "Cadência de engano (menor)",
    # Blues e Jazz
    "I7-IV7-V7": "Progressão blues",
    "I9-II9-V9": "Jazz com tensões",
    "I-I7-IV-IV#dim": "Rhythm Changes (início)",
    # Progressões modais
    "Im-bVII-bVI-V": "Progressão dórica",
    "I-bVII-I": "Progressão mixolídia",
    "Im-bVI-bVII-Im": "Progressão eólia",
    "I-II-I": "Progressão lídia",
    "i-bIII-iv-v": "Progressão eólica completa",
    "I-bVI-bVII-V": "Mixolídio emprestado",
    # Progressões regionais brasileiras
    "I-IV-I-V": "Baião/Sertanejo básico",
    "I-bVII-IV-I": "Forró nordestino (mixolídio)",
    "I-bIII-IV-V": "Modal nordestina",
    "I-IV-V-IV": "Axé/marchinha",
    "I-bVII-bVI-V": "Sertanejo modal",
    "I-bVII-I-IV": "Sertanejo com empréstimo",
    "Im-VII-VIm-V": "Bossa Nova (Jobim)",
    "I-I7-IV-IVm": "MPB cromática",
    "I-I7-IV-IVm-I-V7": "Choro tradicional",
    "I-bIIIdim-IIm-V7": "Choro cromático",
    # Ciclos
    "I-IV-VII-III": "Ciclo de quintas descendente",
    "I-bVII-bVI-bV": "Ciclo de quintas menor",
    "I-IV-VII-III-VI-II-V": "Ciclo de quintas completo",
    "I-III-V-VII": "Ciclo de terças ascendente",
    "I-bIII-bV-bVII": "Ciclo de terças descendente",
    # Modulações
    "I-bIII-bVI-V/bVI": "Modulação para relativo menor",
    "I-I7-IV-IV7-VII-VII7-III": "Modulação por ciclo de quintas",
    "I-bII-V/bII-bII": "Modulação napolitana",
    # Contornos cromáticos
    "I-I+-IV-IVm": "Linha cromática ascendente",
    "I-I#-IV-IVm": "Linha cromática ascendente (alt.)",
    "I-Imaj7-I7-IV-IVm": "Cromatismo na terça",
    # Substitutos e empréstimos
    "I-IVm-V": "Subdominante menor",
    "I-IVm6-V": "Subdominante menor com sexta",
    "I-bII7-I": "Dominante substituto",
    "I-IV-bV7-I": "Substituto tritonal",
    # Progressões avançadas
    "Imaj7-bIIIm7-bVImaj7-bIImaj7": "Coltrane Changes",
    "I-bV7-bIImaj7-IV7": "Substitutos jazz moderno",
    "I-bVI-bIII-VII": "Giant Steps simplificado",
    # Progressões funcionais básicas
    "T-SD-D-T": "Ciclo funcional completo",
    "T-D-T": "Ciclo funcional simplificado",
    "T-SD-T": "Ciclo plagal",
    # Progressões funcionais avançadas
    "T-bSD-D-T": "Ciclo com subdominante menor",
    "T-sD-T": "Ciclo com dominante substituta",
    "T-D/TR-TR": "Modulação para tônica relativa",
}
