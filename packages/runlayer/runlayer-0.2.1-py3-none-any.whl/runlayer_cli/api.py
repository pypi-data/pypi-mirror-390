import httpx


from runlayer_cli.models import (
    ServerDetails,
    LocalCapabilities,
    PreRequest,
    PostRequest,
)

USER_AGENT = "Runlayer CLI"
API_KEY_HEADER_NAME = "x-runlayer-api-key"


class RunlayerClient:
    def __init__(self, hostname: str, secret: str):
        self.headers = {
            "User-Agent": USER_AGENT,
            API_KEY_HEADER_NAME: secret,
        }
        self.base_url = hostname

    def get_server_details(self, server_id: str) -> ServerDetails:
        with httpx.Client(headers=self.headers) as client:
            response = client.get(f"{self.base_url}/api/v1/local/{server_id}")
            response.raise_for_status()
            return ServerDetails.model_validate(response.json())

    def update_capabilities(self, server_id: str, capabilities: LocalCapabilities):
        with httpx.Client(headers=self.headers) as client:
            response = client.post(
                f"{self.base_url}/api/v1/local/{server_id}/capabilities",
                json=capabilities.model_dump(mode="json"),
            )
            return response

    def pre(self, server_id: str, request: PreRequest) -> httpx.Response:
        with httpx.Client(headers=self.headers) as client:
            response = client.post(
                f"{self.base_url}/api/v1/local/{server_id}/pre",
                json=request.model_dump(),
            )
            return response

    def post(self, server_id: str, request: PostRequest) -> httpx.Response:
        with httpx.Client(headers=self.headers) as client:
            response = client.post(
                f"{self.base_url}/api/v1/local/{server_id}/post",
                json=request.model_dump(),
            )
            return response
