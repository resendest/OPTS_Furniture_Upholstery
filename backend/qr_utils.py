import os, qrcode

def generate_order_qr(order_id: int, base_url: str, static_qr_dir: str) -> str:
    """Create QR PNG → return web path like '/static/qr/qr_123.png'"""
    url = f"{base_url}/update_stage/{order_id}"
    os.makedirs(static_qr_dir, exist_ok=True)
    filename = f"qr_{order_id}.png"
    filepath = os.path.join(static_qr_dir, filename)
    img = qrcode.make(url)
    img.save(filepath)
    return f"/static/qr/{filename}"