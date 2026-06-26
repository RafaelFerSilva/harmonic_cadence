## 1. JSON report (`presentation/reports/json.py`)

- [x] 1.1 Add a graceful-include helper (skip `None`/empty/absent sections)
- [x] 1.2 Emit depth sections: `tonal_regions`, `modal_analysis`, `roman_numerals`, `voice_leading`, `chord_scales`
- [x] 1.3 Emit intelligence sections: `functional_parse`, `reharmonizations`, `explanation`
- [x] 1.4 Keep existing keys (metadata, statistics, harmonic_analysis, analysis_progression, function_stats, cadences, raw_data) unchanged

## 2. Markdown report (`presentation/reports/markdown.py`)

- [x] 2.1 Explanation paragraph + key/mode header unchanged
- [x] 2.2 Roman-numeral table; tonal-regions list
- [x] 2.3 Voice-leading (bass line) + chord-scales/tensions lists
- [x] 2.4 Functional-parse table (chord / function / confidence); reharmonizations list (original → result + technique + rationale), capped with a truncation note
- [x] 2.5 Graceful omission of absent/empty sections

## 3. HTML report (`presentation/reports/html.py`)

- [x] 3.1 Add equivalent sections (explanation, Roman numerals, reharmonizations, depth) reusing the existing template style
- [x] 3.2 Graceful omission of absent/empty sections; layout not broken

## 4. Tests & validation

- [x] 4.1 JSON: depth + intelligence sections present for a rich piece; omitted for a tonal/empty piece
- [x] 4.2 Markdown: explanation + reharmonizations + Roman numerals present; existing sections preserved
- [x] 4.3 HTML: explanation + new sections present; report generated without error
- [x] 4.4 Backward-compatibility: statistics, harmonic-analysis table, cadences still rendered
- [x] 4.5 Full suite green across packages; ruff clean
