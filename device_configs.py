from network_services import ( MONITORING_SNMP_HOSTS, NTP_SERVERS, SNMP_CONTACT, SNMP_LOCATION, SNMPV3_AUTH_PASSWORD,
    SNMPV3_PRIV_PASSWORD, SNMPV3_USER, SYSLOG_SERVER,)

from network_services import DOMAIN_NAME, USERNAME, PASSWORD, ENABLE_SECRET

MGMT_MASK = "255.255.255.0"
MGMT_GATEWAY = "10.10.50.1"
DMZ_MGMT_GATEWAY = "10.10.85.1"
NATIVE_VLAN = 998
UNUSED_VLAN = 999
STP_MODE = "rapid-pvst"


MGMT_ALLOWED_NETWORKS = [
    ("10.10.50.0", "0.0.0.255"),  # Management VLAN
    ("10.10.90.0", "0.0.0.255"),  # Admin VLAN
]

VLANS = {
    10: "USER",
    20: "SERVER",
    30: "VOICE",
    35: "PRINTER",
    36: "IOT-CAMERA",
    40: "GUEST",
    50: "MANAGEMENT",
    60: "MONITORING",
    70: "BACKUP",
    80: "DMZ",
    85: "DMZ-MANAGEMENT",
    90: "ADMIN",
    100: "SECURITY-IDS",
    110: "LOAD-BALANCER",
    120: "DATABASE",
    130: "IDENTITY",
    140: "AUTH-NTP",
    998: "NATIVE-BLACKHOLE",
    999: "UNUSED-BLACKHOLE",
}


INTERNAL_VLANS = [10, 20, 30, 35, 36, 40, 50, 60, 70, 90, 100, 110, 120, 130, 140]
ACCESS_SW1_VLANS = [10, 30, 35, 36, 50]
ACCESS_SW2_VLANS = [10, 30, 40, 50]
SERVER_SW_VLANS = [20, 50, 60, 100, 110, 120, 130, 140]
MGMT_SW_VLANS = [50, 70, 90]
DMZ_VLANS = [80,85]

DHCP_SNOOPING_VLANS = [10, 30, 35, 36, 40]
DHCP_SNOOPING_RATE_LIMIT = 15

ALL_PORTS = [
    f"Gi{slot}/{port}"
    for slot in range(4)
    for port in range(4)
]


