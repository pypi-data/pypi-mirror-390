import argparse, json
from . import __version__
from .config import load_config, save_config
from .me import check_me
from .harga import list_roles
from .buyrole import create_payment

def _print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))

def cmd_me(a): _print_json(check_me(a.ip, a.apikey))
def cmd_harga(a): _print_json(list_roles())
def cmd_buy(a): _print_json(create_payment(a.role, a.wa, a.ip, a.apikey, auto_check=True))

def cmd_config(a):
    if a.set_base: save_config({"base_url": a.set_base})
    if a.set_wa: save_config({"wa": a.set_wa})
    if a.set_apikey: save_config({"apikey": a.set_apikey})
    _print_json(load_config())

def main():
    p = argparse.ArgumentParser(
        prog="ytapinvl",
        description="YT API CLI by Nauval — cek info akun, daftar harga, dan beli role via QRIS"
    )
    p.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    # 🔹 me
    s = sub.add_parser("me", help="Cek informasi akun / IP publik")
    s.add_argument("--ip", help="Cek mode IP publik manual (tanpa header)")
    s.add_argument("--apikey", help="Cek mode API Key (kirim header X-API-Key)")
    s.set_defaults(func=cmd_me)

    # 🔹 harga
    s = sub.add_parser("harga", help="Lihat daftar harga role")
    s.set_defaults(func=cmd_harga)

    # 🔹 buy
    s = sub.add_parser("buy", help="Beli role via QRIS + auto cek status 8 menit")
    s.add_argument("--role", required=True, help="Nama role yang ingin dibeli")
    s.add_argument("--wa", help="Nomor WhatsApp (otomatis dari config jika kosong)")
    s.add_argument("--ip", help="Alamat IP manual (mode IP publik)")
    s.add_argument("--apikey", help="Gunakan API key (mode akun)")
    s.set_defaults(func=cmd_buy)

    # 🔹 config
    s = sub.add_parser("config", help="Atur konfigurasi lokal")
    s.add_argument("--set-base", help="Atur URL base API (default: https://ytdlpyton.nvlgroup.my.id)")
    s.add_argument("--set-wa", help="Atur nomor WhatsApp default")
    s.add_argument("--set-apikey", help="Simpan API key ke config lokal")
    s.set_defaults(func=cmd_config)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()