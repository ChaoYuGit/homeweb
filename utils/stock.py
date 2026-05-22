import os

STOCK_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "report")

SECTIONS = [
    ("sync",  "Sync Status",        "cron_daily.log"),
    ("macro", "Macro Data",         "01_Daily_Macro.txt"),
    ("mywatch", "MyWatch",          "02_Daily_MyWatch.txt"),
    ("fund",  "StockInFund",        "03_Daily_StockInFund.txt"),
]


def _read_file(filename):
    path = os.path.join(STOCK_DIR, filename)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return None


def get_stock_files():
    reports = []
    for sid, title, filename in SECTIONS:
        content = _read_file(filename)
        if content is not None:
            reports.append({"id": sid, "title": title, "filename": filename, "content": content})
    return reports


def get_section(section_id):
    for sid, title, filename in SECTIONS:
        if sid == section_id:
            content = _read_file(filename)
            if content is not None:
                return {"id": sid, "title": title, "filename": filename, "content": content}
            return None
    return None