SWITCHES = {
    "CORE-SW1": {
        "mgmt_ip": "10.10.50.2",
        "mgmt_vlan": 50,
        "mgmt_gateway": MGMT_GATEWAY,
        "trunks": {
            "Gi0/0": {"description": "FW1_em2_INTERNAL_TRUNK", "vlans": INTERNAL_VLANS, "dhcp_snooping_trust": True, "arp_inspection_trust": True,},
            "Gi0/3": {"description": "TO_ACCESS-SW1", "vlans": ACCESS_SW1_VLANS, "dhcp_snooping_trust": True, "arp_inspection_trust": True,},
            "Gi3/0": {"description": "TO_ACCESS-SW2", "vlans": ACCESS_SW2_VLANS, "dhcp_snooping_trust": True, "arp_inspection_trust": True,},
            "Gi3/1": {"description": "TO_SERVER-SW1", "vlans": SERVER_SW_VLANS},
            "Gi3/2": {"description": "TO_SERVER-SW2", "vlans": SERVER_SW_VLANS},
            "Gi3/3": {"description": "TO_MGMT-SW", "vlans": MGMT_SW_VLANS},
        },
        "etherchannels": {
            "Port-channel1": {
                "description": "TO_CORE-SW2",
                "members": ["Gi0/1", "Gi0/2"],
                "vlans": INTERNAL_VLANS,
                "channel_group": 1,
                "dhcp_snooping_trust": True,
                "arp_inspection_trust": True,
            }
        },
        "access_ports": {},
        "stp_root_primary": [10, 30, 35, 36, 40, 50, 90, 130],
        "stp_root_secondary": [20, 60, 70, 100, 110, 120, 140],
    },
    "CORE-SW2": {
        "mgmt_ip": "10.10.50.3",
        "mgmt_vlan": 50,
        "mgmt_gateway": MGMT_GATEWAY,
        "trunks": {
            "Gi0/0": {"description": "FW2_em2_INTERNAL_TRUNK", "vlans": INTERNAL_VLANS, "dhcp_snooping_trust": True, "arp_inspection_trust": True,},
            "Gi0/3": {"description": "TO_ACCESS-SW1", "vlans": ACCESS_SW1_VLANS, "dhcp_snooping_trust": True, "arp_inspection_trust": True,},
            "Gi3/0": {"description": "TO_ACCESS-SW2", "vlans": ACCESS_SW2_VLANS, "dhcp_snooping_trust": True, "arp_inspection_trust": True,},
            "Gi3/1": {"description": "TO_SERVER-SW1", "vlans": SERVER_SW_VLANS},
            "Gi3/2": {"description": "TO_SERVER-SW2", "vlans": SERVER_SW_VLANS},
            "Gi3/3": {"description": "TO_MGMT-SW", "vlans": MGMT_SW_VLANS},
        },
        "etherchannels": {
            "Port-channel1": {
                "description": "TO_CORE-SW1",
                "members": ["Gi0/1", "Gi0/2"],
                "vlans": INTERNAL_VLANS,
                "channel_group": 1,
                "dhcp_snooping_trust": True,
                "arp_inspection_trust": True,
            }
        },
        "access_ports": {},
        "stp_root_primary": [20, 60, 70, 100, 110, 120, 140],
        "stp_root_secondary": [10, 30, 35, 36, 40, 50, 90, 130],
    },
    "ACCESS-SW1": {
        "mgmt_ip": "10.10.50.11",
        "mgmt_vlan": 50,
        "mgmt_gateway": MGMT_GATEWAY,
        "trunks": {
            "Gi0/0": {"description": "TO_CORE-SW1", "vlans": ACCESS_SW1_VLANS, "dhcp_snooping_trust": True, "arp_inspection_trust": True,},
            "Gi0/1": {"description": "TO_CORE-SW2", "vlans": ACCESS_SW1_VLANS, "dhcp_snooping_trust": True, "arp_inspection_trust": True,},
        },
        "etherchannels": {},
        "access_ports": {
            "Gi0/2": {"description": "USER-PC1", "vlan": 10, "protected": True},
            "Gi0/3": {"description": "USER-PC2", "vlan": 10, "protected": True},
            "Gi1/0": {"description": "PRINTER1", "vlan": 35, "protected": True},
            "Gi1/1": {"description": "VOICE-PC1", "vlan": 30, "protected": True},
            "Gi1/2": {"description": "CAMERA1", "vlan": 36, "protected": True},
        },
    },
    "ACCESS-SW2": {
        "mgmt_ip": "10.10.50.12",
        "mgmt_vlan": 50,
        "mgmt_gateway": MGMT_GATEWAY,
        "trunks": {
            "Gi0/0": {"description": "TO_CORE-SW1", "vlans": ACCESS_SW2_VLANS, "dhcp_snooping_trust": True, "arp_inspection_trust": True,},
            "Gi0/1": {"description": "TO_CORE-SW2", "vlans": ACCESS_SW2_VLANS, "dhcp_snooping_trust": True, "arp_inspection_trust": True,},
        },
        "etherchannels": {},
        "access_ports": {
            "Gi0/2": {"description": "GUEST-PC1", "vlan": 40, "protected": True},
            "Gi0/3": {"description": "GUEST-PC2", "vlan": 40, "protected": True},
            "Gi1/0": {"description": "USER-PC3", "vlan": 10, "protected": True},
            "Gi1/1": {"description": "VOICE-PC2", "vlan": 30, "protected": True},
        },
    },
    "SERVER-SW1": {
        "mgmt_ip": "10.10.50.21",
        "mgmt_vlan": 50,
        "mgmt_gateway": MGMT_GATEWAY,
        "trunks": {
            "Gi0/0": {"description": "TO_CORE-SW1", "vlans": SERVER_SW_VLANS},
            "Gi0/1": {"description": "TO_CORE-SW2", "vlans": SERVER_SW_VLANS},
        },
        "etherchannels": {},
        "access_ports": {
            "Gi0/2": {"description": "APP1", "vlan": 20},
            "Gi0/3": {"description": "DB1", "vlan": 120},
            "Gi1/0": {"description": "LB1", "vlan": 110, "max_mac": 2},
            "Gi1/1": {"description": "RADIUS1", "vlan": 140},
            "Gi1/2": {"description": "TACACS1", "vlan": 140},
            "Gi1/3": {"description": "NTP1", "vlan": 140},
            "Gi2/0": {"description": "AD-DC1", "vlan": 130},
            "Gi2/1": {"description": "DNS1", "vlan": 130},
            "Gi2/2": {"description": "DHCP1", "vlan": 130},
            "Gi3/0": {"description": "PROMETHEUS", "vlan": 60},
            "Gi3/1": {"description": "MONITOR-ZABBIX", "vlan": 60},
            "Gi3/2": {"description": "IDS-SURICATA", "vlan": 100},
            "Gi3/3": {"description": "LOG-SIEM-WAZUH", "vlan": 100},
        },
    },
    "SERVER-SW2": {
        "mgmt_ip": "10.10.50.22",
        "mgmt_vlan": 50,
        "mgmt_gateway": MGMT_GATEWAY,
        "trunks": {
            "Gi0/0": {"description": "TO_CORE-SW1", "vlans": SERVER_SW_VLANS},
            "Gi0/1": {"description": "TO_CORE-SW2", "vlans": SERVER_SW_VLANS},
        },
        "etherchannels": {},
        "access_ports": {
            "Gi0/2": {"description": "APP2", "vlan": 20},
            "Gi0/3": {"description": "DB2", "vlan": 120},
            "Gi1/0": {"description": "LB2", "vlan": 110, "max_mac": 2},
            "Gi1/1": {"description": "RADIUS2", "vlan": 140},
            "Gi1/2": {"description": "TACACS2", "vlan": 140},
            "Gi1/3": {"description": "NTP2", "vlan": 140},
            "Gi2/0": {"description": "AD-DC2", "vlan": 130},
            "Gi2/1": {"description": "DNS2", "vlan": 130},
            "Gi2/2": {"description": "DHCP2", "vlan": 130},
            "Gi3/0": {"description": "NETFLOW-COLLECTOR", "vlan": 60},
            "Gi3/1": {"description": "GRAFANA", "vlan": 60},
            "Gi3/2": {"description": "IDS-ZEEK", "vlan": 100},
            "Gi3/3": {"description": "GRAYLOG", "vlan": 100},
        },
    },
    "MGMT-SW": {
        "mgmt_ip": "10.10.50.31",
        "mgmt_vlan": 50,
        "mgmt_gateway": MGMT_GATEWAY,
        "trunks": {
            "Gi0/0": {"description": "TO_CORE-SW1", "vlans": MGMT_SW_VLANS},
            "Gi0/1": {"description": "TO_CORE-SW2", "vlans": MGMT_SW_VLANS},
        },
        "etherchannels": {},
        "access_ports": {
            "Gi0/2": {"description": "ADMIN-PC1", "vlan": 90},
            "Gi0/3": {"description": "HELPDESK-PC1", "vlan": 90},
            "Gi1/0": {"description": "NETBOX", "vlan": 50},
            "Gi1/1": {"description": "JUMPBOX", "vlan": 50},
            "Gi1/2": {"description": "CONFIG-BACKUP", "vlan": 50},
            "Gi1/3": {"description": "BACKUP", "vlan": 70},
        },
    },
    "DMZ-SW1": {
        "mgmt_ip": "10.10.85.11",
        "mgmt_vlan": 85,
        "mgmt_gateway": DMZ_MGMT_GATEWAY,
        "trunks": {
            "Gi0/0": {"description": "FW1_em3_DMZ", "vlans": DMZ_VLANS,
                      },
        },
        "etherchannels": {
            "Port-channel8": {
                "description": "TO_DMZ-SW2",
                "members": ["Gi0/1", "Gi0/2"],
                "vlans": DMZ_VLANS,
                "channel_group": 8,
            }
        },
        "access_ports": {
            "Gi1/0": {"description": "WEB1-DMZ", "vlan": 80},
            "Gi1/1": {"description": "WAF-LB1", "vlan": 80, "max_mac": 2},
            "Gi1/2": {"description": "PUBLIC-DNS1", "vlan": 80},
        },
    },
    "DMZ-SW2": {
        "mgmt_ip": "10.10.85.12",
        "mgmt_vlan": 85,
        "mgmt_gateway": DMZ_MGMT_GATEWAY,
        "trunks": {
            "Gi0/0": {"description": "FW2_em3_DMZ", "vlans": DMZ_VLANS,
                      },
        },
        "etherchannels": {
            "Port-channel8": {
                "description": "TO_DMZ-SW1",
                "members": ["Gi0/1", "Gi0/2"],
                "vlans": DMZ_VLANS,
                "channel_group": 8,
            }
        },
        "access_ports": {
            "Gi1/0": {"description": "WEB2-DMZ", "vlan": 80},
            "Gi1/1": {"description": "WAF-LB2", "vlan": 80, "max_mac": 2},
            "Gi1/2": {"description": "VPN-GW", "vlan": 80},
        },
    },
}

