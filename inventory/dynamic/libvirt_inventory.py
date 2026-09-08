#!/usr/bin/env python3
"""libvirt uzerindeki calisan VM'leri Ansible envanteri olarak dondurur."""

import json
import subprocess
import sys
import xml.etree.ElementTree as ET

BRIDGE = "br0"
EXCLUDE = {"linuxlab"}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def get_domains():
    """Calisan VM'lerin adlarini dondurur."""
    out = run(["virsh", "-c", "qemu:///system", "list", "--name", "--state-running"])
    return [n.strip() for n in out.splitlines() if n.strip()]


def get_mac(name):
    """VM'in MAC adresini XML tanimindan cikarir."""
    xml = run(["virsh", "-c", "qemu:///system", "dumpxml", name])
    if not xml:
        return None
    try:
        root = ET.fromstring(xml)
        mac = root.find(".//interface/mac")
        return mac.get("address").lower() if mac is not None else None
    except ET.ParseError:
        return None


def scan_network():
    """Agdaki MAC-IP eslesmelerini toplar."""
    table = {}

    # Once ARP onbellegine bak (hizli)
    for line in run(["ip", "neigh"]).splitlines():
        parts = line.split()
        if "lladdr" in parts:
            ip = parts[0]
            mac = parts[parts.index("lladdr") + 1].lower()
            table[mac] = ip

    # Eksikler icin agi tara
    scan = run(["sudo", "-n", "arp-scan", f"--interface={BRIDGE}", "--localnet"])
    for line in scan.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].count(".") == 3:
            table[parts[1].lower()] = parts[0]

    return table


def build():
    arp = scan_network()
    hosts = {}

    for name in get_domains():
        if name in EXCLUDE:
            continue
        mac = get_mac(name)
        if not mac:
            continue
        ip = arp.get(mac)
        if ip:
            hosts[name] = ip

    inventory = {
        "servers": {
            "hosts": list(hosts.keys()),
        },
        "_meta": {
            "hostvars": {
                name: {
                    "ansible_host": ip,
                    "ansible_user": "baris",
                }
                for name, ip in hosts.items()
            }
        },
    }
    return inventory


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--host":
        print(json.dumps({}))
        return
    print(json.dumps(build(), indent=2))


if __name__ == "__main__":
    main()
