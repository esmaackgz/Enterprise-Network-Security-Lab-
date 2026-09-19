from device_configs import DEVICE_CONFIGS


WATCH_COMMANDS = [
    "ip dhcp snooping",
    "ip dhcp snooping vlan",
    "ip dhcp snooping trust",
    "ip arp inspection vlan",
    "ip arp inspection trust",
    "ip verify source",
    "switchport protected",
    "storm-control broadcast",
    "storm-control multicast",
]


def main():
    for device_name, commands in DEVICE_CONFIGS.items():
        print("=" * 80)
        print(device_name)
        print("=" * 80)

        current_interface = None

        for command in commands:
            if command.startswith("interface "):
                current_interface = command

            if any(command.startswith(item) for item in WATCH_COMMANDS):
                if current_interface:
                    print(current_interface)
                else:
                    print("global")
                print(" ", command)


if __name__ == "__main__":
    main()