#VLAN ları listeye çevir. native VLAN yoksa ekler.
def vlan_csv(vlans, include_native=False):
    vlan_list = list(vlans)
    if include_native and NATIVE_VLAN not in vlan_list:
        vlan_list.append(NATIVE_VLAN)
    return ",".join(str(vlan_id) for vlan_id in sorted(vlan_list))

#switche eklenecek vlanları belirler
def get_required_vlan_ids(switch):
    vlan_ids = {switch["mgmt_vlan"], NATIVE_VLAN, UNUSED_VLAN}

    for trunk in switch["trunks"].values():
        vlan_ids.update(trunk["vlans"])

    for channel in switch["etherchannels"].values():
        vlan_ids.update(channel["vlans"])

    for access in switch["access_ports"].values():
        vlan_ids.add(access["vlan"])

    return sorted(vlan_ids)

#KONF HAZIR KOMUT. vlan ekle, ssh izni
def add_common_global_config(commands, hostname, switch):
    commands.extend([
        f"hostname {hostname}",
        "no ip routing",
        "service password-encryption",
        "service timestamps log datetime msec localtime show-timezone",
        f"enable secret {ENABLE_SECRET}",
        f"username {USERNAME} privilege 15 secret {PASSWORD}",
        f"spanning-tree mode {STP_MODE}",
        "no ip domain-lookup",
        f"ip domain-name {DOMAIN_NAME}",
        "ip ssh version 2",
        "ip ssh time-out 60",
        "ip ssh authentication-retries 3",
        "no ip http server",
        "no ip http secure-server",
        f"logging host {SYSLOG_SERVER}",
        "logging trap informational",
        f"logging source-interface Vlan{switch['mgmt_vlan']}",
        f"ntp source Vlan{switch['mgmt_vlan']}",
    ])

    for index, server in enumerate(NTP_SERVERS):
        prefer = " prefer" if index == 0 else ""
        commands.append(f"ntp server {server}{prefer}")

    required_vlans = set(get_required_vlan_ids(switch))
    dhcp_snooping_vlans = required_vlans.intersection(DHCP_SNOOPING_VLANS)

    if dhcp_snooping_vlans:
        commands.append("ip dhcp snooping")
        commands.append(f"ip dhcp snooping vlan {vlan_csv(dhcp_snooping_vlans)}")
        commands.append("no ip dhcp snooping information option")
        commands.append(f"ip arp inspection vlan {vlan_csv(dhcp_snooping_vlans)}")


    commands.append("ip access-list standard MONITORING-SNMP")

    for host in MONITORING_SNMP_HOSTS:
        commands.append(f"permit {host}")

    commands.extend([
        "deny any log",
        "exit",
        f"snmp-server location {SNMP_LOCATION}",
        f"snmp-server contact {SNMP_CONTACT}",
        "snmp-server view MONITORING iso included",
        "snmp-server group MONITORING v3 priv read MONITORING access MONITORING-SNMP",
        (
            f"snmp-server user {SNMPV3_USER} MONITORING v3 auth sha "
            f"{SNMPV3_AUTH_PASSWORD} priv aes 128 {SNMPV3_PRIV_PASSWORD} "
            "access MONITORING-SNMP"
        ),
    ])

    for vlan_id in get_required_vlan_ids(switch):
        vlan_name = VLANS[vlan_id]
        commands.append(f"vlan {vlan_id}")
        commands.append(f"name {vlan_name}")

    commands.append("ip access-list standard MANAGEMENT-VTY")

    for network, wildcard in MGMT_ALLOWED_NETWORKS:
        commands.append(f"permit {network} {wildcard}")

    commands.extend([
        "deny any log",
        "exit",
    ])

    commands.extend([
        "line vty 0 15",
        "access-class MANAGEMENT-VTY in",
        "login local",
        "transport input ssh",
        "exec-timeout 15 0",
        "exit",
    ])

