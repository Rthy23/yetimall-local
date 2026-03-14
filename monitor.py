import asyncio
import logging
from playwright.async_api import async_playwright
import processor
from config import PRODUCT_URL, ORDER_URL_KEYWORDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 在 monitor.py 的 _handle_request 函數開頭加入這行
async def _handle_request(request):
    print(f"DEBUG: Catching URL: {request.url}")  # 這會顯示在 GitHub Action 的 Log 裡
    if "yetimall.store" in request.url and any(kw in request.url for kw in ORDER_URL_KEYWORDS):
        # ... 原有的處理邏輯 ...
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
        # 加入偽裝 User-Agent，避免網站直接擋掉機器人
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        page.on("requestfinished", _handle_request)
        
        logger.info(f"Navigating → {PRODUCT_URL}")
        
        # --- 核心修改 ---
        # 改用 'domcontentloaded'，這比 'networkidle' 寬容得多，能有效解決 Timeout
        await page.goto(PRODUCT_URL, wait_until="domcontentloaded")
        
        # 即使頁面還在載入其他資源，我們手動等待 15 秒，確保 API 有機會發出並被捕捉
        await asyncio.sleep(15) 
        # ----------------
        
        await browser.close()
        logger.info("Session finished.")

async def _handle_request(request):
    # 加上這行，我們會看到所有攔截到的網址
    print(f"DEBUG: Processing URL: {request.url}") 
    
    if "yetimall.store" in request.url and any(kw in request.url for kw in ORDER_URL_KEYWORDS):
        try:
            response = await request.response()
            if response:
                data = await response.json()
                processor.record_order(data)
                print("DEBUG: DATA CAPTURED!")
        except Exception as e:
            print(f"DEBUG: Error: {e}")
            
