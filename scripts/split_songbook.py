"""Separa um songbook markdown em `cifras/<slug>.md`, um arquivo por música.

Alimenta a frente #8 (ampliar o corpus). O fonte (songbook completo) é **copyright** e fica
gitignored; a saída (`cifras/*.md`) também é local/gitignored — só os FATOS (regra + música)
entram na análise, nunca o texto do livro. Esta ferramenta é só a transformação de formato.

Fonte esperado (formato do songbook):
    ### Título
    _COMPOSITORES_
    ```text
    <bloco de cifra alinhada>
    ```

Saída (formato do corpus, idêntico às cifras existentes):
    ## <a name="slug"></a>🎼 Título

    **Compositores:** ...

    **Acordes Utilizados:** `X`, `Y`, ...    ← whitelist de raiz-nua, gerada pela extração

    ```
    <bloco de cifra>
    ```

Uso:  uv run python scripts/split_songbook.py <fonte.md> [--write]
      (sem --write = dry-run; nunca sobrescreve uma cifra já existente)
"""

import os
import re
import sys

from cifra_core import cifra_from_text, extract_chords_from_lines, slugify

OUT_DIR = "cifras"

_SONG = re.compile(r"^### (.+?)\n(.*?)(?=^### |\Z)", re.M | re.S)
_COMPOSERS = re.compile(r"^_(.+?)_\s*$", re.M)
_FENCE = re.compile(r"```[a-zA-Z]*\n(.*?)```", re.S)


def _manifest(block: str) -> list[str]:
    """Acordes únicos (ordem de aparição) do bloco, pelo caminho único de extração, sem whitelist.

    Espelha o que o baseline vê; o resultado vira o header `Acordes Utilizados`, que na releitura
    confirma as raízes-nuas ambíguas (`A`-`G`)."""
    cifra = cifra_from_text(block)
    seen: dict[str, None] = {}
    for sym in extract_chords_from_lines(cifra.cifra):
        seen.setdefault(sym, None)
    return list(seen)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("uso: split_songbook.py <fonte.md> [--write]")
        raise SystemExit(2)
    src, write = args[0], "--write" in sys.argv
    text = open(src, encoding="utf-8").read()

    made = skipped = 0
    for title, body in _SONG.findall(text):
        title = title.strip()
        mfence = _FENCE.search(body)
        if not mfence:
            continue  # bloco sem cifra (ex.: índice) — não é música
        block = mfence.group(1).rstrip("\n")
        chords = _manifest(block)
        if not chords:
            print(f"  [SKIP sem acordes] {title}")
            continue
        slug = slugify(title)
        path = os.path.join(OUT_DIR, f"{slug}.md")
        if os.path.exists(path):
            print(f"  [SKIP já existe] {slug}.md")
            skipped += 1
            continue
        mcomp = _COMPOSERS.search(body)
        composers = mcomp.group(1).strip() if mcomp else ""
        manifest_str = ", ".join(f"`{c}`" for c in chords)
        out = (
            f'## <a name="{slug}"></a>🎼 {title}\n\n'
            f"**Compositores:** {composers}\n\n"
            f"**Acordes Utilizados:** {manifest_str}\n\n"
            f"```\n{block}\n```\n"
        )
        if write:
            with open(path, "w", encoding="utf-8") as f:
                f.write(out)
        made += 1
        print(f"  [OK] {slug}.md  ({len(chords)} acordes){'' if write else ' (dry)'}")

    verb = "Escritos" if write else "Simulados"
    print(f"\n{verb}: {made}  (pulados/existentes: {skipped})")
    if not write:
        print("(dry-run — rode com --write para gravar)")


if __name__ == "__main__":
    main()