#management vlan ip konf
def add_management_config(commands, switch):
    mgmt_vlan = switch["mgmt_vlan"]
    commands.extend([
        f"interface vlan {mgmt_vlan}",
        "description SWITCH_MANAGEMENT",
        f"ip address {switch['mgmt_ip']} {MGMT_MASK}",
        "no shutdown",
        "exit",
        f"ip default-gateway {switch['mgmt_gateway']}",
    ])

#trunk konfu
def add_trunk_config(commands, port, trunk):
    commands.extend([
        f"interface {port}",
        f"description {trunk['description']}",
        "switchport trunk encapsulation dot1q",
        "switchport mode trunk",
        f"switchport trunk native vlan {NATIVE_VLAN}",
        f"switchport trunk allowed vlan {vlan_csv(trunk['vlans'])}",
        "switchport nonegotiate",
    ])

    if trunk.get("dhcp_snooping_trust", False):
        commands.append("ip dhcp snooping trust")

    if trunk.get("arp_inspection_trust", False):
        commands.append("ip arp inspection trust")

    commands.extend([
        "no shutdown",
        "exit",
    ])

#etherchannel oluşturma
def add_etherchannel_config(commands, port_channel, channel):
    member_ports = ", ".join(channel["members"])

    commands.extend([
        f"interface {port_channel}",
        f"description {channel['description']}",
        "switchport trunk encapsulation dot1q",
        "switchport mode trunk",
        f"switchport trunk native vlan {NATIVE_VLAN}",
        f"switchport trunk allowed vlan {vlan_csv(channel['vlans'])}",
        "switchport nonegotiate",
    ])

    if channel.get("dhcp_snooping_trust", False):
        commands.append("ip dhcp snooping trust")

    if channel.get("arp_inspection_trust", False):
        commands.append("ip arp inspection trust")

    commands.extend([
        "no shutdown",
        "exit",

        f"interface range {member_ports}",
        "no switchport access vlan",
        "no spanning-tree bpduguard enable",
        f"description {channel['description']}_MEMBER",
        "switchport trunk encapsulation dot1q",
        "switchport mode trunk",
        f"switchport trunk native vlan {NATIVE_VLAN}",
        f"switchport trunk allowed vlan {vlan_csv(channel['vlans'])}",
        "switchport nonegotiate",
        f"channel-group {channel['channel_group']} mode active",
        "no shutdown",
        "exit",
    ])

