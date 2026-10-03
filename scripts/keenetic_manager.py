#!/usr/bin/env py
"""
Канонический скрипт управления и аудита роутера Keenetic (RCI API).

Функционал:
- Аудит активных политик маршрутизации и VPN-туннелей (WireGuard).
- Инвентаризация подключенных устройств локальной сети (Hotspot).
- Проверка DNS-прокси, апстримов DoH/DoT и фильтров (AdGuard).
- Сетевая диагностика (ping/traceroute через туннели с роутера).

Использование:
  py scripts/keenetic_manager.py status [--password PASS]
  py scripts/keenetic_manager.py hotspot [--filter NAME/IP/MAC]
  py scripts/keenetic_manager.py policies
  py scripts/keenetic_manager.py dns
  py scripts/keenetic_manager.py ping --host www.youtube.com [--interface Wireguard1]
"""

import sys
import os
import argparse
import hashlib
import json
import time
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_ROUTER_IP = os.getenv("KEENETIC_IP", "192.168.1.1")
DEFAULT_USERNAME = os.getenv("KEENETIC_USER", "admin")


class KeeneticClient:
    def __init__(self, ip=DEFAULT_ROUTER_IP, user=DEFAULT_USERNAME, password=None):
        self.ip = ip
        self.user = user
        self.password = password or os.getenv("KEENETIC_PASSWORD", "")
        self.session = requests.Session()
        self.authenticated = False

    def authenticate(self):
        if not self.password:
            raise ValueError("Пароль роутера не указан! Передайте через --password или переменную окружения KEENETIC_PASSWORD.")

        auth_url = f"http://{self.ip}/auth"
        r = self.session.get(auth_url)
        if r.status_code == 200:
            self.authenticated = True
            return True

        realm = r.headers.get("X-NDM-Realm")
        challenge = r.headers.get("X-NDM-Challenge")
        if not realm or not challenge:
            raise ConnectionError(f"Ошибка получения challenge от роутера ({r.status_code}): {r.headers}")

        # Хэширование по стандарту KeeneticOS RCI:
        # 1. md5(username:realm:password)
        # 2. sha256(challenge + md5_hex)
        md5_hash = hashlib.md5(f"{self.user}:{realm}:{self.password}".encode('utf-8')).hexdigest()
        final_hash = hashlib.sha256((challenge + md5_hash).encode('utf-8')).hexdigest()

        payload = {"login": self.user, "password": final_hash}
        login_res = self.session.post(auth_url, json=payload)
        if login_res.status_code == 200:
            self.authenticated = True
            return True
        else:
            raise PermissionError(f"Ошибка аутентификации ({login_res.status_code}): {login_res.text}")

    def rci_get(self, path):
        if not self.authenticated:
            self.authenticate()
        r = self.session.get(f"http://{self.ip}/rci/{path}")
        r.raise_for_status()
        return r.json()

    def rci_text(self, path):
        if not self.authenticated:
            self.authenticate()
        r = self.session.get(f"http://{self.ip}/rci/{path}")
        r.raise_for_status()
        return r.text

    def rci_post(self, path, payload):
        if not self.authenticated:
            self.authenticate()
        r = self.session.post(f"http://{self.ip}/rci/{path}", json=payload)
        r.raise_for_status()
        return r.json()


def cmd_status(client, args):
    system = client.rci_get("show/system")
    version = client.rci_get("show/version")
    interfaces = client.rci_get("show/interface")

    uptime = int(system.get('uptime', 0))
    mem_total = int(system.get('memtotal', 0))
    mem_free = int(system.get('memfree', 0))

    print(f"=== Роутер: {system.get('hostname', 'Keenetic')} ({version.get('model', 'KN')}) ===")
    print(f"KeeneticOS: {version.get('title', '')} (версия {version.get('release', '')})")
    print(f"Аптайм: {uptime // 3600} ч. {(uptime % 3600) // 60} мин.")
    print(f"Память: занято {mem_total - mem_free} КБ из {mem_total} КБ")
    print(f"CPU: {system.get('cpuload', 0)}%")
    print("\n--- Ключевые интерфейсы ---")
    for name, iface in interfaces.items():
        itype = iface.get("type", "")
        if itype in ["Wireguard", "OpenVPN", "PPPoE", "UsbQmi"] or iface.get("global", False):
            desc = iface.get("description", "")
            state = iface.get("state", "down")
            addr = iface.get("address", "")
            mtu = iface.get("mtu", "")
            print(f"- {name} ({itype}): desc='{desc}', state={state}, mtu={mtu}, ip={addr}")


