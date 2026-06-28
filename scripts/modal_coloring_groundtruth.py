"""Ground-truth da coloração modal — ancorado em Chediak (árbitro do projeto).

Fatos `(artista, música, modo_chediak, página, papel_v1)` — NÃO as cifras (re-raspadas,
dentro da fronteira de copyright, igual ao `key_baseline.GOLD`). O modo e a página são
a classificação do próprio Chediak (Vol. I, "Exemplos de músicas populares em alguns
modos", pp. 125-127); o `papel_v1` diz o que o detector de coloração v1
(mixolídio sobre maior via bVII/v-menor; frígio sobre menor via bII→i estrutural)
deve fazer, COM a divergência documentada quando o dado raspado difere de Chediak.

Use para validação ao vivo (rede), não como fixture de teste offline — os testes
determinísticos usam progressões sintéticas por modo (ver test_modal_coloring).
"""

# Classificações de Chediak (pp. 125-127) — o gold autoritativo.
# papel_v1: "positivo" (deve disparar), "controle" (deve silenciar),
#           "fora-v1" (modo não coberto pela v1), "divergência" (gold≠detector, explicada)
CHEDIAK_GOLD = [
    # (artista, música, modo, página, papel_v1, nota)
    ("Milton Nascimento", "Cravo e Canela", "ionian", 125, "controle",
     "iônico = maior; sem coloração esperada (silêncio)"),
    ("Edu Lobo", "Arrastao", "dorian", 125, "divergência",
     "Lá dórico (Chediak). detect_key ancora em Ré maior e lê superfície mixolídia "
     "(bVII→I); dórico↔mixolídio compartilham coleção, separá-los exige detecção de "
     "centro modal (3b, bloqueado). v1 não mira dórico."),
    ("Edu Lobo", "Upa Neguinho", "mixolydian", 126, "positivo",
     "Ré mixolídio por Vm7 (Am7), SEM bVII. Exige o 2º sinal mixolídio (v menor); "
     "só-bVII perderia esta música."),
    ("Gilberto Gil", "Procissao", "mixolydian", 126, "divergência",
     "Dó mixolídio com Bb→C explícito em Chediak; a cifra raspada veio tonalizada "
     "(sem Bb) → silêncio fiel ao arranjo, não a Chediak. Divergência de arranjo."),
    ("Geraldo Vandre", "Pra Nao Dizer Que Nao Falei das Flores", "aeolian", 127,
     "controle",
     "Mi eólio = menor natural; Chediak: cadências eólias são subdominantes menores "
     "tonais comuns → silêncio esperado (valida o default tonal do menor)."),
    ("Caetano Veloso", "Gravidade", "lydian_b7", 127, "fora-v1",
     "Dó lídio b7 (I7/II7); modo sintético fora do escopo da v1."),
]

# Positivos verificados por DADO (não exemplificados por Chediak, mas teoricamente
# ancorados nele): a coloração harmônica de superfície aparece de fato na cifra raspada.
DATA_VERIFIED = [
    ("Edu Lobo", "Ponteio", "mixolydian", "positivo",
     "E maior; bVII→I forte (×24 na varredura). Superfície mixolídia inequívoca."),
    ("Baden Powell", "Canto de Ossanha", "phrygian", "positivo",
     "D menor; bII→i estrutural (×22). Frígio dos afro-sambas; Chediak não dá exemplo "
     "frígio, mas define o modo e a cadência bII→i (pp. 122-125)."),
]

# Controles negativos — eólias/bossa que o detector velho marcava falso-frígio.
# Devem SILENCIAR sob a regra ancorada (mixo só-maior; frígio exige bII→i ≥2).
NEGATIVE_CONTROLS = [
    ("Tom Jobim", "Wave", "menor — sem coloração"),
    ("Tom Jobim", "Corcovado", "menor — bII pontual é napolitano/SubV, não frígio"),
    ("Tom Jobim", "Insensatez", "menor — bII sem cadência estrutural"),
    ("Chico Buarque", "Construcao", "menor — bII do baixo cromático, não frígio"),
]
