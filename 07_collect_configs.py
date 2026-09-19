from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException


from gns3_client import gns3_request
from device_configs import DEVICE_CONFIGS
from network_services import SERVER_URL, PROJECT_ID, ENABLE_SECRET


SHOW_COMMANDS = [
    "show vlan brief",
    "show ip interface brief",
    "show mac address-table",
    "show cdp neighbors",
    "show interfaces status",
    "show interfaces trunk",
    "show etherchannel summary",
    "show lacp neighbor",
    "show spanning-tree",
    "show spanning-tree root",
    "show spanning-tree blockedports",
    "show spanning-tree inconsistentports",
    "show port-security",
    "show ip ssh",
    "show logging",
    "show ntp status",
    "show ntp associations",
    "show snmp user",
    "show snmp group",
    "show access-lists MANAGEMENT-VTY",
    "show access-lists MONITORING-SNMP",
]


def get_nodes_by_name():
    nodes = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes"
    )

    return {node["name"]: node for node in nodes}


def get_console_host(node):
    console_host = node.get("console_host")

    if not console_host or console_host in ("0.0.0.0", "::"):
        return urlparse(SERVER_URL).hostname

    return console_host


def collect_device(device_name, node, output_directory):
    device = {
        "device_type": "cisco_ios_telnet",
        "host": get_console_host(node),
        "port": node["console"],
        "secret": ENABLE_SECRET,
        "conn_timeout": 20,
        "read_timeout_override": 180,
        "global_delay_factor": 2,
    }

    print("=" * 60)
    print("Baglaniliyor:", device_name)

    connection = ConnectHandler(**device)
    connection.enable()

    connection.send_command_timing("terminal length 0", read_timeout=30)
    connection.send_command_timing("terminal width 511", read_timeout=30)

    running_config = connection.send_command_timing(
        "show running-config",
        read_timeout=240,
        last_read=8,
    )

    if "\nend" not in running_config:
        running_config = connection.send_command_timing(
            "show running-config",
            read_timeout=300,
            last_read=12,
        )

    config_file = output_directory / f"{device_name}_running-config.txt"
    config_file.write_text(running_config, encoding="utf-8")

    report_parts = []

    for command in SHOW_COMMANDS:
        print("Calistiriliyor:", device_name, command)

        output = connection.send_command(
            command,
            read_timeout=120
        )

        report_parts.append(
            f"\n{'=' * 70}\n"
            f"{command}\n"
            f"{'=' * 70}\n"
            f"{output}\n"
        )

    report_file = output_directory / f"{device_name}_verification.txt"
    report_file.write_text("".join(report_parts), encoding="utf-8")

    connection.disconnect()

    print("Kaydedildi:", config_file)
    print("Kaydedildi:", report_file)


def main():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_directory = Path("collected_configs") / timestamp
    output_directory.mkdir(parents=True, exist_ok=True)

    nodes_by_name = get_nodes_by_name()

    for device_name in DEVICE_CONFIGS:
        if device_name not in nodes_by_name:
            print("Node bulunamadi, atlandi:", device_name)
            continue

        try:
            collect_device(
                device_name,
                nodes_by_name[device_name],
                output_directory
            )

        except NetmikoTimeoutException:
            print("Timeout, cihaz acik mi:", device_name)

        except NetmikoAuthenticationException:
            print("Authentication hatasi:", device_name)

        except KeyboardInterrupt:
            print("\nKullanici tarafindan durduruldu.")
            break

        except Exception as error:
            print("Hata:", device_name, error)

    print("Tum ciktilar burada:", output_directory.resolve())


if __name__ == "__main__":
    main()