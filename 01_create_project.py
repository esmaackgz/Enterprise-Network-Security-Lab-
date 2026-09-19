from gns3_client import gns3_request
from network_services import SERVER_URL

PROJECT_NAME = "Network_Python_Project"


def create_project(project_name):
    body = {
        "name": project_name
    }

    project = gns3_request(
        SERVER_URL,
        "POST",
        "/v2/projects",
        body
    )

    return project


def main():
    version = gns3_request(
        SERVER_URL,
        "GET",
        "/v2/version"
    )

    print("GNS3 bağlantısı başarılı:")
    print(version)

    project = create_project(PROJECT_NAME)

    print("Proje oluşturuldu:")
    print(project)

    print("Project ID:")
    print(project["project_id"])


if __name__ == "__main__":
    main()

