from device_configs import DEVICE_CONFIGS
from router_configs import ROUTER_CONFIGS
from network_services import SNMPV3_AUTH_PASSWORD, SNMPV3_PRIV_PASSWORD


PLACEHOLDER_VALUES = [
    "BURAYA_GUCLU_AUTH_SIFRE_YAZ",
    "BURAYA_GUCLU_PRIV_SIFRE_YAZ",
]


def flatten(configs):
    commands = []

    for device_name, device_commands in configs.items():
        for command in device_commands:
            commands.append((device_name, command))

    return commands


def check_no_telnet(all_commands):
    failures = [
        (device, command)
        for device, command in all_commands
        if command == "transport input telnet"
    ]

    if failures:
        print("HATA: Telnet VTY komutu kalmis:")
        for device, command in failures:
            print(device, command)
        return False

    print("OK: transport input telnet yok.")
    return True


def check_ssh(all_commands):
    ssh_devices = {
        device
        for device, command in all_commands
        if command == "transport input ssh"
    }

    print("OK: SSH VTY olan cihaz sayisi:", len(ssh_devices))
    return True


def check_switch_services():
    ok = True

    for device_name, commands in DEVICE_CONFIGS.items():
        required = [
            "ip ssh version 2",
            "no ip http server",
            "no ip http secure-server",
        ]

        for command in required:
            if command not in commands:
                print(f"HATA: {device_name} icinde eksik komut: {command}")
                ok = False

        if not any(command.startswith("logging host ") for command in commands):
            print(f"HATA: {device_name} icinde logging host yok.")
            ok = False

        if not any(command.startswith("ntp server ") for command in commands):
            print(f"HATA: {device_name} icinde ntp server yok.")
            ok = False

        if any(command == "ip dhcp snooping" for command in commands):
            if "no ip dhcp snooping information option" not in commands:
                print(f"HATA: {device_name} icinde no ip dhcp snooping information option yok.")
                ok = False

            if not any(command.startswith("ip dhcp snooping vlan ") for command in commands):
                print(f"HATA: {device_name} icinde DHCP snooping VLAN listesi yok.")
                ok = False

            if not any(command.startswith("ip arp inspection vlan ") for command in commands):
                print(f"HATA: {device_name} icinde DAI VLAN listesi yok.")
                ok = False

    if ok:
        print("OK: Switch servis/hardening komutlari gorunuyor.")

    return ok


def check_snmp_passwords():
    if SNMPV3_AUTH_PASSWORD in PLACEHOLDER_VALUES:
        print("HATA: SNMPV3_AUTH_PASSWORD placeholder kalmis.")
        return False

    if SNMPV3_PRIV_PASSWORD in PLACEHOLDER_VALUES:
        print("HATA: SNMPV3_PRIV_PASSWORD placeholder kalmis.")
        return False

    print("OK: SNMPv3 placeholder sifre yok.")
    return True


def main():
    switch_commands = flatten(DEVICE_CONFIGS)
    router_commands = flatten(ROUTER_CONFIGS)
    all_commands = switch_commands + router_commands

    checks = [
        check_no_telnet(all_commands),
        check_ssh(all_commands),
        check_switch_services(),
        check_snmp_passwords(),
    ]

    if all(checks):
        print("SONUC: Generated config temel kontrolleri basarili.")
    else:
        print("SONUC: Hata var. Cihazlara config basma.")


if __name__ == "__main__":
    main()