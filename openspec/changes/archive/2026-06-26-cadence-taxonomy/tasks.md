# Tasks — cadence-taxonomy

## 1. Reescrever analyze_cadences
- [x] 1.1 Detecção por `degree_base` + inversão do baixo (`properties.bass`).
- [x] 1.2 Seis chaves: Perfeita, Autêntica, Imperfeita, Plagal, Meia-cadência, Deceptiva.
- [x] 1.3 Regras: perfeita (V→I fund.), imperfeita (V→I invertido / VII→I),
      plagal (IV→I ou IIm→I), meia (→V), deceptiva (V→não-tônica), autêntica (IV/II→V→I).

## 2. Consumidores
- [x] 2.1 `explain/prompt`: `authentic` lê `Perfeita` + `Autêntica`.
- [x] 2.2 `test_harmony`: chave `Perfeita` para V→I.

## 3. Verificação
- [x] 3.1 Cenários: perfeita (G7→C), imperfeita (G7→C/E e Bm7b5→C),
      plagal (Dm→C), deceptiva (G7→Am, G7→F), meia (Dm→G).
- [x] 3.2 Suíte completa verde.
