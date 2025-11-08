from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

async def get_workspace_dependency_graph_v1_workspaces__workspace_id__dependency_graph_get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], project_id : Optional[Union[int,None]] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_DependencyGraphResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/dependency-graph'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'project_id' : project_id
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'get_workspace_dependency_graph_v1_workspaces__workspace_id__dependency_graph_get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_DependencyGraphResponse_(**body) if body is not None else SuccessResponse_DependencyGraphResponse_()