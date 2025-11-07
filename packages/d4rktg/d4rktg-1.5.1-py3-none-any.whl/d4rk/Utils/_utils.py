


def progress_bar(pct):
    pct = float(str(pct).strip("%"))
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    cPart = int(p % 8 - 1)
    p_str = "■" * cFull
    if cPart >= 0:
        p_str += ["▤", "▥", "▦", "▧", "▨", "▩", "■"][cPart]
    p_str += "□" * (12 - cFull)
    return f"[{p_str}]"