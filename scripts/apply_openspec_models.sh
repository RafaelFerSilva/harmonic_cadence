#!/usr/bin/env bash
# apply_openspec_models.sh
#
# Reapplies the model-by-phase strategy to OpenSpec's Claude Code skills.
# OpenSpec regenerates these SKILL.md files from its CLI, which drops any
# `model:`/`effort:` frontmatter. Run this after `openspec` (re)generates the
# .claude/skills/openspec-* adapters in a project.
#
# Strategy: spec skills (propose, explore) -> Opus + high effort; build/admin
# skills inherit the global default (Sonnet + medium). See the memory note
# "model-by-phase-strategy".
#
# Usage:
#   scripts/apply_openspec_models.sh [PROJECT_ROOT]   # default: current dir
#
# Idempotent: skips a skill if it already declares `model:`.

set -euo pipefail

ROOT="${1:-.}"
SKILLS_DIR="$ROOT/.claude/skills"

# Spec-phase skills that should escalate to the expensive, high-effort tier.
SPEC_SKILLS=("openspec-propose" "openspec-explore")

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "error: $SKILLS_DIR not found (run from a project with OpenSpec skills)" >&2
  exit 1
fi

applied=0
for skill in "${SPEC_SKILLS[@]}"; do
  f="$SKILLS_DIR/$skill/SKILL.md"
  if [[ ! -f "$f" ]]; then
    echo "skip: $skill (no SKILL.md)"
    continue
  fi
  if grep -qE '^model:' "$f"; then
    echo "ok:   $skill already has a model: override — left untouched"
    continue
  fi
  # Insert `model:`/`effort:` right after the `description:` line in the
  # YAML frontmatter (the first `description:` is the frontmatter one).
  if ! grep -qE '^description:' "$f"; then
    echo "warn: $skill has no description: line — skipped" >&2
    continue
  fi
  awk '
    BEGIN { done = 0 }
    /^description:/ && !done { print; print "model: opus"; print "effort: high"; done = 1; next }
    { print }
  ' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
  echo "set:  $skill -> model: opus + effort: high"
  applied=$((applied + 1))
done

echo "done: $applied skill(s) updated under $SKILLS_DIR"
