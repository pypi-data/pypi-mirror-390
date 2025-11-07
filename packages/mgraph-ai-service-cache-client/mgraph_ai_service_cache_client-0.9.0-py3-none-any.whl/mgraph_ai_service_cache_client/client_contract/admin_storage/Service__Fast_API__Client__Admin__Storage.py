from typing                                                                                                  import Any, Dict, List
from osbot_utils.type_safe.Type_Safe                                                                         import Type_Safe
from mgraph_ai_service_cache_client.schemas.routes.admin.Schema__Routes__Admin__Storage__Files_All__Response import Schema__Routes__Admin__Storage__Files_All__Response


class Service__Fast_API__Client__Admin__Storage(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def bucket_name(self) -> Dict:                              # Auto-generated from endpoint get__bucket_name
                                                                                    # Build path
        path = "/admin/storage/bucket-name"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json

    def file__exists(self, path: Any) -> Dict:                              # Auto-generated from endpoint get__file__exists
                                                                                    # Build path
        path = f"/admin/storage/file/exists/{path}"                                 # FIXED was {path:path}
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else {}

    def file__bytes(self, path: Any) -> bytes:                              # Auto-generated from endpoint get__file__bytes
                                                                                    # Build path
        path = f"/admin/storage/file/bytes/{path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute( method = "GET",
                                        path   = path,
                                        body   = body)
        return result.content                                                       # Return response data

    def file__json(self, path: Any) -> Dict:                              # Auto-generated from endpoint get__file__json
                                                                                    # Build path
        path = f"/admin/storage/file/json/{path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute( method = "GET",
                                        path   = path ,
                                        body   = body )
                                                                                    # Return response data
        return result.json if result.json else {}

    def files__in__path(self,                                                # List files in path
                        path            : str  = ''    ,
                        return_full_path: bool = False ,
                        recursive       : bool = False
                    ) -> List[str]:


        endpoint = f"/admin/storage/files/in/{path}"                                   # Build endpoint
        params   = []

        if return_full_path:
            params.append(f"return_full_path={return_full_path}")
        if recursive:
            params.append(f"recursive={recursive}")

        if params:
            endpoint = f"{endpoint}?{'&'.join(params)}"

        result = self.requests.execute(method = "GET",
                                       path   = endpoint,
                                       body   = None)
        return result.json if result.json else []

    def files__all__path(self, path: str) -> Schema__Routes__Admin__Storage__Files_All__Response:     # Auto-generated from endpoint get__files__all__path
                                                                                    # Build path
        path = f"/admin/storage/files/all/{path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return Schema__Routes__Admin__Storage__Files_All__Response(**result.json)
        #return result.json if result.json else result.text

    def folders(self,                                                       # List folders in directory path
                path            : str  = ''   ,                             # Directory path to list folders from
                return_full_path: bool = False ,                            # If True, return full paths; if False, return relative names
                recursive       : bool = False                              # If True, list all folders recursively; if False, list only direct children
           ) -> List[str]:                                                  # List of folder paths (string)

        endpoint = f"/admin/storage/folders/{path}"                         # Build endpoint with path
        params   = []

        if return_full_path:
            params.append(f"return_full_path={return_full_path}")
        if recursive:
            params.append(f"recursive={recursive}")

        if params:
            endpoint = f"{endpoint}?{'&'.join(params)}"

        result = self.requests.execute(method = "GET",
                                        path   = endpoint,
                                        body   = None)
        return result.json if result.json else []

    def file__delete(self, path: str) -> Dict[str, Any]:              # Delete a file at path
        endpoint = f"/admin/storage/file/delete/{path}"                      # Build path
        result = self.requests.execute(method = "DELETE",
                                        path   = endpoint,
                                        body   = None)
        return result.json if result.json else {}                            # Return dict (empty if error)