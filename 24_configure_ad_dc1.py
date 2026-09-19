import shlex

from network_services import AD_ADMIN_PASSWORD
from server_console import (
    open_server_console,
    run_checked,
    run_command,
)


SERVER_NAME = "AD-DC1"
HOSTNAME = "ad-dc1"
FQDN = "ad-dc1.corp.local"
SERVER_IP = "10.10.130.11"

REALM = "CORP.LOCAL"
DNS_DOMAIN = "corp.local"
NETBIOS_DOMAIN = "CORP"

DNS_FORWARDERS = ("10.10.130.21", "10.10.130.22")


def write_remote_file(connection, path, content):
    quoted_content = shlex.quote(content)
    quoted_path = shlex.quote(path)
    run_checked(
        connection,
        f"printf %s {quoted_content} | sudo -n tee {quoted_path} >/dev/null",
    )


def configure_hosts_file(connection):
    hosts_content = f"""127.0.0.1 localhost
{SERVER_IP} {FQDN} {HOSTNAME}

::1 localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
"""
    write_remote_file(connection, "/etc/hosts", hosts_content)


def set_install_dns(connection):
    resolv_conf = f"""nameserver {DNS_FORWARDERS[0]}
nameserver {DNS_FORWARDERS[1]}
search {DNS_DOMAIN}
"""

    run_checked(connection, "sudo -n rm -f /etc/resolv.conf")
    write_remote_file(connection, "/etc/resolv.conf", resolv_conf)

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
    run_checked(
        connection,
        "sudo -n dpkg --configure -a",
        timeout=180,
    )

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


def samba_is_provisioned(connection):
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


def provision_domain(connection):
    command_parts = [
        "sudo",
        "-n",
        "samba-tool",
        "domain",
        "provision",
        "--server-role=dc",
        "--use-rfc2307",
        "--dns-backend=SAMBA_INTERNAL",
        f"--realm={REALM}",
        f"--domain={NETBIOS_DOMAIN}",
        f"--adminpass={AD_ADMIN_PASSWORD}",
        "--option=interfaces=lo ens3",
        "--option=bind interfaces only=yes",
    ]

    redacted_parts = [
        "--adminpass=********" if part.startswith("--adminpass=") else part
        for part in command_parts
    ]

    command = " ".join(shlex.quote(part) for part in command_parts)
    redacted_command = " ".join(shlex.quote(part) for part in redacted_parts)

    print("Samba AD domain provision basliyor...")
    run_sensitive_checked(connection, command, redacted_command, timeout=900)

def configure_samba_dns_forwarders(connection):
    forwarders = f"{DNS_FORWARDERS[0]} {DNS_FORWARDERS[1]}"

    run_checked(
        connection,
        "sudo -n sed -i '/^[[:space:]]*dns forwarder[[:space:]]*=.*/d' /etc/samba/smb.conf",
    )
    run_checked(
        connection,
        f"sudo -n sed -i '/^\\[global\\]/a\\        dns forwarder = {forwarders}' /etc/samba/smb.conf",
    )


def configure_final_resolver(connection):
    resolv_conf = f"""nameserver 127.0.0.1
nameserver {SERVER_IP}
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
    run_checked(connection, "sudo -n systemctl status samba-ad-dc --no-pager")
    run_checked(connection, "host -t A corp.local 127.0.0.1")
    run_checked(connection, "host -t SRV _ldap._tcp.corp.local 127.0.0.1")
    run_checked(connection, "smbclient -L localhost -N")


def configure_ad_dc1(connection):
    print("AD-DC1 kurulumu basliyor...")

    run_checked(connection, f"sudo -n hostnamectl set-hostname {HOSTNAME}")
    configure_hosts_file(connection)

    set_install_dns(connection)
    install_packages(connection)
    disable_conflicting_services(connection)

    if samba_is_provisioned(connection):
        print("AD-DC1 daha once provision edilmis, domain provision atlandi.")
    else:
        run_checked(connection, "sudo -n mv /etc/samba/smb.conf /etc/samba/smb.conf.before-ad-dc1 2>/dev/null || true")
        provision_domain(connection)

    configure_samba_dns_forwarders(connection)
    configure_final_resolver(connection)
    start_and_verify(connection)

    print("OK: AD-DC1 Samba AD DNS kurulumu tamamlandi.")


def main():
    if not AD_ADMIN_PASSWORD:
        raise SystemExit("AD_ADMIN_PASSWORD network_services.py icinde bos olamaz.")


    with open_server_console(SERVER_NAME) as connection:
        configure_ad_dc1(connection)


if __name__ == "__main__":
    main()