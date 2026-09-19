from gns3_client import gns3_request
from topology_data import LINKS
from network_services import SERVER_URL, PROJECT_ID

def get_nodes_by_name():
    nodes = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes"
    )

    nodes_by_name = {}

    for node in nodes:
        nodes_by_name[node["name"]] = node

    return nodes_by_name

def port_keys(name):
    raw = name.lower().replace(" ", "")
    keys = {raw}

    if raw.startswith("gigabitethernet"):
        keys.add("gi" + raw[len("gigabitethernet"):])

    if raw.startswith("gi"):
        keys.add("gigabitethernet" + raw[len("gi"):])

    if raw.startswith("ethernet"):
        suffix = raw[len("ethernet"):]
        keys.add("eth" + suffix)
        keys.add("e" + suffix)

    if raw.startswith("eth"):
        suffix = raw[len("eth"):]
        keys.add("ethernet" + suffix)
        keys.add("e" + suffix)

    if raw.startswith("e") and raw[1:].isdigit():
        suffix = raw[1:]
        keys.add("ethernet" + suffix)
        keys.add("eth" + suffix)

    return keys


def get_ports(node):
    if "ports" in node and node["ports"]:
        return node["ports"]

    node_detail = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/nodes/{node['node_id']}"
    )

    return node_detail.get("ports", [])


def find_port(node, port_name):
    wanted_keys = port_keys(port_name)

    for port in get_ports(node):
        names = []

        if "name" in port:
            names.append(port["name"])

        if "short_name" in port:
            names.append(port["short_name"])

        for name in names:
            if wanted_keys & port_keys(name):
                return port

    print("Mevcut portlar:", node["name"])
    for port in get_ports(node):
        print(port)

    raise RuntimeError(f"Port bulunamadi: {node['name']} {port_name}")

def create_link(nodes_by_name, link):
    node_a_name, port_a_name = link["a"]
    node_b_name, port_b_name = link["b"]

    node_a = nodes_by_name[node_a_name]
    node_b = nodes_by_name[node_b_name]

    port_a = find_port(node_a, port_a_name)
    port_b = find_port(node_b, port_b_name)

    body = {
        "nodes": [
            {
                "node_id": node_a["node_id"],
                "adapter_number": port_a["adapter_number"],
                "port_number": port_a["port_number"]
            },
            {
                "node_id": node_b["node_id"],
                "adapter_number": port_b["adapter_number"],
                "port_number": port_b["port_number"]
            }
        ]
    }

    gns3_request(
        SERVER_URL,
        "POST",
        f"/v2/projects/{PROJECT_ID}/links",
        body
    )

    print("Olusturuldu:", node_a_name, port_a_name, "<->", node_b_name, port_b_name)



def endpoint_key(endpoint):
    return (
        endpoint["node_id"],
        endpoint["adapter_number"],
        endpoint["port_number"]
    )


def get_existing_link_keys():
    links = gns3_request(
        SERVER_URL,
        "GET",
        f"/v2/projects/{PROJECT_ID}/links"
    )

    existing = set()

    for link in links:
        endpoints = link["nodes"]

        if len(endpoints) != 2:
            continue

        key = frozenset([
            endpoint_key(endpoints[0]),
            endpoint_key(endpoints[1])
        ])

        existing.add(key)

    return existing

def main():
    nodes_by_name = get_nodes_by_name()
    existing_links = get_existing_link_keys()

    for link in LINKS:
        node_a_name, port_a_name = link["a"]
        node_b_name, port_b_name = link["b"]

        node_a = nodes_by_name[node_a_name]
        node_b = nodes_by_name[node_b_name]

        port_a = find_port(node_a, port_a_name)
        port_b = find_port(node_b, port_b_name)

        endpoint_a = {
            "node_id": node_a["node_id"],
            "adapter_number": port_a["adapter_number"],
            "port_number": port_a["port_number"]
        }

        endpoint_b = {
            "node_id": node_b["node_id"],
            "adapter_number": port_b["adapter_number"],
            "port_number": port_b["port_number"]
        }

        link_key = frozenset([
            endpoint_key(endpoint_a),
            endpoint_key(endpoint_b)
        ])

        if link_key in existing_links:
            print("Zaten var, atlandi:", node_a_name, port_a_name, "<->", node_b_name, port_b_name)
            continue

        body = {
            "nodes": [endpoint_a, endpoint_b]
        }

        gns3_request(
            SERVER_URL,
            "POST",
            f"/v2/projects/{PROJECT_ID}/links",
            body
        )

        existing_links.add(link_key)

        print("Olusturuldu:", node_a_name, port_a_name, "<->", node_b_name, port_b_name)

if __name__ == "__main__":
    main()