import time

from gns3_client import gns3_request
from network_services import SERVER_URL, PROJECT_ID

TARGET_NODES = [

    "ACCESS-SW1",
    "ACCESS-SW2",
# Omurga
    "CORE-SW1",
    "CORE-SW2",
    "SERVER-SW1",
    "SERVER-SW2",
    "MGMT-SW",
    "DMZ-SW1",
    "DMZ-SW2",

    # WAN
    "ISP1",
    "ISP2",
    "EDGE-R1",
    "EDGE-R2",
]


def main():
    nodes = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes",
    )

    nodes_by_name = {
        node["name"]: node
        for node in nodes
    }

    for name in TARGET_NODES:
        node = nodes_by_name.get(name)

        if not node:
            print(f"[HATA] Node bulunamadi: {name}")
            continue

        if node["status"] == "started":
            print(f"OK: {name} zaten acik.")
            continue

        print(f"{name} baslatiliyor...")

        gns3_request(
            SERVER_URL,
            "POST",
            f"/v2/projects/{PROJECT_ID}/nodes/{node['node_id']}/start",
        )

        print(f"OK: {name} start komutu gonderildi.")

    print("OK: DHCP test client node start islemi tamamlandi.")


if __name__ == "__main__":
    main()



""" 
    "AD-DC1",
    "AD-DC2",
    "DHCP1",
    "DHCP2",


    # Firewall
    "FW1",
    "FW2",

    

    # Şu an çalışacağımız serverlar
    "DNS1",
    "DNS2",
    "NTP1",
    "NTP2",

    
    "USER-PC1",
    "USER-PC2",
    "USER-PC3",
    "GUEST-PC1",
    "GUEST-PC2",
    "VOICE-PC1",
    "VOICE-PC2",
    "PRINTER1",
    "CAMERA1",
    


def get_nodes():
    nodes = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes",
    )
    return {node["name"]: node for node in nodes}


def start_node(node):
    if node.get("status") == "started":
        print(f"Zaten calisiyor: {node['name']}")
        return

    gns3_request(
        SERVER_URL,
        "POST",
        f"/v2/projects/{PROJECT_ID}/nodes/{node['node_id']}/start",
    )
    print(f"Baslatma istegi gonderildi: {node['name']}")


def main():
    target_names = TARGET_NODES
    nodes_by_name = get_nodes()
    missing = []

    for name in target_names:
        node = nodes_by_name.get(name)

        if not node:
            missing.append(name)
            print(f"Node bulunamadi: {name}")
            continue

        start_node(node)

    time.sleep(5)
    refreshed_nodes = get_nodes()

    print("\nSON DURUM")
    print("=" * 45)

    for name in target_names:
        node = refreshed_nodes.get(name)

        if node:
            print(f"{name:<22} {node.get('status')}")

    if missing:
        print("\nBulunamayanlar:", ", ".join(missing))


if __name__ == "__main__":
    main()

"""