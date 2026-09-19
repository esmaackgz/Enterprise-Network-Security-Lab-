LINKS = [

    # WAN
    {"a": ("ISP1", "Gi0/0"), "b": ("EDGE-R1", "Gi0/0")},
    {"a": ("ISP2", "Gi0/0"), "b": ("EDGE-R2", "Gi0/0")},
    {"a": ("EDGE-R1", "Gi0/2"), "b": ("EDGE-R2", "Gi0/2"), "desc": "EDGE routing crosslink"},
    # Edge to firewall
    {"a": ("EDGE-R1", "Gi0/1"), "b": ("FW1", "em0")},
    {"a": ("EDGE-R2", "Gi0/1"), "b": ("FW1", "em4"),"desc": "FW1 backup WAN via EDGE-R2"},
    {"a": ("EDGE-R1", "Gi0/3"), "b": ("FW2", "em0")},
    {"a": ("EDGE-R2", "Gi0/3"), "b": ("FW2", "em4"),"desc": "FW2 backup WAN via EDGE-R2"},

    # Firewall HA
    {"a": ("FW1", "em1"), "b": ("FW2", "em1")},

    # Firewall to core - internal VLAN trunk
    {"a": ("FW1", "em2"), "b": ("CORE-SW1", "Gi0/0")},
    {"a": ("FW2", "em2"), "b": ("CORE-SW2", "Gi0/0")},

    # Core to core - EtherChannel member links
    {"a": ("CORE-SW1", "Gi0/1"), "b": ("CORE-SW2", "Gi0/1")},
    {"a": ("CORE-SW1", "Gi0/2"), "b": ("CORE-SW2", "Gi0/2")},

    # Access switch uplinks
    {"a": ("ACCESS-SW1", "Gi0/0"), "b": ("CORE-SW1", "Gi0/3")},
    {"a": ("ACCESS-SW1", "Gi0/1"), "b": ("CORE-SW2", "Gi0/3")},

    {"a": ("ACCESS-SW2", "Gi0/0"), "b": ("CORE-SW1", "Gi3/0")},
    {"a": ("ACCESS-SW2", "Gi0/1"), "b": ("CORE-SW2", "Gi3/0")},

    # Server switch uplinks
    {"a": ("SERVER-SW1", "Gi0/0"), "b": ("CORE-SW1", "Gi3/1")},
    {"a": ("SERVER-SW1", "Gi0/1"), "b": ("CORE-SW2", "Gi3/1")},

    {"a": ("SERVER-SW2", "Gi0/0"), "b": ("CORE-SW1", "Gi3/2")},
    {"a": ("SERVER-SW2", "Gi0/1"), "b": ("CORE-SW2", "Gi3/2")},

    # Management switch uplinks
    {"a": ("MGMT-SW", "Gi0/0"), "b": ("CORE-SW1", "Gi3/3")},
    {"a": ("MGMT-SW", "Gi0/1"), "b": ("CORE-SW2", "Gi3/3")},

    # DMZ
    {"a": ("FW1", "em3"), "b": ("DMZ-SW1", "Gi0/0")},
    {"a": ("FW2", "em3"), "b": ("DMZ-SW2", "Gi0/0")},
    {"a": ("DMZ-SW1", "Gi0/1"), "b": ("DMZ-SW2", "Gi0/1")},
    {"a": ("DMZ-SW1", "Gi0/2"), "b": ("DMZ-SW2", "Gi0/2")},






    # Access clients - Toolbox eth0
    {"a": ("USER-PC1", "eth0"), "b": ("ACCESS-SW1", "Gi0/2")},
    {"a": ("USER-PC2", "eth0"), "b": ("ACCESS-SW1", "Gi0/3")},
    {"a": ("USER-PC3", "eth0"), "b": ("ACCESS-SW2", "Gi1/0")},

    {"a": ("VOICE-PC1", "eth0"), "b": ("ACCESS-SW1", "Gi1/1")},
    {"a": ("VOICE-PC2", "eth0"), "b": ("ACCESS-SW2", "Gi1/1")},

    {"a": ("PRINTER1", "eth0"), "b": ("ACCESS-SW1", "Gi1/0")},
    {"a": ("CAMERA1", "eth0"), "b": ("ACCESS-SW1", "Gi1/2")},

    {"a": ("GUEST-PC1", "eth0"), "b": ("ACCESS-SW2", "Gi0/2")},
    {"a": ("GUEST-PC2", "eth0"), "b": ("ACCESS-SW2", "Gi0/3")},

    # Management - VLAN50 / VLAN70
    {"a": ("ADMIN-PC1", "eth0"), "b": ("MGMT-SW", "Gi0/2")},
    {"a": ("HELPDESK-PC1", "eth0"), "b": ("MGMT-SW", "Gi0/3")},

    {"a": ("NETBOX", "Ethernet0"), "b": ("MGMT-SW", "Gi1/0")},
    {"a": ("JUMPBOX", "Ethernet0"), "b": ("MGMT-SW", "Gi1/1")},
    {"a": ("CONFIG-BACKUP", "Ethernet0"), "b": ("MGMT-SW", "Gi1/2")},
    {"a": ("BACKUP", "Ethernet0"), "b": ("MGMT-SW", "Gi1/3")},


    # Server services - primary side
    {"a": ("AD-DC1", "Ethernet0"), "b": ("SERVER-SW1", "Gi2/0")},
    {"a": ("DNS1", "Ethernet0"), "b": ("SERVER-SW1", "Gi2/1")},
    {"a": ("DHCP1", "Ethernet0"), "b": ("SERVER-SW1", "Gi2/2")},

    {"a": ("RADIUS1", "Ethernet0"), "b": ("SERVER-SW1", "Gi1/1")},
    {"a": ("TACACS1", "Ethernet0"), "b": ("SERVER-SW1", "Gi1/2")},
    {"a": ("NTP1", "Ethernet0"), "b": ("SERVER-SW1", "Gi1/3")},

    {"a": ("LB1", "Ethernet0"), "b": ("SERVER-SW1", "Gi1/0")},
    {"a": ("APP1", "Ethernet0"), "b": ("SERVER-SW1", "Gi0/2")},
    {"a": ("DB1", "Ethernet0"), "b": ("SERVER-SW1", "Gi0/3")},

    {"a": ("MONITOR-ZABBIX", "Ethernet0"), "b": ("SERVER-SW1", "Gi3/1")},
    {"a": ("PROMETHEUS", "Ethernet0"), "b": ("SERVER-SW1", "Gi3/0")},

    {"a": ("LOG-SIEM-WAZUH", "Ethernet0"), "b": ("SERVER-SW1", "Gi3/3")},
    {"a": ("IDS-SURICATA", "Ethernet0"), "b": ("SERVER-SW1", "Gi3/2")},

    # Server services - secondary side
    {"a": ("AD-DC2", "Ethernet0"), "b": ("SERVER-SW2", "Gi2/0")},
    {"a": ("DNS2", "Ethernet0"), "b": ("SERVER-SW2", "Gi2/1")},
    {"a": ("DHCP2", "Ethernet0"), "b": ("SERVER-SW2", "Gi2/2")},

    {"a": ("RADIUS2", "Ethernet0"), "b": ("SERVER-SW2", "Gi1/1")},
    {"a": ("TACACS2", "Ethernet0"), "b": ("SERVER-SW2", "Gi1/2")},
    {"a": ("NTP2", "Ethernet0"), "b": ("SERVER-SW2", "Gi1/3")},

    {"a": ("LB2", "Ethernet0"), "b": ("SERVER-SW2", "Gi1/0")},
    {"a": ("APP2", "Ethernet0"), "b": ("SERVER-SW2", "Gi0/2")},
    {"a": ("DB2", "Ethernet0"), "b": ("SERVER-SW2", "Gi0/3")},

    {"a": ("GRAFANA", "Ethernet0"), "b": ("SERVER-SW2", "Gi3/1")},
    {"a": ("NETFLOW-COLLECTOR", "Ethernet0"), "b": ("SERVER-SW2", "Gi3/0")},

    {"a": ("GRAYLOG", "Ethernet0"), "b": ("SERVER-SW2", "Gi3/3")},
    {"a": ("IDS-ZEEK", "Ethernet0"), "b": ("SERVER-SW2", "Gi3/2")},

    # DMZ server connections
    {"a": ("WEB1-DMZ", "Ethernet0"), "b": ("DMZ-SW1", "Gi1/0")},
    {"a": ("WAF-LB1", "Ethernet0"), "b": ("DMZ-SW1", "Gi1/1")},
    {"a": ("PUBLIC-DNS1", "Ethernet0"), "b": ("DMZ-SW1", "Gi1/2")},

    {"a": ("WEB2-DMZ", "Ethernet0"), "b": ("DMZ-SW2", "Gi1/0")},
    {"a": ("WAF-LB2", "Ethernet0"), "b": ("DMZ-SW2", "Gi1/1")},
    {"a": ("VPN-GW", "Ethernet0"), "b": ("DMZ-SW2", "Gi1/2")},



]

