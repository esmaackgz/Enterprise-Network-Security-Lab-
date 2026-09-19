import shlex
import time
import re

from gns3_client import gns3_request
from network_services import SERVER_URL, PROJECT_ID
from server_console import (
    get_nodes_by_name,
    open_server_console,
    run_checked,
    run_command,
)
from server_inventory import SERVERS


NETPLAN_PATH = "/etc/netplan/99-project-static.yaml"
BACKUP_ROOT = "/root/project-netplan-backups"

AD_DNS_SERVERS = {"AD-DC1", "AD-DC2",}

DNS_FORWARDER_SERVERS = {"DNS1", "DNS2",}

INTERNAL_DNS_CLIENTS = { "DHCP1",  "DHCP2",  "APP1",  "APP2",  "RADIUS1",  "RADIUS2",  "TACACS1",  "TACACS2",
    "NTP1","NTP2",  "MONITOR-ZABBIX",  "PROMETHEUS",  "GRAFANA",  "NETFLOW-COLLECTOR",  "LOG-SIEM-WAZUH",
    "GRAYLOG",  "IDS-SURICATA",  "IDS-ZEEK",  "LB1",  "LB2",  "DB1",  "DB2",
    "NETBOX",  "JUMPBOX",  "CONFIG-BACKUP", "BACKUP",}

DMZ_DNS_CLIENTS = {"WEB1-DMZ", "WEB2-DMZ", "WAF-LB1", "WAF-LB2", "PUBLIC-DNS1", "VPN-GW",}

SERVERS_BY_NAME = {
    server["name"]: server
    for server in SERVERS
}


def validate_dns_policy():
    inventory_names = set(SERVERS_BY_NAME)

    policy_names = (
        AD_DNS_SERVERS
        | DNS_FORWARDER_SERVERS
        | INTERNAL_DNS_CLIENTS
        | DMZ_DNS_CLIENTS
    )

    missing = inventory_names - policy_names
    unknown = policy_names - inventory_names

    if missing:
        raise RuntimeError(
            "DNS politikasi olmayan serverlar: "
            + ", ".join(sorted(missing))
        )

    if unknown:
        raise RuntimeError(
            "Inventory icinde bulunmayan serverlar: "
            + ", ".join(sorted(unknown))
        )


def get_dns_servers(server_name):
    if server_name == "AD-DC1":
        return "10.10.130.11", "10.10.130.12"

    if server_name == "AD-DC2":
        return "10.10.130.12", "10.10.130.11"

    if server_name == "DNS1":
        return "10.10.130.21", "10.10.130.22"

    if server_name == "DNS2":
        return "10.10.130.22", "10.10.130.21"

    if server_name in INTERNAL_DNS_CLIENTS:
        return "10.10.130.11", "10.10.130.12"

    if server_name in DMZ_DNS_CLIENTS:
        return "10.10.130.21", "10.10.130.22"

    raise RuntimeError(
        f"DNS politikasi bulunamadi: {server_name}"
    )


def get_dns_role(server_name):
    if server_name in AD_DNS_SERVERS:
        return "AD DNS"

    if server_name in DNS_FORWARDER_SERVERS:
        return "DNS forwarder"

    if server_name in DMZ_DNS_CLIENTS:
        return "DMZ DNS client"

    return "Internal DNS client"


def extract_mac(output):
    match = re.search(
        r"([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})",
        output,
    )

    if not match:
        raise RuntimeError(
            f"MAC adresi okunamadi: {output!r}"
        )

    return match.group(1).lower()


def write_remote_file(connection, path, content):
    quoted_path = shlex.quote(path)

    run_checked(
        connection,
        f"sudo -n install -m 600 /dev/null {quoted_path}",
        timeout=30,
    )

    lines = content.rstrip("\n").splitlines()

    for start in range(0, len(lines), 20):
        chunk = lines[start:start + 20]
        quoted_lines = " ".join(
            shlex.quote(line)
            for line in chunk
        )

        command = (
            f"printf '%s\\n' {quoted_lines} | "
            f"sudo -n tee -a {quoted_path} > /dev/null"
        )

        output, exit_code = run_command(
            connection,
            command,
            timeout=60,
        )

        if exit_code != 0:
            raise RuntimeError(
                f"Dosya yazilamadi: {path}\n{output}"
            )

    run_checked(
        connection,
        f"sudo -n sed -i 's/\\r$//' {quoted_path}",
        timeout=30,
    )

    print(f"Dosya yazildi: {path}")

def create_netplan(server, mac_address, dns_servers):
    return f"""network:
  version: 2
  ethernets:
    ens3:
      match:
        macaddress: "{mac_address}"
      set-name: "ens3"
      dhcp4: false
      dhcp6: false
      addresses:
        - {server["ip"]}/{server["prefix"]}
      routes:
        - to: default
          via: {server["gateway"]}
      nameservers:
        addresses:
          - {dns_servers[0]}
          - {dns_servers[1]}
"""


def backup_and_clear_netplan(connection, server_name):
    timestamp = run_checked(
        connection,
        "date +%Y%m%d-%H%M%S",
    ).strip()

    backup_dir = (
        f"{BACKUP_ROOT}/{server_name}-{timestamp}"
    )
    quoted_backup = shlex.quote(backup_dir)

    run_checked(
        connection,
        f"sudo -n mkdir -p {quoted_backup}",
    )

    run_checked(
        connection,
        "sudo -n find /etc/netplan "
        "-maxdepth 1 -type f "
        "\\( -name '*.yaml' -o -name '*.yml' \\) "
        f"-exec cp -a {{}} {quoted_backup}/ \\;",
    )

    run_checked(
        connection,
        "sudo -n find /etc/netplan "
        "-maxdepth 1 -type f "
        "\\( -name '*.yaml' -o -name '*.yml' \\) "
        "-delete",
    )

    print(f"Netplan yedegi: {backup_dir}")
    return backup_dir


