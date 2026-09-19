import shlex

from network_services import AD_ADMIN_PASSWORD
from server_console import (
    open_server_console,
    run_checked,
    run_command,
)


SERVER_NAME = "AD-DC2"
HOSTNAME = "ad-dc2"
FQDN = "ad-dc2.corp.local"
SERVER_IP = "10.10.130.12"

PRIMARY_DC_IP = "10.10.130.11"
PRIMARY_DC_FQDN = "ad-dc1.corp.local"

REALM = "CORP.LOCAL"
DNS_DOMAIN = "corp.local"
NETBIOS_DOMAIN = "CORP"


def write_remote_file(connection, path, content):
    quoted_content = shlex.quote(content)
    quoted_path = shlex.quote(path)

    run_checked(
        connection,
        f"printf %s {quoted_content} | sudo -n tee {quoted_path} >/dev/null",
    )


def configure_hosts_file(connection):
    hosts_content = f"""127.0.0.1 localhost
{PRIMARY_DC_IP} {PRIMARY_DC_FQDN} ad-dc1
{SERVER_IP} {FQDN} {HOSTNAME}

::1 localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
"""
    write_remote_file(connection, "/etc/hosts", hosts_content)


def configure_resolver_for_join(connection):
    resolv_conf = f"""nameserver {PRIMARY_DC_IP}
search {DNS_DOMAIN}
"""
    run_checked(connection, "sudo -n rm -f /etc/resolv.conf")
    write_remote_file(connection, "/etc/resolv.conf", resolv_conf)

    run_checked(connection, "timeout 15 host -t A corp.local 10.10.130.11")
    run_checked(connection, "timeout 15 host -t SRV _ldap._tcp.corp.local 10.10.130.11")
    run_checked(connection, "timeout 15 host -t SRV _kerberos._udp.corp.local 10.10.130.11")
    run_checked(connection, "timeout 15 getent ahostsv4 archive.ubuntu.com")


def install_packages(connection):
    apt_options = (
        "-o Acquire::ForceIPv4=true "
        "-o Acquire::Retries=1 "
        "-o Acquire::http::Timeout=20 "
        "-o Acquire::https::Timeout=20 "
    )

    run_checked(
        connection,
        "sudo -n systemctl disable --now apt-daily.timer apt-daily-upgrade.timer || true",
        timeout=60,
    )
    run_checked(
        connection,
        "sudo -n systemctl stop apt-daily.service apt-daily-upgrade.service || true",
        timeout=60,
    )
    run_checked(connection, "sudo -n dpkg --configure -a", timeout=180)

    run_checked(
        connection,
        f"sudo -n apt-get {apt_options} update",
        timeout=900,
    )

    run_checked(
        connection,
        "sudo -n DEBIAN_FRONTEND=noninteractive "
        f"apt-get {apt_options} install -y samba-ad-dc krb5-user dnsutils smbclient",
        timeout=1200,
    )


def disable_conflicting_services(connection):
    run_checked(connection, "sudo -n systemctl disable --now smbd nmbd winbind systemd-resolved || true")
    run_checked(connection, "sudo -n systemctl mask smbd nmbd winbind || true")
    run_checked(connection, "sudo -n systemctl unmask samba-ad-dc || true")


def samba_is_joined(connection):
    output = run_checked(connection, "test -f /var/lib/samba/private/sam.ldb && echo YES || echo NO")
    return "YES" in output


def run_sensitive_checked(connection, command, redacted_command, timeout=30):
    output, exit_code = run_command(connection, command, timeout=timeout)

    print(f"\n$ {redacted_command}")

    if output:
        print(output)

    print("Exit code:", exit_code)

    if exit_code != 0:
        raise RuntimeError(f"Komut basarisiz: {redacted_command}")

    return output


def join_domain_as_dc(connection):
    command_parts = [
        "sudo",
        "-n",
        "samba-tool",
        "domain",
        "join",
        DNS_DOMAIN,
        "DC",
        f"--realm={REALM}",
        "--dns-backend=SAMBA_INTERNAL",
        "-U",
        f"{NETBIOS_DOMAIN}\\Administrator%{AD_ADMIN_PASSWORD}",
        "--option=interfaces=lo ens3",
        "--option=bind interfaces only=yes",
    ]

    redacted_parts = [
        f"{NETBIOS_DOMAIN}\\Administrator%********"
        if part.startswith(f"{NETBIOS_DOMAIN}\\Administrator%")
        else part
        for part in command_parts
    ]

    command = " ".join(shlex.quote(part) for part in command_parts)
    redacted_command = " ".join(shlex.quote(part) for part in redacted_parts)

    print("AD-DC2 mevcut domaine DC olarak join oluyor...")
    run_sensitive_checked(connection, command, redacted_command, timeout=1200)


def configure_final_resolver(connection):
    resolv_conf = f"""nameserver 127.0.0.1
nameserver {SERVER_IP}
nameserver {PRIMARY_DC_IP}
search {DNS_DOMAIN}
"""
    run_checked(connection, "sudo -n rm -f /etc/resolv.conf")
    write_remote_file(connection, "/etc/resolv.conf", resolv_conf)


def start_and_verify(connection):
    run_checked(connection, "sudo -n cp /var/lib/samba/private/krb5.conf /etc/krb5.conf")
    run_checked(connection, "sudo -n systemctl enable --now samba-ad-dc", timeout=120)
    run_checked(connection, "sudo -n systemctl restart samba-ad-dc", timeout=120)

    run_checked(connection, "hostname")
    run_checked(connection, "hostname -f")
    run_checked(connection, "sudo -n systemctl is-active samba-ad-dc")

    run_checked(connection, "sudo -n samba_dnsupdate --verbose", timeout=180)

    run_checked(connection, "host -t A ad-dc1.corp.local 127.0.0.1")
    run_checked(connection, "host -t A ad-dc2.corp.local 127.0.0.1")
    run_checked(connection, "host -t A corp.local 127.0.0.1")
    run_checked(connection, "host -t SRV _ldap._tcp.corp.local 127.0.0.1")
    run_checked(connection, "host -t SRV _kerberos._udp.corp.local 127.0.0.1")

    run_checked(connection, "sudo -n samba-tool drs showrepl", timeout=180)
    run_checked(connection, "smbclient -L localhost -N")
    run_checked(connection, "sudo -n ss -lntup | grep ':53'")


def configure_ad_dc2(connection):
    print("AD-DC2 kurulumu basliyor...")

    run_checked(connection, f"sudo -n hostnamectl set-hostname {HOSTNAME}")
    configure_hosts_file(connection)
    configure_resolver_for_join(connection)

    install_packages(connection)
    disable_conflicting_services(connection)

    if samba_is_joined(connection):
        print("AD-DC2 daha once domaine katilmis, join adimi atlandi.")
    else:
        run_checked(connection, "sudo -n mv /etc/samba/smb.conf /etc/samba/smb.conf.before-ad-dc2 2>/dev/null || true")
        join_domain_as_dc(connection)

    configure_final_resolver(connection)
    start_and_verify(connection)

    print("OK: AD-DC2 mevcut CORP.LOCAL domainine ikinci DC olarak katildi.")


def main():
    if not AD_ADMIN_PASSWORD:
        raise SystemExit("AD_ADMIN_PASSWORD network_services.py icinde bos olamaz.")

    with open_server_console(SERVER_NAME) as connection:
        configure_ad_dc2(connection)


if __name__ == "__main__":
    main()