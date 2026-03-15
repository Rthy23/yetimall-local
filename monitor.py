import asyncio
import json
import logging
from playwright.async_api import async_playwright
import processor
from config import PRODUCT_URL, ORDER_URL_KEYWORDS

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def _handle_response(response):
    """Intercept all responses; debug-log every yetimall.store response, record matching order APIs."""
    url = response.url
    if "yetimall.store" not in url:
        return
    asyncio.create_task(_debug_and_maybe_record(response))


async def _debug_and_maybe_record(response):
    """For every yetimall.store response: print URL, status, first 200 chars of body. Optionally record orders."""
    url = response.url
    status = response.status
    try:
        body = await response.body()
    except Exception as e:
        print(f"[yetimall.response] URL={url} Status={status} body_error={e}")
        return

    # Debug: print URL, status, and first 200 chars of body for any yetimall response
    ct = response.headers.get("content-type") or ""
    body_preview = ""
    if body:
        try:
            body_preview = body.decode("utf-8", errors="replace")[:200]
        except Exception:
            body_preview = "<binary or decode error>"
    print(f"[yetimall.response] URL={url} Status={status} body_preview={body_preview!r}")

    # Record order data only when URL matches keywords and response is JSON
    if any(kw in url for kw in ORDER_URL_KEYWORDS) and "application/json" in ct and body:
        try:
            data = json.loads(body)
            if processor.record_order(data):
                logger.info("DEBUG: DATA CAPTURED SUCCESSFULLY!")
        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.debug(f"Parse/record error: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 390, "height": 844},
            locale="zh-TW",
        )
        page = await context.new_page()
        page.on("response", _handle_response)
        
        logger.info(f"Navigating → {PRODUCT_URL}")
        await page.goto(PRODUCT_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(15)
        
        await browser.close()
        logger.info("Session finished.")

if __name__ == "__main__":
    asyncio.run(main())
