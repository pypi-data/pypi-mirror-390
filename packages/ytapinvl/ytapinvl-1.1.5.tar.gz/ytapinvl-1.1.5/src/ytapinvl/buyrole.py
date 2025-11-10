import time, requests
from .config import load_config
from .utils import get_json, save_history

def buy_role(role: str, wa: str, ip=None, apikey=None):
    cfg = load_config()
    base = cfg["base_url"].rstrip("/")
    mode = "AUTO"

    # 🔹 Tentukan mode
    if apikey:
        mode = "APIKEY"
        final_ip = apikey  # apikey dikirim langsung via ?ip=
    elif ip:
        mode = "IP"
        final_ip = ip
    else:
        # 🔹 AUTO ambil dari /checkme
        try:
            info = get_json(f"{base}/checkme")
            final_ip = info.get("auth_value") or info.get("ip") or "127.0.0.1"
            print(f"🌍 Auto detect IP dari /checkme → {final_ip}")
        except Exception as e:
            print(f"⚠️ Gagal auto detect IP: {e}")
            final_ip = "127.0.0.1"

    # 🔹 Buat URL transaksi
    url = f"{base}/topup/qris?ip={final_ip}&role={role}&wa={wa}"

    print(f"\n🪙 Membuat transaksi QRIS untuk role '{role}' ...")
    print(f"   ➤ Mode : {mode}")
    print(f"   ➤ IP/apikey dikirim : {final_ip}")
    print(f"   ➤ WA : {wa}")
    print(f"   ➤ URL : {url}")

    # 🔹 Kirim request
    try:
        res = requests.post(url, timeout=20)
        res.raise_for_status()
        result = res.json()
    except Exception as e:
        print(f"❌ Gagal membuat transaksi: {e}")
        return

    idpay = result.get("idpay") or result.get("order_id")
    qris_url = result.get("redirect_url") or result.get("qris_url") or "tidak tersedia"

    print(f"✅ Transaksi berhasil dibuat: {idpay}")
    print(f"🔗 QRIS Link: {qris_url}")
    print("⏳ Menunggu pembayaran (cek setiap 30 detik hingga 8 menit)...\n")

    save_history(result)

    # 🔁 Loop cek status setiap 30 detik (total 8 menit)
    for _ in range(16):
        try:
            status_data = get_json(f"{base}/topup/check/{idpay}")
            status = (status_data.get("transaction_status") or status_data.get("status") or "").lower()

            if status in ("settlement", "capture", "success"):
                print(f"🎉 Pembayaran sukses untuk {role}! (status: {status})")
                return
            elif status in ("expire", "failure", "cancel"):
                print(f"❌ Transaksi {status}, pembayaran gagal/expired.")
                return
            else:
                print(f"⏳ Belum dibayar... (status: {status or 'pending'})")
        except Exception as e:
            print(f"⚠️ Gagal cek status: {e}")
        time.sleep(30)

    print("⌛ Batas waktu 8 menit habis, transaksi belum selesai.")