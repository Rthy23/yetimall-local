import csv
import os
import logging
from config import DATA_FILE

logger = logging.getLogger(__name__)

# JSON key 優先序維持不變，保持你的解析能力
_ORDER_ID_KEYS = ("orderId", "order_id", "orderCode", "orderNo", "transactionId", "transaction_id", "purchaseId", "purchase_id")
_USER_ID_KEYS = ("userId", "user_id", "buyerId", "buyer_id", "participantId", "participant_id", "memberId", "member_id", "nickname", "userName", "username")
_QTY_KEYS = ("quantity", "qty", "count", "item_count", "itemCount", "purchaseQuantity", "purchase_quantity", "orderQuantity", "order_quantity")
_COUNTRY_KEYS = ("country", "countryCode", "country_code", "region", "area", "nation", "deliveryCountry", "delivery_country", "shippingCountry", "shipping_country")

def record_to_local_csv(order):
    """將訂單記錄追加到本地 CSV，這是 GitHub Action 的基礎"""
    file_exists = os.path.exists(DATA_FILE)
    
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['user_id', 'order_id', 'quantity', 'timestamp', 'country'])
        
        writer.writerow([
            order.get('user_id'), 
            order.get('order_id'), 
            order.get('quantity'), 
            order.get('timestamp'), 
            order.get('country')
        ])

def record_order(order):
    """處理並記錄訂單"""
    try:
        oid = next((order.get(k) for k in _ORDER_ID_KEYS if k in order), None)
        if not oid:
            return False
            
        record_to_local_csv(order)
        logger.info(f"[記錄成功] order_id={oid!r}  qty={order.get('quantity')}")
        return True
    except Exception as exc:
        logger.warning(f"[record_order] 錯誤: {exc}")
        return False