ROUTER = "Cisco IOSv 15.9M6"
SWITCH = "Cisco IOSvL2 15.2(20200924:215240)"
FIREWALL = "pfSense 2.7.0"
SERVER = "Ubuntu Cloud Guest Ubuntu 24.04 LTS (Noble Numbat)"
PC = "Toolbox"


NETWORK_NODES = [
    {"name": "ISP1", "template_name": ROUTER, "x": -600, "y": -570},
    {"name": "ISP2", "template_name": ROUTER, "x": 230, "y": -570},
    {"name": "EDGE-R1", "template_name": ROUTER, "x": -460, "y": -480},
    {"name": "EDGE-R2", "template_name": ROUTER, "x": 80, "y": -480},
    {"name": "FW1", "template_name": FIREWALL, "x": -300, "y": -400},
    {"name": "FW2", "template_name": FIREWALL, "x": -100, "y": -400},
    {"name": "CORE-SW1", "template_name": SWITCH, "x": -350, "y": -250},
    {"name": "CORE-SW2", "template_name": SWITCH, "x": -60, "y": -250},
    {"name": "ACCESS-SW1", "template_name": SWITCH, "x": -1100, "y": -50},
    {"name": "ACCESS-SW2", "template_name": SWITCH, "x": -900, "y": -50},
    {"name": "SERVER-SW1", "template_name": SWITCH, "x": -500, "y": -50},
    {"name": "SERVER-SW2", "template_name": SWITCH, "x": -150, "y": -50},
    {"name": "DMZ-SW1", "template_name": SWITCH, "x": 670, "y": -470},
    {"name": "DMZ-SW2", "template_name": SWITCH, "x": 880, "y": -470},
    {"name": "MGMT-SW", "template_name": SWITCH, "x": 750, "y": -50},
]
DMZ_NODES = [
    {"name": "WAF-LB1", "template_name": SERVER, "x": 680, "y": -290},
    {"name": "WAF-LB2", "template_name": SERVER, "x": 880, "y": -290},
    {"name": "WEB1-DMZ", "template_name": SERVER, "x": 620, "y": -380},
    {"name": "WEB2-DMZ", "template_name": SERVER, "x": 720, "y": -380},
    {"name": "PUBLIC-DNS1", "template_name": SERVER, "x": 840, "y": -380},
    {"name": "VPN-GW", "template_name": SERVER, "x": 940, "y": -380},
]
SERVER_NODES = [
    {"name": "AD-DC1", "template_name": SERVER, "x": -700, "y": 70},
    {"name": "AD-DC2", "template_name": SERVER, "x": -600, "y": 70},
    {"name": "DNS1", "template_name": SERVER, "x": -700, "y": 160},
    {"name": "DNS2", "template_name": SERVER, "x": -600, "y": 160},
    {"name": "DHCP1", "template_name": SERVER, "x": -700, "y": 250},
    {"name": "DHCP2", "template_name": SERVER, "x": -600, "y": 250},
    {"name": "RADIUS1", "template_name": SERVER, "x": -450, "y": 70},
    {"name": "RADIUS2", "template_name": SERVER, "x": -350, "y": 70},
    {"name": "TACACS1", "template_name": SERVER, "x": -450, "y": 160},
    {"name": "TACACS2", "template_name": SERVER, "x": -350, "y": 160},
    {"name": "NTP1", "template_name": SERVER, "x": -450, "y": 250},
    {"name": "NTP2", "template_name": SERVER, "x": -350, "y": 250},
    {"name": "LB1", "template_name": SERVER, "x": -200, "y": 70},
    {"name": "LB2", "template_name": SERVER, "x": -100, "y": 70},
    {"name": "APP1", "template_name": SERVER, "x": -200, "y": 160},
    {"name": "APP2", "template_name": SERVER, "x": -100, "y": 160},
    {"name": "DB1", "template_name": SERVER, "x": -200, "y": 250},
    {"name": "DB2", "template_name": SERVER, "x": -100, "y": 250},
]
MONITORING_SECURITY_NODES = [
    {"name": "MONITOR-ZABBIX", "template_name": SERVER, "x": 180, "y": 70},
    {"name": "PROMETHEUS", "template_name": SERVER, "x": 300, "y": 70},
    {"name": "GRAFANA", "template_name": SERVER, "x": 180, "y": 170},
    {"name": "LOG-SIEM-WAZUH", "template_name": SERVER, "x": 300, "y": 170},
    {"name": "GRAYLOG", "template_name": SERVER, "x": 180, "y": 270},
    {"name": "NETFLOW-COLLECTOR", "template_name": SERVER, "x": 300, "y": 270},
    {"name": "IDS-SURICATA", "template_name": SERVER, "x": 180, "y": 370},
    {"name": "IDS-ZEEK", "template_name": SERVER, "x": 300, "y": 370},
    {"name": "NETBOX", "template_name": SERVER, "x": 650, "y": 80},
    {"name": "BACKUP", "template_name": SERVER, "x": 750, "y": 180},
    {"name": "JUMPBOX", "template_name": SERVER, "x": 750, "y": 80},
    {"name": "CONFIG-BACKUP", "template_name": SERVER, "x": 650, "y": 180},
]
CLIENT_NODES = [

    {"name": "USER-PC1", "template_name": PC, "x": -1150, "y": 50},
    {"name": "USER-PC2", "template_name": PC, "x": -1150, "y": 130},
    {"name": "USER-PC3", "template_name": PC, "x": -1150, "y": 210},

    {"name": "VOICE-PC1", "template_name": PC, "x": -1150, "y": 320},
    {"name": "VOICE-PC2", "template_name": PC, "x": -1150, "y": 400},

    {"name": "PRINTER1", "template_name": PC, "x": -1060, "y": 50},
    {"name": "CAMERA1", "template_name": PC, "x": -1060, "y": 130},

    {"name": "ADMIN-PC1", "template_name": PC, "x": -900, "y": 50},
    {"name": "HELPDESK-PC1", "template_name": PC, "x": -900, "y": 130},

    {"name": "GUEST-PC1", "template_name": PC, "x": 810, "y": 50},
    {"name": "GUEST-PC2", "template_name": PC, "x": 810, "y": 130},
]


NODES = NETWORK_NODES + DMZ_NODES + SERVER_NODES + MONITORING_SECURITY_NODES + CLIENT_NODES

