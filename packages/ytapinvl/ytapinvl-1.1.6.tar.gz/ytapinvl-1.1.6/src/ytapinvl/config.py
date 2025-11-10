import os
import json
from datetime import datetime

# ============================================================
# 📁 Path lokasi penyimpanan konfigurasi
# ============================================================
CONFIG_DIR = os.path.expanduser("~/.config/ytapinvl")
HISTORY_FILE = os.path.join(CONFIG_DIR, "history.json")

# ============================================================
# ⚙️  Fungsi utama
# ============================================================

def ensure_config():
    """Pastikan direktori konfigurasi tersedia"""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
    except Exception as e:
        print(f"⚠️ Gagal membuat direktori konfigurasi: {e}")

def show_config():
    """Menampilkan informasi konfigurasi CLI"""
    ensure_config()

    print("⚙️  Konfigurasi YT API CLI by Nauval")
    print("─────────────────────────────────────")
    print(f"📁 Direktori Konfig : {CONFIG_DIR}")
    print(f"🧾 File Riwayat     : {HISTORY_FILE}")

    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)

            print(f"📦 Jumlah Riwayat   : {len(history)} transaksi")
            if history:
                latest = history[0]
                waktu = latest.get("time", "-")
                data = latest.get("data", {})
                idpay = data.get("idpay", "-")
                role = data.get("role", "-")
                print("─────────────────────────────────────")
                print(f"🕓 Terakhir         : {waktu}")
                print(f"💳 ID Transaksi     : {idpay}")
                print(f"🏷️  Role Dibeli     : {role}")
        except Exception as e:
            print(f"⚠️  Gagal membaca file history: {e}")
    else:
        print("📭 Belum ada file riwayat transaksi.")

# ============================================================
# 🧩 Fungsi tambahan opsional
# ============================================================

def clear_history():
    """Hapus seluruh riwayat transaksi"""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        print("🧹 Riwayat transaksi berhasil dihapus.")
    else:
        print("📭 Tidak ada file riwayat untuk dihapus.")

def print_last_history():
    """Tampilkan transaksi terakhir dari history"""
    if not os.path.exists(HISTORY_FILE):
        print("📭 Belum ada riwayat transaksi.")
        return
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        if not history:
            print("📭 File riwayat kosong.")
            return
        last = history[0]
        print("🕓 Transaksi Terakhir")
        print("────────────────────────")
        print(json.dumps(last, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"⚠️ Gagal membaca riwayat: {e}")

# ============================================================
# 🔚 Eksekusi langsung (opsional)
# ============================================================
if __name__ == "__main__":
    show_config()