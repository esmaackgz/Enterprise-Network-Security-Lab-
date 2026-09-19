import json
from urllib.request import Request, urlopen

def gns3_request(server_url, method, path, body=None):
    # GNS3 API'ye istek atan ortak fonksiyon
    url = server_url.rstrip("/") + path

    data = None
    headers = {
        "Accept": "application/json"
    }

    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        url,
        data=data,
        headers=headers,
        method=method
    )

    with urlopen(request, timeout=10) as response:
        raw_response = response.read().decode("utf-8")

        if raw_response:
            return json.loads(raw_response)

        return {}