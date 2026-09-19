SERVERS = [
    # Identity services - VLAN130
    {
        "name": "AD-DC1",
        "hostname": "ad-dc1",
        "ip": "10.10.130.11",
        "prefix": 24,
        "gateway": "10.10.130.1",
    },
    {
        "name": "AD-DC2",
        "hostname": "ad-dc2",
        "ip": "10.10.130.12",
        "prefix": 24,
        "gateway": "10.10.130.1",
    },
    {
        "name": "DNS1",
        "hostname": "dns1",
        "ip": "10.10.130.21",
        "prefix": 24,
        "gateway": "10.10.130.1",
    },
    {
        "name": "DNS2",
        "hostname": "dns2",
        "ip": "10.10.130.22",
        "prefix": 24,
        "gateway": "10.10.130.1",
    },
    {
        "name": "DHCP1",
        "hostname": "dhcp1",
        "ip": "10.10.130.31",
        "prefix": 24,
        "gateway": "10.10.130.1",
    },
    {
        "name": "DHCP2",
        "hostname": "dhcp2",
        "ip": "10.10.130.32",
        "prefix": 24,
        "gateway": "10.10.130.1",
    },

    # Server VLAN20
    {
        "name": "APP1",
        "hostname": "app1",
        "ip": "10.10.20.21",
        "prefix": 24,
        "gateway": "10.10.20.1",
    },
    {
        "name": "APP2",
        "hostname": "app2",
        "ip": "10.10.20.22",
        "prefix": 24,
        "gateway": "10.10.20.1",
    },

    # Authentication and NTP - VLAN140
    {
        "name": "RADIUS1",
        "hostname": "radius1",
        "ip": "10.10.140.11",
        "prefix": 24,
        "gateway": "10.10.140.1",
    },
    {
        "name": "RADIUS2",
        "hostname": "radius2",
        "ip": "10.10.140.12",
        "prefix": 24,
        "gateway": "10.10.140.1",
    },
    {
        "name": "TACACS1",
        "hostname": "tacacs1",
        "ip": "10.10.140.21",
        "prefix": 24,
        "gateway": "10.10.140.1",
    },
    {
        "name": "TACACS2",
        "hostname": "tacacs2",
        "ip": "10.10.140.22",
        "prefix": 24,
        "gateway": "10.10.140.1",
    },
    {
        "name": "NTP1",
        "hostname": "ntp1",
        "ip": "10.10.140.31",
        "prefix": 24,
        "gateway": "10.10.140.1",
    },
    {
        "name": "NTP2",
        "hostname": "ntp2",
        "ip": "10.10.140.32",
        "prefix": 24,
        "gateway": "10.10.140.1",
    },

    # Monitoring - VLAN60
    {
        "name": "MONITOR-ZABBIX",
        "hostname": "monitor-zabbix",
        "ip": "10.10.60.10",
        "prefix": 24,
        "gateway": "10.10.60.1",
    },
    {
        "name": "PROMETHEUS",
        "hostname": "prometheus",
        "ip": "10.10.60.11",
        "prefix": 24,
        "gateway": "10.10.60.1",
    },
    {
        "name": "GRAFANA",
        "hostname": "grafana",
        "ip": "10.10.60.12",
        "prefix": 24,
        "gateway": "10.10.60.1",
    },
    {
        "name": "NETFLOW-COLLECTOR",
        "hostname": "netflow-collector",
        "ip": "10.10.60.13",
        "prefix": 24,
        "gateway": "10.10.60.1",
    },

    # Security tools - VLAN100
    {
        "name": "LOG-SIEM-WAZUH",
        "hostname": "log-siem-wazuh",
        "ip": "10.10.100.10",
        "prefix": 24,
        "gateway": "10.10.100.1",
    },
    {
        "name": "GRAYLOG",
        "hostname": "graylog",
        "ip": "10.10.100.11",
        "prefix": 24,
        "gateway": "10.10.100.1",
    },
    {
        "name": "IDS-SURICATA",
        "hostname": "ids-suricata",
        "ip": "10.10.100.20",
        "prefix": 24,
        "gateway": "10.10.100.1",
    },
    {
        "name": "IDS-ZEEK",
        "hostname": "ids-zeek",
        "ip": "10.10.100.21",
        "prefix": 24,
        "gateway": "10.10.100.1",
    },

    # Load balancer and database
    {
        "name": "LB1",
        "hostname": "lb1",
        "ip": "10.10.110.11",
        "prefix": 24,
        "gateway": "10.10.110.1",
    },
    {
        "name": "LB2",
        "hostname": "lb2",
        "ip": "10.10.110.12",
        "prefix": 24,
        "gateway": "10.10.110.1",
    },
    {
        "name": "DB1",
        "hostname": "db1",
        "ip": "10.10.120.11",
        "prefix": 24,
        "gateway": "10.10.120.1",
    },
    {
        "name": "DB2",
        "hostname": "db2",
        "ip": "10.10.120.12",
        "prefix": 24,
        "gateway": "10.10.120.1",
    },

    # Management and backup
    {
        "name": "NETBOX",
        "hostname": "netbox",
        "ip": "10.10.50.100",
        "prefix": 24,
        "gateway": "10.10.50.1",
    },
    {
        "name": "JUMPBOX",
        "hostname": "jumpbox",
        "ip": "10.10.50.101",
        "prefix": 24,
        "gateway": "10.10.50.1",
    },
    {
        "name": "CONFIG-BACKUP",
        "hostname": "config-backup",
        "ip": "10.10.50.102",
        "prefix": 24,
        "gateway": "10.10.50.1",
    },
    {
        "name": "BACKUP",
        "hostname": "backup",
        "ip": "10.10.70.11",
        "prefix": 24,
        "gateway": "10.10.70.1",
    },

    # DMZ - VLAN80
    {
        "name": "WEB1-DMZ",
        "hostname": "web1-dmz",
        "ip": "10.10.80.11",
        "prefix": 24,
        "gateway": "10.10.80.1",
    },
    {
        "name": "WEB2-DMZ",
        "hostname": "web2-dmz",
        "ip": "10.10.80.12",
        "prefix": 24,
        "gateway": "10.10.80.1",
    },
    {
        "name": "WAF-LB1",
        "hostname": "waf-lb1",
        "ip": "10.10.80.21",
        "prefix": 24,
        "gateway": "10.10.80.1",
    },
    {
        "name": "WAF-LB2",
        "hostname": "waf-lb2",
        "ip": "10.10.80.22",
        "prefix": 24,
        "gateway": "10.10.80.1",
    },
    {
        "name": "PUBLIC-DNS1",
        "hostname": "public-dns1",
        "ip": "10.10.80.53",
        "prefix": 24,
        "gateway": "10.10.80.1",
    },
    {
        "name": "VPN-GW",
        "hostname": "vpn-gw",
        "ip": "10.10.80.60",
        "prefix": 24,
        "gateway": "10.10.80.1",
    },
]
