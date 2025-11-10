from .utils import get_json

# ============================================================
# 💰 Daftar harga role
# ============================================================

def list_roles():
    """Ambil dan tampilkan daftar harga role dari server"""
    url = "https://ytdlpyton.nvlgroup.my.id/topup/roles"
    print(f"📦 Mengambil daftar harga role dari: {url}")

    data = get_json(url)
    if not data:
        print("⚠️ Gagal mengambil data role dari server.")
        return

    print("💰 Daftar Role Tersedia:")
    print("────────────────────────────")

    for kategori, roles in data.items():
        print(f"\n🧩 {kategori.upper()}")
        for r in roles:
            role = r.get("role")
            price = r.get("price")
            days = r.get("days")
            print(f"  • {role:<20} Rp{price:<6} | {days} hari")

    print("\nGunakan: ytapinvl buy --role <nama> --wa <nomor>")