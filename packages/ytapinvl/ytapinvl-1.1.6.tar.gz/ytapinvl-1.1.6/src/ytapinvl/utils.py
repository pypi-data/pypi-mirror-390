import os
import json
import requests
from datetime import datetime

# 🔹 Lokasi penyimpanan data konfigurasi & history
CONFIG_DIR = os.path.expanduser("~/.config/ytapinvl")
HISTORY_FILE = os.path.join(CONFIG_DIR, "history.json")

# ============================================================
# 🔸 Helper HTTP Functions
# ============================================================

def get_json(url):
    """Ambil data JSON dari URL GET"""
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"⚠️ Gagal mengambil data dari {url}: {e}")
        return {}

def post_json(url, payload=None):
    """Kirim data JSON via POST"""
    try:
        res = requests.post(url, json=payload or {}, timeout=20)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"⚠️ Gagal POST ke {url}: {e}")
        return {}

# ============================================================
# 🔸 History Functions
# ============================================================

def save_history(data):
    """Simpan data transaksi terbaru ke file history.json"""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        history = []

        # baca history lama jika ada
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)

        # tambah timestamp
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": data
        }

        history.insert(0, entry)
        history = history[:20]  # batasi 20 transaksi terakhir

        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)

        print(f"💾 Riwayat transaksi disimpan di {HISTORY_FILE}")
    except Exception as e:
        print(f"⚠️ Gagal menyimpan riwayat transaksi: {e}")

def load_history(limit=10):
    """Ambil daftar transaksi terakhir"""
    if not os.path.exists(HISTORY_FILE):
        print("📭 Belum ada riwayat transaksi.")
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        return history[:limit]
    except Exception as e:
        print(f"⚠️ Gagal membaca riwayat transaksi: {e}")
        return []

# ============================================================
# 🔸 Utility Output
# ============================================================

def print_json(obj):
    """Tampilkan JSON secara rapi di terminal"""
    try:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    except Exception:
        print(obj)