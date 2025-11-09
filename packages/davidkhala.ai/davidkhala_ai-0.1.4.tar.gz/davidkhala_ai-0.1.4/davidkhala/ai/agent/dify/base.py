from davidkhala.utils.http_request import Request

class API(Request):
    def __init__(self, api_key: str, base_url="https://api.dify.ai/v1"):
        super().__init__({'bearer': api_key})
        self.base_url = base_url
        self.api_key = api_key