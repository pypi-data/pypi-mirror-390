import requests

def verify_paytm(mid: str, order_id: str) -> dict:
    """
    Verify a Paytm merchant payment using MID and Order ID.
    Returns a structured JSON-style dictionary similar to the npm package.
    """
    if not mid or not order_id:
        raise ValueError("Both 'mid' and 'order_id' are required.")

    BASE_URL = "https://paytm.udayscriptsx.workers.dev"

    try:
        response = requests.get(BASE_URL, params={"mid": mid, "id": order_id}, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise RuntimeError(f"Verification failed: {str(e)}")

    order_id_val = data.get("ORDERID")
    amount = data.get("TXNAMOUNT")
    status = data.get("STATUS")
    message = data.get("RESPMSG")
    date = data.get("TXNDATE")
    mode = data.get("PAYMENTMODE")
    bank_txn = data.get("BANKTXNID")

    missing = [k for k, v in data.items() if v == ""]

    if status == "TXN_SUCCESS":
        readable = f"✅ Payment Successful\nOrder ID: {order_id_val}\nAmount: ₹{amount}\nDate: {date}\nMode: {mode}\nBank Txn ID: {bank_txn}"
    elif status == "TXN_FAILURE":
        readable = f"❌ Payment Failed\nOrder ID: {order_id_val}\nReason: {message}"
    else:
        readable = f"⚠️ Payment Status Unknown\nOrder ID: {order_id_val}\nMessage: {message}"

    return {
        "success": status == "TXN_SUCCESS",
        "orderId": order_id_val,
        "status": status,
        "amount": amount or None,
        "message": message,
        "date": date or None,
        "paymentMode": mode or None,
        "bankTxnId": bank_txn or None,
        "missingFields": missing if missing else None,
        "readable": readable
    }
