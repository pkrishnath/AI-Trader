from typing import List, Dict, Any, Optional


def dumps(rows: List[Dict[str, Any]], name: Optional[str] = None) -> str:
    """
    Minimal TOON formatter used by prompts.
    Example output:
    rows[2] {date,open,high,low,close}
      2024-01-01 100 110 90 105
      2024-01-02 105 115 95 110

    We implement only what's needed: formatting a list of dicts.
    """
    if rows is None or len(rows) == 0:
        header_name = name or "rows"
        return f"{header_name}[0] {{}}\n"  # empty with no columns

    # Use keys from first row to define column order
    first = rows[0]
    keys = list(first.keys())
    header_name = name or "rows"

    # Build header
    header = f"{header_name}[{len(rows)}] {{{','.join(keys)}}}"

    def fmt_val(v: Any) -> str:
        if v is None:
            return ""
        # Normalize booleans and numbers to plain str
        return str(v)

    # Build body lines
    body_lines = []
    for r in rows:
        values = [fmt_val(r.get(k)) for k in keys]
        body_lines.append("  " + " ".join(values))

    return "\n".join([header] + body_lines) + "\n"
