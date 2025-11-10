from .config import load_config
from .utils import get_json
import requests

def check_me(ip: str = None, apikey: str = None):
    """
    Mengecek informasi akun / IP pengguna:
    - Jika pakai --ip -> GET /checkme?ip=<ip> (tanpa header)
    - Jika pakai --apikey -> GET /checkme?ip=halo (pakai header X-API-Key)
    - Jika tidak isi -> GET /checkme (ambil IP publik otomatis)
    """
    cfg = load_config()
    base = cfg["base_url"].rstrip("/")

    if apikey:
        url = f"{base}/checkme?ip=halo"
        print(f"🔑 Mode API Key aktif → {url}")
        try:
            r = requests.get(url, headers={"accept": "application/json", "X-API-Key": apikey}, timeout=(5,10))
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    elif ip:
        url = f"{base}/checkme?ip={ip}"
        print(f"🌐 Mode IP publik → {url}")
        return get_json(url)

    else:
        url = f"{base}/checkme"
        print(f"🤖 Mode otomatis (ambil IP publik) → {url}")
        return get_json(url)