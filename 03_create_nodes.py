from gns3_client import gns3_request
from topology_data import NODES
from network_services import SERVER_URL, PROJECT_ID


def get_templates_by_name():
    templates = gns3_request(
        SERVER_URL,
        "GET",
        "/v2/templates"
    )

    templates_by_name = {}

    for template in templates:
        templates_by_name[template["name"]] = template["template_id"]

    return templates_by_name


def create_node(node, templates_by_name):
    template_name = node["template_name"]
    template_id = templates_by_name[template_name]

    print("Node:", node["name"])
    print("Template:", template_name)
    print("Template ID:", template_id)

    body = {
        "name": node["name"],
        "x": node["x"],
        "y": node["y"]
    }

    created_node = gns3_request(
        SERVER_URL,
        "POST",
        f"/v2/projects/{PROJECT_ID}/templates/{template_id}",
        body
    )

    return created_node


def main():
    templates_by_name = get_templates_by_name()

    print("Bulunan template isimleri:")
    for name in templates_by_name:
        print("-", name)

    print("Node oluşturma başladı")

    for node in NODES:
        created_node = create_node(node, templates_by_name)
        print("Oluşturuldu:", created_node["name"], created_node["node_id"])


if __name__ == "__main__":
    main()
