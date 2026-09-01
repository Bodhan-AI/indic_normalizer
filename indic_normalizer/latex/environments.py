"""Speaking of LaTeX environments (matrix / cases / align families)."""

from __future__ import annotations


MATRIX_ENVS = {
    "matrix", "pmatrix", "bmatrix", "Bmatrix", "smallmatrix", "array",
}
DET_ENVS = {"vmatrix", "Vmatrix"}
CASE_ENVS = {"cases", "dcases"}
ALIGN_ENVS = {
    "align", "align*", "aligned", "alignat", "alignat*", "equation",
    "equation*", "split", "gather", "gather*", "multline", "multline*",
    "eqnarray", "eqnarray*", "flalign", "flalign*", "displaymath",
}


def speak_environment(node, speaker):
    """Render an environment Node to spoken English using ``speaker``.

    ``speaker`` is an object exposing ``.speak(node) -> str`` and
    ``.numword(int) -> str``.
    """
    name = node.name
    srows = []
    for row in node.rows:
        cells = [speaker.speak(cell).strip() for cell in row]
        srows.append(cells)

    if name in CASE_ENVS:
        parts = [" ".join(c for c in row if c).strip() for row in srows]
        parts = [p for p in parts if p]
        return "; ".join(parts)

    if name in ALIGN_ENVS:
        parts = [" ".join(c for c in row if c).strip() for row in srows]
        parts = [p for p in parts if p]
        return ". ".join(parts)

    # Matrix-like
    label = "determinant" if name in DET_ENVS else "matrix"
    body_rows = []
    idx = 0
    for row in srows:
        text = " ".join(c for c in row if c).strip()
        if text == "" and len(srows) > 1:
            # skip trailing empty row produced by a final "\\"
            continue
        idx += 1
        body_rows.append("row " + speaker.numword(idx) + " " + text)
    if not body_rows:
        return label
    return label + ", " + ", ".join(r.rstrip() for r in body_rows)
