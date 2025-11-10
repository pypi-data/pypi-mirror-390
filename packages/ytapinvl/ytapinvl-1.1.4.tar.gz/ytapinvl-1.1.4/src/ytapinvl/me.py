import requests
from .utils import print_json

# ============================================================
# 🔍 Fungsi cek akun via IP atau API Key
# ============================================================

def check_me(ip=None, apikey=None):
    """
    Mengecek akun dan role:
    - Jika apikey diberikan → kirim via header Authorization
    - Jika ip diberikan → kirim via query ?ip=
    - Jika tidak ada keduanya → cek otomatis berdasarkan IP publik
    """
    base = "https://ytdlpyton.nvlgroup.my.id"
    url = f"{base}/checkme"

    headers = {}
    params = {}

    if apikey:
        print("🔑 Mengecek akun menggunakan API Key ...")
        headers["Authorization"] = apikey  # kirim via header
    elif ip:
        print(f"🌐 Mengecek akun menggunakan IP manual: {ip}")
        params["ip"] = ip
    else:
        print("🌍 Mengecek akun otomatis via IP publik ...")

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        res.raise_for_status()
        data = res.json()
        print_json(data)
    except Exception as e:
        print(f"⚠️ Gagal memeriksa akun: {e}")