import time
from urllib.parse import urlparse

from netmiko import ConnectHandler

from gns3_client import gns3_request
from router_configs import ROUTER_CONFIGS
from network_services import DOMAIN_NAME, SERVER_URL, PROJECT_ID


TARGET_DEVICES = [
    "ISP1",
    "ISP2",
#    "EDGE-R1",
#    "EDGE-R2",
]


CONFIG_READ_TIMEOUT = 180
IOS_ERROR_PATTERN = r"% Invalid input|% Incomplete command|% Ambiguous command"


def get_server_host():
    parsed_url = urlparse(SERVER_URL)
    return parsed_url.hostname


def get_nodes_by_name():
    nodes = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes",
    )
    return {node["name"]: node for node in nodes}


def get_console_host(node):
    console_host = node.get("console_host") or get_server_host()

    if console_host in ("0.0.0.0", "::", None):
        return get_server_host()

    return console_host


def get_console_port(node):
    console_port = node.get("console")

    if console_port is None:
        raise RuntimeError(f"Console port bulunamadi: {node['name']}")

    return int(console_port)

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


def ensure_rsa_key(connection, device_name):
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
        f"ip domain-name {DOMAIN_NAME}",
        read_timeout=60,
        strip_prompt=False,
        strip_command=False,
    )

    output += connection.send_command_timing(
        "ip ssh version 2",
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

    if "[yes/no]" in output.lower() or "replace" in output.lower():
        output += connection.send_command_timing(
            "no",
            read_timeout=60,
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

def push_config(device_name, node):
    console_host = get_console_host(node)
    console_port = get_console_port(node)
    commands = ROUTER_CONFIGS[device_name]

    print("=" * 60)
    print(f"Cihaz: {device_name}")
    print(f"Console: {console_host} {console_port}")

    device = {
        "device_type": "cisco_ios_telnet",
        "host": console_host,
        "port": console_port,
        "username": "",
        "password": "",
        "secret": "",
        "conn_timeout": 20,
        "read_timeout_override": CONFIG_READ_TIMEOUT,
        "global_delay_factor": 2,
        "fast_cli": False,
    }

    connection = ConnectHandler(**device)

    try:
        connection.enable()
        ensure_rsa_key(connection, device_name)

        # RSA üretiminden kalan mesajları temizle ve promptu yeniden algıla.
        time.sleep(3)
        connection.clear_buffer()
        current_prompt = connection.find_prompt()
        print("Aktif prompt:", current_prompt)
        connection.set_base_prompt()

        output = connection.send_config_set(
            commands,
            exit_config_mode=True,
            read_timeout=CONFIG_READ_TIMEOUT,
            cmd_verify=False,
            error_pattern=IOS_ERROR_PATTERN,
        )
        print(output)

        connection.set_base_prompt()

        save_output = connection.send_command_timing(
            "write memory",
            read_timeout=CONFIG_READ_TIMEOUT,
        )

        if "confirm" in save_output.lower() or "[ok]" not in save_output.lower():
            save_output += connection.send_command_timing(
                "\n",
                read_timeout=CONFIG_READ_TIMEOUT,
            )

        print(save_output)

    finally:
        connection.disconnect()


def main():
    nodes_by_name = get_nodes_by_name()

    for device_name in TARGET_DEVICES:
        if device_name not in ROUTER_CONFIGS:
            print(f"Atlandi, router_configs icinde yok: {device_name}")
            continue

        if device_name not in nodes_by_name:
            print(f"Atlandi, GNS3 projesinde node yok: {device_name}")
            continue

        push_config(device_name, nodes_by_name[device_name])


if __name__ == "__main__":
    main()
