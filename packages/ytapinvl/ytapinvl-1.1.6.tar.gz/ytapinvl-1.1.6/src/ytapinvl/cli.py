import argparse
from .me import check_me
from .harga import list_roles
from .buyrole import buy_role
from .config import show_config

# ============================================================
# 🎛️  CLI Utama YT API by Nauval
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        prog="ytapinvl",
        description="YT API CLI by Nauval - Pembelian Role & Cek Status Akun"
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # --------------------------------------------------------
    # 🧭 Command: me
    # --------------------------------------------------------
    s_me = sub.add_parser("me", help="Cek akun Anda via IP atau API Key")
    s_me.add_argument("--ip", help="Cek berdasarkan IP manual")
    s_me.add_argument("--apikey", help="Cek berdasarkan API key")
    s_me.set_defaults(func=lambda a: check_me(a.ip, a.apikey))

    # --------------------------------------------------------
    # 💰 Command: harga
    # --------------------------------------------------------
    s_harga = sub.add_parser("harga", help="Lihat daftar harga dan paket role")
    s_harga.set_defaults(func=lambda a: list_roles())

    # --------------------------------------------------------
    # 🪙 Command: buy
    # --------------------------------------------------------
    s_buy = sub.add_parser("buy", help="Beli role via QRIS (otomatis cek pembayaran)")
    s_buy.add_argument("--role", required=True, help="Nama role yang ingin dibeli (contoh: masterpro1)")
    s_buy.add_argument("--wa", required=True, help="Nomor WhatsApp untuk notifikasi (contoh: 6285177470790)")
    s_buy.add_argument("--ip", help="Gunakan IP manual (opsional)")
    s_buy.add_argument("--apikey", help="Gunakan API Key (opsional)")
    s_buy.set_defaults(func=lambda a: buy_role(a.role, a.wa, a.ip, a.apikey))

    # --------------------------------------------------------
    # ⚙️ Command: config
    # --------------------------------------------------------
    s_conf = sub.add_parser("config", help="Lihat lokasi konfigurasi dan riwayat transaksi")
    s_conf.set_defaults(func=lambda a: show_config())

    # --------------------------------------------------------
    # Jalankan
    # --------------------------------------------------------
    args = parser.parse_args()
    args.func(args)

# ============================================================
# 🚀 Entry Point
# ============================================================
if __name__ == "__main__":
    main()