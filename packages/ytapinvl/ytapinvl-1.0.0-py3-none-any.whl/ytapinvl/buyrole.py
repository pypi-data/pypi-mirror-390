import time
from .config import load_config, save_config, save_history
from .utils import get_json, post_json

def create_payment(role, wa=None, force_ip=None, apikey=None, auto_check=True):
    """
    Membuat transaksi QRIS:
    - Jika ada --apikey -> ip=<apikey>
    - Jika ada --ip -> ip=<alamat ip>
    - Jika dua-duanya kosong -> ambil IP dari /checkme (tanpa header)
    Semua dikirim lewat query, tanpa header X-API-Key
    """
    cfg = load_config()
    base = cfg["base_url"].rstrip("/")

    ip_arg = force_ip
    apikey_arg = apikey or cfg.get("apikey")
    wa_final = wa or cfg.get("wa")

    if not wa_final:
        raise RuntimeError("❌ Nomor WA belum diset. Gunakan `ytapinvl config --set-wa`.")
    if not role:
        raise RuntimeError("❌ Role belum ditentukan.")

    # Tentukan mode
    if apikey_arg:
        ip_query = apikey_arg
        mode = "apikey"
    elif ip_arg:
        ip_query = ip_arg
        mode = "ip"
    else:
        # AUTO: ambil IP dari /checkme
        checkme_url = f"{base}/checkme"
        try:
            data = get_json(checkme_url)
            ip_query = data.get("ip") or data.get("client_ip") or "0.0.0.0"
            mode = "auto"
            print(f"🌍 Auto detect IP dari /checkme: {ip_query}")
        except Exception as e:
            print(f"⚠️ Gagal ambil IP dari /checkme: {e}")
            ip_query = "0.0.0.0"
            mode = "auto"

    save_config({"last_ip": ip_query, "wa": wa_final})

    url = f"{base}/topup/qris?ip={ip_query}&role={role}&wa={wa_final}"
    print(f"\n🪙 Membuat transaksi QRIS untuk role '{role}' ...")
    print(f"   ➤ Mode : {mode.upper()}")
    print(f"   ➤ IP/apikey dikirim : {ip_query}")
    print(f"   ➤ WA : {wa_final}")
    print(f"   ➤ URL : {url}\n")

    result = post_json(url)
    if not result or "idpay" not in result:
        return {"error": "Gagal membuat transaksi.", "response": result}

    idpay = result["idpay"]
    print(f"✅ Transaksi berhasil dibuat: {idpay}")
    print("🔗 QRIS Link:", result.get("qris_url", "tidak tersedia"))
    print("⏳ Menunggu pembayaran (cek setiap 30 detik hingga 8 menit)...\n")

    save_history({
        "last_idpay": idpay,
        "last_ip": ip_query,
        "last_role": role,
        "timestamp": time.time()
    })

    # Polling 8 menit
    if not auto_check:
        return result

    check_url = f"{base}/topup/check/{idpay}"
    last_status = None
    for i in range(1, 17):
        try:
            status_data = get_json(check_url)
            status = status_data.get("transaction_status") or status_data.get("status") or "unknown"
            if status != last_status:
                print(f"🔄 [{i}] Status: {status}")
                last_status = status
            if status.lower() in ("settlement", "success", "capture"):
                print("\n✅ Pembayaran berhasil! Role aktif.")
                result["status_info"] = status_data
                break
        except Exception as e:
            print(f"⚠️ Error saat cek status: {e}")
        if i < 16:
            time.sleep(30)

    print("\n📦 Proses selesai.")
    result["status_info"] = status_data
    return result