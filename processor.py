import csv
import os
import logging
from datetime import datetime
from config import DATA_FILE

logger = logging.getLogger(__name__)

# JSON key 優先序維持不變，保持你的解析能力
_ORDER_ID_KEYS = ("orderId", "order_id", "orderCode", "orderNo", "transactionId", "transaction_id", "purchaseId", "purchase_id")
_USER_ID_KEYS = ("userId", "user_id", "buyerId", "buyer_id", "participantId", "participant_id", "memberId", "member_id", "nickname", "userName", "username")
_QTY_KEYS = ("quantity", "qty", "count", "item_count", "itemCount", "purchaseQuantity", "purchase_quantity", "orderQuantity", "order_quantity")
_COUNTRY_KEYS = ("country", "countryCode", "country_code", "region", "area", "nation", "deliveryCountry", "delivery_country", "shippingCountry", "shipping_country")
_TIMESTAMP_KEYS = ("timestamp", "createdAt", "created_at", "orderTime", "order_time", "createTime", "create_time", "paidAt", "paid_at")

def _extract(obj, keys, default=""):
    """從 obj 或巢狀 dict 中萃取第一個匹配的 key 值"""
    if obj is None:
        return default
    if isinstance(obj, dict):
        for k in keys:
            if k in obj:
                val = obj[k]
                if isinstance(val, (dict, list)):
                    return str(val)[:100] if val else default
                return val if val is not None else default
    return default

def _normalize_order(data):
    """Map incoming API fields (nested keys, camelCase) to flat CSV schema."""
    obj = data.get("data", data) if isinstance(data, dict) else data
    if isinstance(obj, list) and obj:
        obj = obj[0] if isinstance(obj[0], dict) else data
    if not isinstance(obj, dict):
        obj = data if isinstance(data, dict) else {}

    return {
        "user_id": _extract(obj, _USER_ID_KEYS),
        "order_id": _extract(obj, _ORDER_ID_KEYS),
        "quantity": _extract(obj, _QTY_KEYS, default=1),
        "timestamp": _extract(obj, _TIMESTAMP_KEYS) or datetime.utcnow().isoformat(),  # default if API omits
        "country": _extract(obj, _COUNTRY_KEYS),
    }

def record_to_local_csv(order):
    """將訂單記錄追加到本地 CSV，這是 GitHub Action 的基礎"""
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['user_id', 'order_id', 'quantity', 'timestamp', 'country'])
        writer.writerow([
            order.get('user_id', ''),
            order.get('order_id', ''),
            order.get('quantity', ''),
            order.get('timestamp', ''),
            order.get('country', ''),
        ])

def record_order(raw_order):
    """處理並記錄訂單，支援 raw API JSON（含巢狀 data）"""
    try:
        normalized = _normalize_order(raw_order)
        oid = normalized.get('order_id')
        if not oid:
            return False
        record_to_local_csv(normalized)
        logger.info(f"[記錄成功] order_id={oid!r}  qty={normalized.get('quantity')}")
        return True
    except Exception as exc:
        logger.warning(f"[record_order] 錯誤: {exc}")
        return False