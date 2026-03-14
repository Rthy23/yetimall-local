"""
monitor.py — GitHub Action 雲端快照版 (執行一次即結束)
"""

import asyncio
import logging
from playwright.async_api import async_playwright

import processor
from config import PRODUCT_URL, ORDER_URL_KEYWORDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

async def _handle_request(request):
    """攔截 API 請求並提取訂單數據"""
    if "yetimall.store" in request.url:
        if any(kw in request.url for kw in ORDER_URL_KEYWORDS):
            try:
                response = await request.response()
                if response:
                    data = await response.json()
                    processor.record_order(data)
            except Exception:
                pass

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("requestfinished", _handle_request)
        
        logger.info(f"Navigating → {PRODUCT_URL}")
        # 訪問網頁，等待網路活動平靜下來
        await page.goto(PRODUCT_URL, wait_until="networkidle")
        
        # 關鍵修改：等待 10 秒，給 API 請求足夠時間觸發並被攔截
        await asyncio.sleep(10) 
        
        await browser.close()
        logger.info("Session finished.")

if __name__ == "__main__":
    asyncio.run(main())
