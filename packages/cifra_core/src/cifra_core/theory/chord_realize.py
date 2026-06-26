"""Realização de acorde em classes de altura.

A lógica vive agora em `chord_parse` (parsing estruturado por slots, do qual a
realização é derivada). Este módulo é mantido como re-export para compatibilidade
com importações existentes (`from cifra_core.theory.chord_realize import realize`).
"""

from cifra_core.theory.chord_parse import realize, root_pitch_class

__all__ = ["realize", "root_pitch_class"]
