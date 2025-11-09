from __future__ import annotations
from typing import List


def wrap_text(text: str, width: int) -> List[str]:
    """
    Pure text wrapper (no printing).
    - Splits on whitespace.
    - If a single word is longer than width, it is put on its own line (no hyphenation).
    """
    if width is None or width < 1:
        raise ValueError("width must be >= 1")

    words = text.split()
    if not words:
        return [""]

    lines: List[str] = []
    cur = words[0]
    for w in words[1:]:
        if len(cur) + 1 + len(w) <= width:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def make_bubble(text: str, width: int | None = None) -> str:
    """
    Build a speech bubble as a single string.
    - If width is provided, wrap the text to that width.
    - Supports multi-line input already containing '\n' (each line is treated as a paragraph).
    """
    if text is None:
        raise ValueError("text must be a string")

    # split paragraphs first
    paragraphs = text.split("\n")
    if width is not None:
        if width < 1:
            raise ValueError("width must be >= 1")
        lines = []
        for p in paragraphs:
            if p.strip() == "":
                lines.append("")  # preserve empty line
            else:
                lines.extend(wrap_text(p, width))
    else:
        lines = paragraphs

    # compute max visible width
    maxw = max((len(line) for line in lines), default=0)

    top = "  " + "_" * (maxw + 2)
    body = "\n".join(f"| {line.ljust(maxw)} |" for line in lines)
    bottom = "  " + "=" * (maxw + 2)
    tail = "       \\\n        \\"

    return f"{top}\n {body}\n{bottom}\n{tail}"

#test - run: python3 -m bloomsays.bubble
if __name__ == "__main__":
    print(make_bubble("Ask Bloombot!"))

