import time
from .utils import post_json, save_history, get_json

# ============================================================
# 💸 Buat transaksi QRIS dan auto cek status
# ============================================================

def buy_role(role, wa, ip=None, apikey=None):
    """Buat transaksi QRIS untuk beli role dengan auto-cek pembayaran"""
    base = "https://ytdlpyton.nvlgroup.my.id"
    qris_url = f"{base}/topup/qris?role={role}&wa={wa}"

    if apikey:
        qris_url += f"&ip={apikey}"
        print("🪙 Membuat transaksi QRIS via API Key ...")
        print(f"   ➤ Mode : APIKEY")
    elif ip:
        qris_url += f"&ip={ip}"
        print("🪙 Membuat transaksi QRIS via IP manual ...")
        print(f"   ➤ Mode : IP")
    else:
        print("🌍 Mengecek otomatis IP publik via /checkme ...")
        me = get_json(f"{base}/checkme")
        if not me or not me.get("auth_value"):
            print("⚠️ Gagal mendeteksi IP, isi manual dengan --ip atau --apikey")
            return
        ip_auto = me["auth_value"]
        qris_url += f"&ip={ip_auto}"
        print(f"🪙 Membuat transaksi QRIS otomatis dengan IP {ip_auto} ...")
        print(f"   ➤ Mode : AUTO")

    print(f"   ➤ WA : {wa}")
    print(f"   ➤ URL : {qris_url}")

    res = post_json(qris_url)
    if not res:
        print("❌ Gagal membuat transaksi QRIS.")
        return

    idpay = res.get("idpay")
    redirect_url = res.get("redirect_url")
    if idpay:
        print(f"✅  Transaksi berhasil dibuat: {idpay}")
    if redirect_url:
        print(f"🔗 QRIS Link: {redirect_url}")
    else:
        print("⚠️ QRIS Link tidak tersedia di respon server.")

    save_history(res)

    # ======================================================
    # 🕒 Auto cek status pembayaran 8 menit (tiap 30 detik)
    # ======================================================
    print("⏳  Menunggu pembayaran (cek setiap 30 detik hingga 8 menit)...")
    for _ in range(16):  # 16 * 30s = 8 menit
        time.sleep(30)
        cek_url = f"{base}/topup/check/{idpay}"
        hasil = get_json(cek_url)
        status = hasil.get("transaction_status") or hasil.get("status") or "unknown"
        print(f"🔁  Status: {status}")
        if status.lower() in ["settlement", "success", "paid"]:
            print("🎉 Pembayaran berhasil!")
            break
    else:
        print("⌛ Waktu tunggu habis, transaksi belum dibayar.")