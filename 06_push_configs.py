from urllib.parse import urlparse

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

from gns3_client import gns3_request
from device_configs import DEVICE_CONFIGS
from network_services import DOMAIN_NAME, SERVER_URL, PROJECT_ID, ENABLE_SECRET

def get_gns3_server_host():
    parsed = urlparse(SERVER_URL)
    return parsed.hostname


def get_console_host(node):
    console_host = node.get("console_host")

    if not console_host:
        return get_gns3_server_host()

    if console_host in ("0.0.0.0", "::"):
        return get_gns3_server_host()

    return console_host

def get_nodes_by_name():
    nodes = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes"
    )

    return {node["name"]: node for node in nodes}

def save_config(connection):
    connection.set_base_prompt()

    output = connection.send_command_timing(
        "write memory",
        strip_prompt=False,
        strip_command=False
    )

    if "confirm" in output.lower():
        output += connection.send_command_timing(
            "\n",
            strip_prompt=False,
            strip_command=False
        )

    return output

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
    console_port = node["console"]

    device = {
        "device_type": "cisco_ios_telnet",
        "host": console_host,
        "port": console_port,
        "secret": ENABLE_SECRET,
        "conn_timeout": 20,
        "timeout": 30,
        "global_delay_factor": 2,
    }

    print("=" * 60)
    print("Cihaz:", device_name)
    print("Console:", console_host, console_port)

    connection = ConnectHandler(**device)
    connection.enable()

    commands = DEVICE_CONFIGS[device_name]

    hostname_command = commands[0]
    remaining_commands = commands[1:]

    connection.send_config_set(
        [hostname_command],
        cmd_verify=False
    )

    connection.set_base_prompt()

    ensure_rsa_key(connection, device_name)
    
    output = connection.send_config_set(
        remaining_commands,
        read_timeout=120,
        cmd_verify=False
    )

    print(output)

    save_output = save_config(connection)
    print(save_output)

    connection.disconnect()

    print("Tamamlandi:", device_name)




def main():
    nodes_by_name = get_nodes_by_name()

    for device_name in DEVICE_CONFIGS:
        if device_name not in nodes_by_name:
            print("Node bulunamadi, atlandi:", device_name)
            continue

        try:
            push_config(device_name, nodes_by_name[device_name])
        except NetmikoTimeoutException:
            print("Timeout, cihaz acik mi kontrol et:", device_name)
        except NetmikoAuthenticationException:
            print("Authentication hatasi:", device_name)
        except Exception as error:
            print("Hata:", device_name, error)

if __name__ == "__main__":
    main()