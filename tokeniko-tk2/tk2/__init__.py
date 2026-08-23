"""tokeniko 2 — the body.

The import name is `tk2` and not `lib`: tk1's package is `lib`, both live in the same virtualenv
during the translation, and a collision between the two generations is the one bug that would be
impossible to read.

The body is an INTERPRETER of the db (body req. 2): this package holds only the irreducible math —
the evaluator, the loop, the operators — and changes only when the math changes. Everything that is
knowledge, parameter or policy lives in rows.
"""
