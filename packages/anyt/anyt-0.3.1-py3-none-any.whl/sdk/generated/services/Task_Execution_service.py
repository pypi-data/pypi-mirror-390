from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

def get_workspace_execution_order_v1_workspaces__workspace_id__tasks_execution_order_get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], project_id : Optional[Union[int,None]] = None, num_runners : Optional[int] = None, include_completed : Optional[bool] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_ExecutionOrderResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/execution-order'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'project_id' : project_id,
'num_runners' : num_runners,
'include_completed' : include_completed
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'get_workspace_execution_order_v1_workspaces__workspace_id__tasks_execution_order_get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_ExecutionOrderResponse_(**body) if body is not None else SuccessResponse_ExecutionOrderResponse_()
def get_project_execution_order_v1_workspaces__workspace_id__projects__project_id__tasks_execution_order_get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], project_id : int, num_runners : Optional[int] = None, include_completed : Optional[bool] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_ExecutionOrderResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/{project_id}/tasks/execution-order'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'num_runners' : num_runners,
'include_completed' : include_completed
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'get_project_execution_order_v1_workspaces__workspace_id__projects__project_id__tasks_execution_order_get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_ExecutionOrderResponse_(**body) if body is not None else SuccessResponse_ExecutionOrderResponse_()