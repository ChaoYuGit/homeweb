import os

STOCK_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "report")

FILES = [
    ("Daily Macro", "01_Daily_Macro.txt"),
    ("Daily MyWatch", "02_Daily_MyWatch.txt"),
    ("Daily StockInFund", "03_Daily_StockInFund.txt"),
]


def get_stock_files():
    reports = []
    for title, filename in FILES:
        path = os.path.join(STOCK_DIR, filename)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                content = f.read()
            reports.append({"title": title, "filename": filename, "content": content})
    return reports
