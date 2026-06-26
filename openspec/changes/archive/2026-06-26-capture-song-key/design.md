# Design — Capturar o tom da música (Cifra Club)

## O dado já está lá, sendo jogado fora

```python
cifra_tom_elem = soup.find(id="cifra_tom")
if cifra_tom_elem:
    cifra_tom_elem.decompose()   # acha o tom e... descarta
```

A extração acontece **antes** desse descarte, do `soup` original do
`scrape_cifra` (o `decompose` vive numa cópia parseada dentro de
`clean_cifra_html`).

## Extração

O `#cifra_tom` costuma exibir algo como "Tom: G" / "Tom: Am". Extraímos o
primeiro token de nota:

```python
def _extract_tom(self, soup) -> str:
    elem = soup.find(id="cifra_tom")
    if not elem:
        return ""
    m = re.search(r"[A-G][#b]?m?", elem.get_text(" ", strip=True))
    return m.group(0) if m else ""
```

Heurística simples e defensiva (o tom é "prata" — fonte colaborativa). Casos como
capotraste (tom soante ≠ tom escrito) ficam como ruído conhecido, que o harness
da Fase A vai medir, não esconder.

## `key` da fonte ≠ `key` detectado

O `Cifra.key` é o tom **anotado pela fonte** (entrada); o `result["key"]` da
análise é o tom **detectado** (saída). Vivem em objetos diferentes — o harness os
compara (anotação vs detecção). Mantemos o nome `key` em cada um por ser natural
(uma música *tem* um tom); a confusão é nula porque não coexistem no mesmo dict.

## Não-objetivos

- Harness de acurácia (próxima change).
- Normalizar/validar o tom (maiúsculo/relativa); é a fonte "prata".
