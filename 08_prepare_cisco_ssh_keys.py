from urllib.parse import urlparse

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

from device_configs import DEVICE_CONFIGS
from gns3_client import gns3_request

from network_services import SERVER_URL, PROJECT_ID, DOMAIN_NAME, ENABLE_SECRET


def get_gns3_server_host():
    return urlparse(SERVER_URL).hostname


def get_console_host(node):
    console_host = node.get("console_host")

    if not console_host or console_host in ("0.0.0.0", "::"):
        return get_gns3_server_host()

    return console_host


def get_nodes_by_name():
    nodes = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes",
    )
    return {node["name"]: node for node in nodes}


def has_rsa_key(connection):
    output = connection.send_command_timing(
        "show crypto key mypubkey rsa",
        read_timeout=60,
        strip_prompt=False,
        strip_command=False,
    )

    lowered = output.lower()

    no_key_markers = [
        "not found",
        "no key",
        "not been generated",
        "key pair was not found",
    ]

    if any(marker in lowered for marker in no_key_markers):
        return False

    return "key name:" in lowered or "public key data" in lowered


def prepare_device(device_name, node):
    device = {
        "device_type": "cisco_ios_telnet",
        "host": get_console_host(node),
        "port": node["console"],
        "secret": ENABLE_SECRET,
        "conn_timeout": 20,
        "read_timeout_override": 180,
        "global_delay_factor": 2,
        "fast_cli": False,
    }

    print("=" * 60)
    print("Cihaz:", device_name)

    connection = ConnectHandler(**device)

    try:
        connection.enable()

        connection.send_config_set(
            [
                f"hostname {device_name}",
                f"ip domain-name {DOMAIN_NAME}",
                "ip ssh version 2",
            ],
            read_timeout=120,
            cmd_verify=False,
        )

        if has_rsa_key(connection):
            print("UYARI: RSA key zaten var, atlandi:", device_name)
            return

        print("RSA key yok, olusturuluyor:", device_name)

        output = connection.send_command_timing(
            "configure terminal",
            read_timeout=60,
            strip_prompt=False,
            strip_command=False,
        )

        output += connection.send_command_timing(
            "crypto key generate rsa modulus 2048",
            read_timeout=180,
            strip_prompt=False,
            strip_command=False,
        )

        output += connection.send_command_timing(
            "end",
            read_timeout=60,
            strip_prompt=False,
            strip_command=False,
        )

        print(output)

        save_output = connection.send_command_timing(
            "write memory",
            read_timeout=120,
            strip_prompt=False,
            strip_command=False,
        )

        if "confirm" in save_output.lower():
            save_output += connection.send_command_timing(
                "\n",
                read_timeout=120,
                strip_prompt=False,
                strip_command=False,
            )

        print(save_output)

    finally:
        connection.disconnect()


def main():
    nodes_by_name = get_nodes_by_name()

    for device_name in DEVICE_CONFIGS:
        node = nodes_by_name.get(device_name)

        if not node:
            print("Node bulunamadi, atlandi:", device_name)
            continue

        try:
            prepare_device(device_name, node)
        except NetmikoTimeoutException:
            print("Timeout, cihaz acik mi kontrol et:", device_name)
        except NetmikoAuthenticationException:
            print("Authentication hatasi:", device_name)
        except Exception as error:
            print("Hata:", device_name, error)


if __name__ == "__main__":
    main()