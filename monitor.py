"""
monitor.py — GitHub Action 雲端監控版 (CSV 輸出)
"""

import asyncio
import logging
import random
import time
from datetime import datetime
from playwright.async_api import async_playwright

import processor
from config import (
    GOODS_ID, PRODUCT_URL, DEADLINE,
    ORDER_URL_KEYWORDS,
    JITTER_LOW, JITTER_HIGH,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 請求攔截邏輯
# ---------------------------------------------------------------------------

async def _handle_request(request):
    """攔截 API 請求並提取訂單數據"""
    if "yetimall.store" in request.url:
        if any(kw in request.url for kw in ORDER_URL_KEYWORDS):
            try:
                response = await request.response()
                if response:
                    data = await response.json()
                    # 直接呼叫 processor.py 處理並存入 CSV
                    processor.record_order(data)
            except Exception:
                pass

# ---------------------------------------------------------------------------
# Playwright Session
# ---------------------------------------------------------------------------

async def _run_session():
    async with async_playwright() as p:
        # 在 GitHub Actions 中，記得使用 headless 模式
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 註冊攔截器
        page.on("requestfinished", _handle_request)
        
        logger.info(f"Navigating → {PRODUCT_URL}")
        await page.goto(PRODUCT_URL, wait_until="networkidle")
        
        # 監控直到截止時間
        while datetime.now() < DEADLINE:
            await asyncio.sleep(30) # 每 30 秒確認一次
            
        await browser.close()

# ---------------------------------------------------------------------------
# 主程式 (Entry point)
# ---------------------------------------------------------------------------

def run() -> None:
    logger.info(f"Monitor started — goods {GOODS_ID} | deadline {DEADLINE}")
    
    # 不再需要 init_db()，直接開始運行
    while datetime.now() < DEADLINE:
        try:
            asyncio.run(_run_session())
        except Exception as exc:
            wait = random.uniform(JITTER_LOW, JITTER_HIGH)
            logger.error(f"Session error: {exc} — restarting in {wait:.1f}s")
            time.sleep(wait)

if __name__ == "__main__":
    run()