"""
config.py — 平台切換中心 (GitHub 雲端監控版)
"""

from datetime import datetime

# ── 活動設定 ─────────────────────────────────────────────────────────────────
GOODS_ID     = 29860
PRODUCT_NAME = "Yetimall 商品監控"
DEADLINE     = datetime(2026, 3, 16, 0, 0, 0)
FAST_START   = datetime(2026, 3, 15, 21, 0, 0)   # 此時間後切換 5 秒高頻模式

# ── 儲存設定 (取代原有的 SQLite) ────────────────────────────────────────────
# 數據將直接儲存為此 CSV 檔案，之後會透過 GitHub Actions 自動更新
DATA_FILE = "sales_records.csv"

# ── 目標網址 ─────────────────────────────────────────────────────────────────
PRODUCT_URL = f"https://m.yetimall.store/h5/#/goods?gid={GOODS_ID}"

# ── 訂單 API 攔截關鍵字（更廣泛以減少漏掉 API）──────────────────────────────────
ORDER_URL_KEYWORDS: tuple[str, ...] = (
    "/order/",
    "/get",
    "/list",
    "/user/",
    "payment",
    "order",
    "checkout",
    "api/v1/order",
    "submit",
    "purchase",
)

# ── 採樣間隔（秒）────────────────────────────────────────────────────────────
NORMAL_INTERVAL  = 30    # 平時
FAST_INTERVAL    = 5     # FAST_START 後
SILENT_INTERVAL  = 60    # 429 靜默模式
JITTER_LOW       = 1.0
JITTER_HIGH      = 3.0