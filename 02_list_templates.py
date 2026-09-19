from gns3_client import gns3_request

from network_services import  SERVER_URL

def list_templates():
    templates = gns3_request(
        SERVER_URL,
        "GET",
        "/v2/templates"
    )

    return templates


def main():
    templates = list_templates()

    print("Template listesi:")
    print(len(templates))

    print("Ham cevap:")
    print(templates)
"""
    for template in templates:
        print(template["name"], "-", template["template_id"])
"""



if __name__ == "__main__":
    main()