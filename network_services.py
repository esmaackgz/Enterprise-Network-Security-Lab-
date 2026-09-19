SERVER_URL = "http://100.98.251.22:80"
PROJECT_ID = "1c320728-4402-4ddf-930e-a99dc604e277"


USERNAME = "esma"
PASSWORD = "esma123"
ENABLE_SECRET = "esma123"


DOMAIN_NAME = "corp.local"

SYSLOG_SERVER = "10.10.100.11"

NTP_SERVERS = [
    "10.10.140.31",
    "10.10.140.32",
]

AD_ADMIN_USERNAME = "Administrator"
AD_ADMIN_PASSWORD = "CorpLab2026!"

SNMP_LOCATION = "GNS3-Lab"
SNMP_CONTACT = "admin/corp.local"

MONITORING_SNMP_HOSTS = [
    "10.10.60.10",  # Prometheus
    "10.10.60.11",  # Zabbix
]

SNMPV3_USER = "monitor"
SNMPV3_AUTH_PASSWORD = "corpLabMon"
SNMPV3_PRIV_PASSWORD = "corpLabMon"