#portları access yapma. port-security, stp konfu
def add_access_config(commands, port, access):
    commands.extend([
        f"interface {port}",
        f"description {access['description']}",
        "switchport mode access",
        f"switchport access vlan {access['vlan']}",
    ])

    if access.get("protected", False):
        commands.append("switchport protected")


    if access.get("port_security", True):
        commands.extend([
            "switchport port-security",
            f"switchport port-security maximum {access.get('max_mac', 1)}",
            "switchport port-security violation restrict",
            "switchport port-security mac-address sticky",
        ])
    else:
        commands.append("no switchport port-security")


    if access["vlan"] in DHCP_SNOOPING_VLANS:
        commands.append(f"ip dhcp snooping limit rate {DHCP_SNOOPING_RATE_LIMIT}")

    commands.extend([
        "spanning-tree portfast",
        "spanning-tree bpduguard enable",
        "no shutdown",
        "exit",
    ])

#kullanılmayan portları kapat
def add_unused_config(commands, port):
    commands.extend([
        f"interface {port}",
        "description UNUSED_PORT",
        "switchport mode access",
        f"switchport access vlan {UNUSED_VLAN}",
        "spanning-tree bpduguard enable",
        "shutdown",
        "exit",
    ])

#stp ayarları hangi sw root olacak. native_vlanı ekleme
def add_stp_root_config(commands, switch):
    primary = switch.get("stp_root_primary", [])
    secondary = switch.get("stp_root_secondary", [])

    if primary:
        commands.append(f"spanning-tree vlan {vlan_csv(primary, include_native=False)} root primary")
    if secondary:
        commands.append(f"spanning-tree vlan {vlan_csv(secondary, include_native=False)} root secondary")


def build_switch_config(hostname, switch):
    commands = []
    used_ports = set()

    add_common_global_config(commands, hostname, switch)
    add_management_config(commands, switch)
    add_stp_root_config(commands, switch)

    for port_channel, channel in switch["etherchannels"].items():
        add_etherchannel_config(commands, port_channel, channel)
        used_ports.update(channel["members"])

    for port, trunk in switch["trunks"].items():
        add_trunk_config(commands, port, trunk)
        used_ports.add(port)

    for port, access in switch["access_ports"].items():
        add_access_config(commands, port, access)
        used_ports.add(port)

    for port in ALL_PORTS:
        if port not in used_ports:
            add_unused_config(commands, port)

    return commands


DEVICE_CONFIGS = {
#    "DMZ-SW1": build_switch_config("DMZ-SW1", SWITCHES["DMZ-SW1"]),
#    "DMZ-SW2": build_switch_config("DMZ-SW2", SWITCHES["DMZ-SW2"]),
    hostname: build_switch_config(hostname, switch)
    for hostname, switch in SWITCHES.items()
}