def cmd_hotspot(client, args):
    hotspot = client.rci_get("show/ip/hotspot")
    hosts = hotspot.get("host", [])
    running_cfg_text = client.rci_text("show/running-config")

    # Считываем привязки политик из конфига
    policy_map = {}
    filter_map = {}
    for line in running_cfg_text.splitlines():
        line = line.strip().strip('"').strip(',')
        if line.startswith("host ") and "policy " in line:
            parts = line.split()
            if len(parts) >= 4:
                policy_map[parts[1].lower()] = parts[3]
        if line.startswith("filter assign host preset "):
            parts = line.split()
            if len(parts) >= 6:
                filter_map[parts[4].lower()] = parts[5]

    print(f"=== Зарегистрированные и активные устройства ({len(hosts)}) ===")
    print(f"{'Имя устройства':<30} | {'IP-адрес':<15} | {'MAC-адрес':<17} | {'Статус':<8} | {'Политика':<15} | {'Фильтр'}")
    print("-" * 105)

    search = (args.filter or "").lower()
    for h in sorted(hosts, key=lambda x: (not x.get("active", False), x.get("ip", ""))):
        name = h.get("name") or h.get("hostname") or "—"
        ip = h.get("ip", "—")
        mac = h.get("mac", "").lower()
        active = "ONLINE" if h.get("active", False) else "offline"
        pol = policy_map.get(mac, "Основная")
        flt = filter_map.get(mac, "—")

        if search and (search not in name.lower() and search not in ip and search not in mac):
            continue

        print(f"{name:<30} | {ip:<15} | {mac:<17} | {active:<8} | {pol:<15} | {flt}")


def cmd_policies(client, args):
    policies = client.rci_get("show/ip/policy")
    print("=== Политики маршрутизации (Connection Priorities) ===")
    for pol_id, pol_data in policies.items():
        desc = pol_data.get("description", pol_id)
        routes = pol_data.get("route4", {}).get("route", [])
        gw = "Шлюз по умолчанию: "
        def_routes = [r for r in routes if r.get("destination") == "0.0.0.0/0"]
        if def_routes:
            gw += f"{def_routes[0].get('interface')} (metric {def_routes[0].get('metric')})"
        else:
            gw += "Основной провайдер (PPPoE/WAN)"

        print(f"\n[{pol_id}] {desc}")
        print(f"  {gw}")
        print(f"  Маршрутов в таблице: {len(routes)}")
        for r in routes:
            if r.get("destination") != "0.0.0.0/0":
                print(f"    -> {r.get('destination')} через {r.get('interface')}")


def cmd_dns(client, args):
    dns_servers = client.rci_get("show/ip/name-server")
    print("=== Системные DNS-серверы ===")
    for s in dns_servers.get("server", []):
        print(f"- {s.get('address')} (domain: '{s.get('domain', '')}', interface: '{s.get('interface', '')}')")

    try:
        dp = client.rci_get("show/dns-proxy")
        print("\n=== DNS-Proxy (DoH / DoT Upstreams) ===")
        proxy_list = dp if isinstance(dp, list) else dp.values() if isinstance(dp, dict) else []
        for p in proxy_list:
            if not isinstance(p, dict):
                continue
            pname = p.get("proxy-name", "")
            tls = p.get("proxy-tls", {}).get("server-tls", [])
            https = p.get("proxy-https", {}).get("server-https", [])
            filters = p.get("proxy-https-filters", {}).get("server-https", [])
            print(f"\nПрофиль: {pname}")
            for t in tls:
                print(f"  [DoT] {t.get('address')}")
            for h in https:
                print(f"  [DoH] {h.get('uri')}")
            for f in filters:
                print(f"  [Filter] {f.get('uri')}")
    except Exception as e:
        print(f"Детали dns-proxy недоступны: {e}")


def cmd_ping(client, args):
    host = args.host
    iface = args.interface or "Wireguard1"
    print(f"Запуск ping {host} через интерфейс {iface} с роутера...")
    payload = {"host": host, "interface": iface, "count": args.count}
    client.rci_post("tools/ping", payload)
    time.sleep(2)
    res = client.rci_get("tools/ping")
    for line in res.get("message", []):
        print(line)


def main():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--ip", default=DEFAULT_ROUTER_IP, help="IP-адрес роутера (default: 192.168.1.1)")
    common_parser.add_argument("--user", default=DEFAULT_USERNAME, help="Пользователь роутера (default: admin)")
    common_parser.add_argument("--password", default=None, help="Пароль администратора роутера (или KEENETIC_PASSWORD)")

    parser = argparse.ArgumentParser(description="Keenetic Router API Manager", parents=[common_parser])
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommands
    subparsers.add_parser("status", parents=[common_parser], help="Общий статус системы и интерфейсов")
    
    p_hotspot = subparsers.add_parser("hotspot", parents=[common_parser], help="Список устройств и привязок к политикам")
    p_hotspot.add_argument("--filter", default="", help="Фильтр по имени, IP или MAC")

    subparsers.add_parser("policies", parents=[common_parser], help="Таблицы и политики маршрутизации")
    subparsers.add_parser("dns", parents=[common_parser], help="DNS-серверы, DoH, DoT и контентные фильтры")

    p_ping = subparsers.add_parser("ping", parents=[common_parser], help="Пинг узла через выбранный интерфейс")
    p_ping.add_argument("--host", required=True, help="Целевой хост")
    p_ping.add_argument("--interface", default="Wireguard1", help="Интерфейс выхода (default: Wireguard1)")
    p_ping.add_argument("--count", type=int, default=3, help="Количество пакетов")

    args = parser.parse_args()
    client = KeeneticClient(ip=args.ip, user=args.user, password=args.password)

    if args.command == "status":
        cmd_status(client, args)
    elif args.command == "hotspot":
        cmd_hotspot(client, args)
    elif args.command == "policies":
        cmd_policies(client, args)
    elif args.command == "dns":
        cmd_dns(client, args)
    elif args.command == "ping":
        cmd_ping(client, args)


if __name__ == "__main__":
    main()
