"""Ledger curado de **completude do corpus** (corpus-completeness-quarantine).

A auditoria de 2026-07-02 provou que parte das cifras locais está incompleta:
a conversão PDF→MD do songbook v4 perdeu seções (quebra de página), e algumas
originais têm manifesto independente divergente do corpo. Este ledger registra
**fatos de qualidade do DADO DE ENTRADA** — nunca defeito do motor, nunca placar.

Regras (espelha o padrão `modal_centers`):
- **Evidência obrigatória** — um fato sem evidência não existe (`__post_init__`
  falha na importação).
- **Só fatos** — slug + símbolos declarados-e-ausentes + fonte da evidência;
  NUNCA texto de cifra (fronteira de copyright).
- **Conservador** — dialeto (mesmos pitch-classes) e mojibake são descontados
  ANTES de curar; corpus sem oráculo (v3: fonte deletada, manifesto derivado do
  corpo) NÃO entra — quarentena exige evidência, não suspeita gratuita.
- Gates duros NÃO filtram por completude (invariante por ocorrência vale em
  cifra parcial); consumidores de CURADORIA (centro, adjudicação de trítono)
  usam o status para saber o que é dado parcial.

Verificação anti-drift: `scripts/audit_completeness.py` re-deriva a evidência
com a extração corrente e acusa divergência com este ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

CompletenessStatus = Literal["incomplete", "suspect"]

# Fontes de evidência canônicas.
_V4_ORACLE = (
    "songbook v4 (fonte local, header `Acordes:` do livro) — vocabulário "
    "declarado pela obra, ausente do corpo convertido"
)
_MANIFEST_ORACLE = (
    "manifesto `Acordes Utilizados` independente (fonte original) divergente "
    "do corpo, pós-desconto de dialeto"
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CompletenessFact:
    """Uma música quarentenada: evidência obrigatória, só fatos."""

    slug: str
    status: CompletenessStatus
    missing_declared: tuple[str, ...]  # símbolos declarados e ausentes do corpo
    evidence: str  # fonte da declaração (o oráculo)

    def __post_init__(self) -> None:
        if not self.slug.strip():
            raise ValueError("CompletenessFact.slug vazio.")
        if self.status not in ("incomplete", "suspect"):
            raise ValueError(f"status inválido: {self.status!r}")
        if not self.missing_declared:
            raise ValueError(
                f"{self.slug}: fato de completude sem acordes ausentes não existe."
            )
        if not self.evidence.strip():
            raise ValueError(f"{self.slug}: fato de completude sem evidência não existe.")


def _f(slug: str, status: CompletenessStatus, missing: str, evidence: str) -> CompletenessFact:
    return CompletenessFact(
        slug=slug,
        status=status,
        missing_declared=tuple(missing.split()),
        evidence=evidence,
    )


# ── INCOMPLETE — oráculo forte: o header `Acordes:` do songbook v4 declara
#    acordes ausentes do corpo (truncamento na conversão PDF→MD; irrecuperável
#    sem a fonte original). Auditoria 2026-07-02, pós fix-glued-chord-density,
#    dialeto descontado. ─────────────────────────────────────────────────────
_INCOMPLETE = [
    _f("a-paz", "incomplete", "Cm7(9) Eb7M Gm Gm7(9)", _V4_ORACLE),
    _f("a-tarde", "incomplete", "C7M(9/#11)", _V4_ORACLE),
    _f("ainda-mais-lindo", "incomplete", "Ab7(13)", _V4_ORACLE),
    _f("brisa-do-mar", "incomplete", "Eb7M", _V4_ORACLE),
    _f("beijo-partido", "incomplete", "B7M4", _V4_ORACLE),
    _f("embarcacao", "incomplete", "D7(b9)", _V4_ORACLE),
    _f("estrada-branca", "incomplete", "D7(9) Em7(9)", _V4_ORACLE),
    _f("gaiolas-abertas", "incomplete", "Eb7(13)", _V4_ORACLE),
    _f("luiza", "incomplete", "Em7(b9)", _V4_ORACLE),
    _f(
        "no-cordao-da-saideira",
        "incomplete",
        "Am6 Bb/E Bb7(11) Bm7(11) C#7(#9) C#7(b9) G7(#5)",
        _V4_ORACLE,
    ),
    _f(
        "se-todos-fossem-iguais-a-voce",
        "incomplete",
        "A7(b9) Em7(9) F#m7(b5)",
        _V4_ORACLE,
    ),
    _f("viola-enluarada", "incomplete", "G/A", _V4_ORACLE),
    _f("seu-chopin-desculpe", "incomplete", "D7(b9)", _V4_ORACLE),
    _f("tempo-feliz", "incomplete", "D7(b9) Eb7(9) G6 G7(13)", _V4_ORACLE),
    _f("ultima-forma", "incomplete", "Em7", _V4_ORACLE),
]

# ── SUSPECT — oráculo fraco: manifesto independente diverge do corpo e não há
#    fonte para confirmar truncamento (pode ser vocabulário de seção não
#    transcrita, ex. intro/solo). Auditoria 2026-07-02, pós-fix, dialeto
#    descontado. ────────────────────────────────────────────────────────────
_SUSPECT = [
    _f("demais", "suspect", "F#7(b13) G6", _MANIFEST_ORACLE),
    _f("deus-brasileiro", "suspect", "C7M", _MANIFEST_ORACLE),
    _f("dindi", "suspect", "D7(13)", _MANIFEST_ORACLE),
    _f("discussao", "suspect", "Dm7(9) E7(#5)", _MANIFEST_ORACLE),
    _f("enquanto-a-tristeza-nao-vem", "suspect", "Cm9", _MANIFEST_ORACLE),
    _f("eu-sei-que-vou-te-amar", "suspect", "Abm6 Am6", _MANIFEST_ORACLE),
    _f("falando-de-amor", "suspect", "E7(13)", _MANIFEST_ORACLE),
    _f("feio-nao-e-bonito", "suspect", "C6/9 D7(13) Gb7", _MANIFEST_ORACLE),
    _f("influencia-do-jazz", "suspect", "G7M(#11)", _MANIFEST_ORACLE),
    _f("nos-e-o-mar", "suspect", "Ab7(9)", _MANIFEST_ORACLE),
    _f("razao-de-viver", "suspect", "D7M(9)", _MANIFEST_ORACLE),
    _f("retrato-em-branco-e-preto", "suspect", "Gm7", _MANIFEST_ORACLE),
    _f("sonho-de-maria", "suspect", "Bb7M", _MANIFEST_ORACLE),
]

COMPLETENESS_LEDGER: Mapping[str, CompletenessFact] = {
    f.slug: f for f in (*_INCOMPLETE, *_SUSPECT)
}


def completeness_for(slug: str) -> str:
    """Status de completude de uma música: 'complete' (default), 'suspect' ou
    'incomplete'. Ausente do ledger = completo (quarentena exige evidência)."""
    fact = COMPLETENESS_LEDGER.get(slug)
    return fact.status if fact else "complete"
