> **STATUS: BLOCKED BY DATA — NOT IMPLEMENTED (2026-06-28).** The apply step ran the
> zero-regression trava first (live probe of the four `chediak`-tier modal songs) and it
> invalidated this proposal's core premise: the Chediak modal center is **not encoded in
> the Cifra Club chords**. See [PROBE-FINDINGS.md](./PROBE-FINDINGS.md). Arrastão's finalis
> is unrecoverable (`_central_pc`→Mi, ends on `D7+`, Lá only tied-2nd); Procissão's Dó
> appears 1×/80; Upa Neguinho and Pra Não Dizer already detect the center correctly (only
> the *mode name* diverges — that is `modal_coloring`'s job). The arbitration is blocked by
> **data, not mechanism** — it needs a curated modal corpus whose chords encode the finalis.
> The design and metric stand as reasoning; reopen when the corpus exists. Per the project's
> Golden Rule (Cifra Club = raw input; algorithm + Chediak = ground truth), a detection
> target is only implementable if the raw data encodes it.

## Why

Pieces whose true center is **modal** (Arrastão → Lá dórico; Chediak Vol. I p. 125)
are invisible to every center mechanism we have. The K-S detector and the Cifra Club
annotation read the **tonal axis** (Arrastão → Ré maior, the V of the real finalis);
the 3b quality gate only fires on a **functional dominant** resolution, which a modal
piece lacks *by construction*; and the `center_accuracy` metric runs **only** over the
dominant-verified subset, so modal pieces sit permanently in quarantine — their center
is never even measured. The modal-coloring overlay already names the *flavor* but
explicitly refuses to re-center. The center itself is the gap this change closes.

The two blockers the ROADMAP records are now addressable: (a) a **principled
modal↔tonal discriminator** — Chediak's own criterion, *absence of a functional
dominant* + a *characteristic modal cadence resolving to the finalis* (pp. 121-123),
which we can read off real chords by reusing `modal_coloring` and the modal library;
and (b) a **transposition-safe metric** — the modal center expressed degree-relative to
the Cifra Club key in one frame, never by absolute Chediak−CC pitch subtraction (the
trap that breaks Pra Não Dizer: Chediak Mi vs CC Fá).

## What Changes

- Add a **modal-center arbitration overlay**: a strictly additive, ultraconservative
  annotation that names a modal center (finalis + church mode) **distinct from the
  tonal key**, only when (1) no functional dominant resolves to either the tonal tonic
  or the candidate finalis, (2) a characteristic modal cadence (bVII→I, IV→i, bII→i)
  resolves onto the finalis, and (3) the bass-centric finalis differs from the K-S
  tonal tonic. Reuses `modal_coloring` evidence, `modal.detect_mode`/`_central_pc`, and
  `chediak_structural_gold.verify_tonal_center`.
- **Guardrail (inviolable):** `detect_key` is **not** touched. The overlay never alters
  the key, mode, scale degrees, harmonic functions, cadences, or the four Cifra-Club
  metrics. It emits a separate `modal_center` field (absent by default), exactly like
  `modal_coloring`.
- Add a **degree-relative modal-center metric** (`modal_center_accuracy`) that
  **activates the existing `chediak` provenance tier** (the modal facts already
  committed but deferred — Arrastão A dorian p.125, etc.). The gold offset is a
  **curated degree fact** (the finalis's degree within the Cifra Club key, per
  Chediak's functional reading), compared in the same `(detected − cc_key) % 12` frame
  as the detected finalis — never an absolute cross-source subtraction. The existing
  tonal `center_accuracy` (over the `verified` tier) and the four Cifra-Club metrics
  stay **identical**.
- Report the modal center in analysis output (lazy section, visible degradation) and in
  `scripts/key_baseline.py` (new modal-center line, measured live against the baseline).

## Capabilities

### New Capabilities
- `modal-center-arbitration`: the conservative overlay that arbitrates a modal center
  (finalis + church mode) for a piece, distinct from and additive to the tonal key,
  gated on absence-of-functional-dominant + modal-cadence-to-finalis, never re-centering
  the tonal analysis.

### Modified Capabilities
- `key-accuracy-evaluation`: add a degree-relative `modal_center_accuracy` metric that
  activates the existing `chediak` provenance tier, whose structural offset is a curated
  degree fact (not absolute pitch subtraction); the four Cifra-Club metrics and the
  tonal `center_accuracy` (over the `verified` tier) remain unchanged.

## Impact

- **New code:** `packages/harmonic_analysis/src/harmonic_analysis/domain/modal_center.py`
  (arbitration overlay), tests `test_modal_center.py`.
- **Modified code:** `validation/key_accuracy.py` (modal center metric + tier);
  `services/analysis_service.py` (new lazy `modal_center` section);
  `scripts/chediak_structural_gold.py` (modal tier with curated degree offsets +
  `chediak-modal` provenance); `scripts/key_baseline.py` (report the modal-center line).
- **Reuses unchanged:** `modal_coloring.detect_coloring`, `modal.detect_mode` /
  `_central_pc` / `modal_cadences`, `chediak_structural_gold.verify_tonal_center`.
- **Risk gate:** zero regression of the four Cifra-Club metrics and the tonal
  `center_accuracy` is inviolable; every recalibration is measured live against the
  baseline (the rule that already barred two bad ships). `detect_key` is unchanged.
