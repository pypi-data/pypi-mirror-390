from typing                          import Any, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Service__Fast_API__Client__Namespaces(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def list(self) -> Dict:
                                                                                    # Build path
        path = f"/namespaces/list"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else []