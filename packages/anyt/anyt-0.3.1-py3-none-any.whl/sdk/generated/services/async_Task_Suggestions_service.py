from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

async def suggest_workspace_tasks_v1_workspaces__workspace_id__tasks_suggest_get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], max_suggestions : Optional[int] = None, status : Optional[str] = None, include_assigned : Optional[bool] = None, agent_id : Optional[Union[str,None]] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_TaskSuggestionsResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/suggest'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'max_suggestions' : max_suggestions,
'status' : status,
'include_assigned' : include_assigned,
'agent_id' : agent_id
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
        raise HTTPException(response.status_code, f'suggest_workspace_tasks_v1_workspaces__workspace_id__tasks_suggest_get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_TaskSuggestionsResponse_(**body) if body is not None else SuccessResponse_TaskSuggestionsResponse_()
async def suggest_project_tasks_v1_workspaces__workspace_id__projects__project_id__tasks_suggest_get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], project_id : int, max_suggestions : Optional[int] = None, status : Optional[str] = None, include_assigned : Optional[bool] = None, agent_id : Optional[Union[str,None]] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_TaskSuggestionsResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/{project_id}/tasks/suggest'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'max_suggestions' : max_suggestions,
'status' : status,
'include_assigned' : include_assigned,
'agent_id' : agent_id
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
        raise HTTPException(response.status_code, f'suggest_project_tasks_v1_workspaces__workspace_id__projects__project_id__tasks_suggest_get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_TaskSuggestionsResponse_(**body) if body is not None else SuccessResponse_TaskSuggestionsResponse_()