def restore_netplan(connection, backup_dir):
    quoted_backup = shlex.quote(backup_dir)

    print("Netplan hatasi, eski dosyalar geri yukleniyor.")

    run_command(
        connection,
        "sudo -n find /etc/netplan "
        "-maxdepth 1 -type f "
        "\\( -name '*.yaml' -o -name '*.yml' \\) "
        "-delete",
        timeout=30,
    )

    run_command(
        connection,
        f"sudo -n cp -a {quoted_backup}/. /etc/netplan/",
        timeout=30,
    )

    run_command(
        connection,
        "sudo -n netplan generate",
        timeout=60,
    )


def configure_server(server_name):
    server = SERVERS_BY_NAME[server_name]
    dns_servers = get_dns_servers(server_name)

    print("\n" + "-" * 60)
    print("Server:", server_name)
    print("Rol:", get_dns_role(server_name))
    print("IP:", server["ip"])
    print("Gateway:", server["gateway"])
    print("DNS:", ", ".join(dns_servers))

    with open_server_console(server_name) as connection:
        raw_mac = run_checked(
            connection,
            "cat /sys/class/net/ens3/address",
        ).strip()

        mac_address = extract_mac(raw_mac)
        print("MAC:", mac_address)

        backup_dir = backup_and_clear_netplan(
            connection,
            server_name,
        )

        write_remote_file(
            connection,
            "/etc/cloud/cloud.cfg.d/"
            "99-disable-network-config.cfg",
            "network:\n  config: disabled\n",
        )

        write_remote_file(
            connection,
            NETPLAN_PATH,
            create_netplan(
                server,
                mac_address,
                dns_servers,
            ),
        )

        run_checked(
            connection,
            f"sudo -n chmod 600 {NETPLAN_PATH}",
        )

        output, exit_code = run_command(
            connection,
            "sudo -n netplan generate",
            timeout=60,
        )

        print("\n$ sudo -n netplan generate")
        if output:
            print(output)
        print("Exit code:", exit_code)

        if exit_code != 0:
            restore_netplan(connection, backup_dir)
            raise RuntimeError("Netplan generate basarisiz.")

        run_checked(
            connection,
            "sudo -n resolvectl revert ens3",
        )

        run_checked(
            connection,
            "sudo -n netplan apply",
            timeout=90,
        )

        time.sleep(3)

        address_output = run_checked(
            connection,
            "ip -4 -br addr show ens3",
        )

        route_output = run_checked(
            connection,
            "ip route show default",
        )

        dns_output = run_checked(
            connection,
            "resolvectl status ens3",
        )

        if server["ip"] not in address_output:
            raise RuntimeError("Statik IP uygulanmadi.")

        if server["gateway"] not in route_output:
            raise RuntimeError("Default gateway uygulanmadi.")

        for dns_server in dns_servers:
            if dns_server not in dns_output:
                raise RuntimeError(
                    f"DNS uygulanmadi: {dns_server}"
                )

        print(f"OK: {server_name} Netplan tamamlandi.")


def change_node_state(node, action):
    gns3_request(
        SERVER_URL,
        "POST",
        f"/v2/projects/{PROJECT_ID}/nodes/"
        f"{node['node_id']}/{action}",
    )


def wait_for_node_started(server_name, timeout=180):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        node = get_nodes_by_name().get(server_name)

        if node and node.get("status") == "started":
            return

        time.sleep(5)

    raise TimeoutError(
        f"Node baslatilamadi: {server_name}"
    )


def wait_for_console(server_name, timeout=180):
    deadline = time.monotonic() + timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            with open_server_console(server_name) as connection:
                output, exit_code = run_command(
                    connection,
                    "true",
                    timeout=15,
                )

                if exit_code == 0:
                    return

        except Exception as error:
            last_error = error

        time.sleep(5)

    raise TimeoutError(
        f"Console hazir olmadi: {server_name}: "
        f"{last_error}"
    )


def main():
    validate_dns_policy()

    updated = []
    failed = []

    print("Toplam server:", len(SERVERS))

    for server in SERVERS:
        server_name = server["name"]
        node = get_nodes_by_name().get(server_name)

        if not node:
            failed.append((server_name, "Node bulunamadi"))
            continue

        was_started = node.get("status") == "started"

        try:
            if not was_started:
                print(f"\n{server_name} baslatiliyor...")
                change_node_state(node, "start")
                wait_for_node_started(server_name)
                wait_for_console(server_name)

            configure_server(server_name)
            updated.append(server_name)

        except Exception as error:
            failed.append((server_name, str(error)))
            print(f"[HATA] {server_name}: {error}")

        finally:
            if not was_started:
                current_node = get_nodes_by_name().get(
                    server_name
                )

                if (
                    current_node
                    and current_node.get("status") == "started"
                ):
                    change_node_state(current_node, "stop")
                    print(f"{server_name} yeniden kapatildi.")
                    time.sleep(5)

    print("\n" + "=" * 60)
    print("TUM SERVER NETPLAN SONUCU")
    print("=" * 60)
    print(f"Basarili: {len(updated)}/{len(SERVERS)}")

    for server_name in updated:
        print(f"OK: {server_name}")

    if failed:
        print("\nHatalar:")

        for server_name, error in failed:
            print(f"HATA: {server_name}: {error}")


if __name__ == "__main__":
    main()