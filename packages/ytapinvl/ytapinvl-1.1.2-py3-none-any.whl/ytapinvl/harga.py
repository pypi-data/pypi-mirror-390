from .config import load_config
from .utils import get_json

def list_roles(interactive=True):
    cfg = load_config()
    base = cfg["base_url"].rstrip("/")
    url = f"{base}/topup/roles"
    print(f"📦 Mengambil daftar harga role dari: {url}")

    try:
        data = get_json(url)
    except Exception as e:
        print(f"⚠️ Gagal mengambil data role: {e}")
        return {}

    if not isinstance(data, dict):
        print("❌ Format data tidak valid (bukan object JSON).")
        return {}

    print("\n💰 Daftar Role Tersedia:\n────────────────────────────")

    flat_roles = []  # daftar semua role (gabungan semua kategori)
    index = 1

    # 🔹 Loop setiap kategori (mis. masterpro, strategiselit, dll)
    for kategori, daftar in data.items():
        print(f"\n🗂️  {kategori.upper()}")
        for r in daftar:
            role = r.get("role")
            harga = r.get("price", 0)
            hari = r.get("days", "-")
            print(f"{index}. {role:<22} Rp{harga:,}  ({hari} hari)")
            flat_roles.append({"kategori": kategori, **r})
            index += 1

    if not interactive:
        return flat_roles

    pilih = input("\n🔹 Masukkan nomor role untuk lihat detail (atau Enter untuk keluar): ").strip()
    if not pilih:
        print("👋 Keluar tanpa memilih role.")
        return flat_roles

    if not pilih.isdigit() or not (1 <= int(pilih) <= len(flat_roles)):
        print("❌ Pilihan tidak valid.")
        return flat_roles

    chosen = flat_roles[int(pilih) - 1]
    limit = chosen.get("limit", {})

    print("\n📋 Detail Role:")
    print("────────────────────────────")
    print(f"Kategori   : {chosen.get('kategori', '-')}")
    print(f"Nama Role  : {chosen.get('role', '-')}")
    print(f"Harga      : Rp{chosen.get('price', 0):,}")
    print(f"Durasi     : {chosen.get('days', '-')} hari")
    print(f"Resolusi   : {limit.get('resolution', '-')}")
    print(f"Max Size   : {limit.get('max_size_mb', '-')} MB")
    print(f"Rate/min   : {limit.get('rpm', '-')}")
    print("────────────────────────────\n")

    return flat_roles