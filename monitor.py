import asyncio
import logging
from playwright.async_api import async_playwright
import processor
from config import PRODUCT_URL, ORDER_URL_KEYWORDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

async def _handle_request(request):
    if "yetimall.store" in request.url and any(kw in request.url for kw in ORDER_URL_KEYWORDS):
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
        await page.goto(PRODUCT_URL, wait_until="networkidle")
        
        # 等待 15 秒讓 API 有機會被觸發與捕捉？
        await asyncio.sleep(15) 
        
        await browser.close()
        logger.info("Session finished.")

if __name__ == "__main__":
    asyncio.run(main())

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
            
