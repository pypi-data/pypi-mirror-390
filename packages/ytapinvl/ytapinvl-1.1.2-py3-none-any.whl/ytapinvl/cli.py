import argparse
from .me import check_me
from .harga import list_roles
from .buyrole import buy_role
from .config import show_config

def main():
    parser = argparse.ArgumentParser(prog="ytapinvl", description="YT API CLI by Nauval")
    sub = parser.add_subparsers(dest="cmd", required=True)

    s_me = sub.add_parser("me", help="Cek akun / IP / API Key")
    s_me.add_argument("--ip", help="Cek via IP manual")
    s_me.add_argument("--apikey", help="Cek via API key")
    s_me.set_defaults(func=lambda a: check_me(a.ip, a.apikey))

    s_harga = sub.add_parser("harga", help="Lihat daftar harga role")
    s_harga.set_defaults(func=lambda a: list_roles())

    s_buy = sub.add_parser("buy", help="Beli role via QRIS")
    s_buy.add_argument("--role", required=True, help="Nama role yang ingin dibeli")
    s_buy.add_argument("--wa", required=True, help="Nomor WhatsApp")
    s_buy.add_argument("--ip", help="Gunakan IP manual")
    s_buy.add_argument("--apikey", help="Gunakan API Key")
    s_buy.set_defaults(func=lambda a: buy_role(a.role, a.wa, a.ip, a.apikey))

    s_conf = sub.add_parser("config", help="Lihat konfigurasi")
    s_conf.set_defaults(func=lambda a: show_config())

    args = parser.parse_args()
    args.func(args)