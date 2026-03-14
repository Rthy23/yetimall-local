import asyncio
import logging
from playwright.async_api import async_playwright
import processor
from config import PRODUCT_URL, ORDER_URL_KEYWORDS

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

async def _handle_request(request):
    # 【關鍵】列印所有請求，如果 Log 沒東西，說明爬蟲連網頁都沒連上
    print(f"DEBUG: Processing URL: {request.url}") 
    
    if "yetimall.store" in request.url and any(kw in request.url for kw in ORDER_URL_KEYWORDS):
        try:
            response = await request.response()
            if response:
                data = await response.json()
                processor.record_order(data)
                print("DEBUG: DATA CAPTURED SUCCESSFULLY!")
        except Exception as e:
            print(f"DEBUG: Error in capturing data: {e}")

# ... (main 函式保持使用 domcontentloaded 導航)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 設定偽裝 User-Agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        page.on("requestfinished", _handle_request)
        
        logger.info(f"Navigating → {PRODUCT_URL}")
        # 使用 domcontentloaded 避免 Timeout
        await page.goto(PRODUCT_URL, wait_until="domcontentloaded")
        
        # 等待 API 觸發
        await asyncio.sleep(15) 
        
        await browser.close()
        logger.info("Session finished.")

if __name__ == "__main__":
    asyncio.run(main())
