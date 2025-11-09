from datetime import date as _date

def month_code(d: _date) -> str:
    return f"{d.year}-{d.month:02d}"