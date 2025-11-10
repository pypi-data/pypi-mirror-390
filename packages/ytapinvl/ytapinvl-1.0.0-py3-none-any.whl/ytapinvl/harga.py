from .config import load_config
from .utils import get_json

def list_roles(interactive=True):
    """
    Mengambil daftar harga role dari server:
    Endpoint: /topup/roles
    Jika interactive=True, akan menampilkan daftar dan minta user memilih role untuk melihat detail.
    """
    cfg = load_config()
    base = cfg["base_url"].rstrip("/")
    url = f"{base}/topup/roles"
    print(f"📦 Mengambil daftar harga role dari: {url}")

    try:
        data = get_json(url)
    except Exception as e:
        print(f"⚠️ Gagal mengambil data role: {e}")
        return {"error": str(e)}

    roles = data.get("roles") or data
    if not roles:
        print("❌ Tidak ada data role tersedia.")
        return {}

    print("\n💰 Daftar Role Tersedia:")
    print("────────────────────────────")
    for i, r in enumerate(roles, 1):
        nama = r.get("nama") or r.get("role") or "Tidak diketahui"
        harga = r.get("harga") or 0
        hari = r.get("hari") or r.get("durasi") or "-"
        print(f"{i}. {nama:<20} Rp{harga:,}  ({hari} hari)")

    if not interactive:
        return roles

    # Interaktif: pilih role
    try:
        pilih = input("\n🔹 Masukkan nama atau nomor role yang ingin dilihat detailnya: ").strip()
    except KeyboardInterrupt:
        print("\nDibatalkan.")
        return roles

    # Coba cocokkan berdasarkan index atau nama
    chosen = None
    if pilih.isdigit() and 1 <= int(pilih) <= len(roles):
        chosen = roles[int(pilih) - 1]
    else:
        for r in roles:
            if pilih.lower() in str(r.get("nama", "")).lower():
                chosen = r
                break

    if not chosen:
        print("❌ Role tidak ditemukan.")
        return roles

    print("\n📋 Detail Role:")
    print("────────────────────────────")
    print(f"Nama    : {chosen.get('nama', 'Tidak diketahui')}")
    print(f"Harga   : Rp{chosen.get('harga', 0):,}")
    print(f"Durasi  : {chosen.get('hari', chosen.get('durasi', '-'))} hari")
    fitur = chosen.get("fitur") or []
    if fitur:
        print("Fitur   :")
        for f in fitur:
            print(f"   - {f}")
    else:
        print("Fitur   : -")
    print("────────────────────────────\n")

    return roles