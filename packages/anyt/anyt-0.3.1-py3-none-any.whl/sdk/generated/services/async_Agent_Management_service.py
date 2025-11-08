from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

async def list_agents_v1_workspaces__workspace_id__agents__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_list_Agent__:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/agents/'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
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
        raise HTTPException(response.status_code, f'list_agents_v1_workspaces__workspace_id__agents__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_list_Agent__(**body) if body is not None else SuccessResponse_list_Agent__()
async def create_agent_v1_workspaces__workspace_id__agents__post(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], data : CreateAgentRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Agent_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/agents/'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'post',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump()
                    )

    if response.status_code != 201:
        raise HTTPException(response.status_code, f'create_agent_v1_workspaces__workspace_id__agents__post failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return SuccessResponse_Agent_(**body) if body is not None else SuccessResponse_Agent_()
async def get_agent_v1_workspaces__workspace_id__agents__agent_id__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], agent_id : str, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Agent_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/agents/{agent_id}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
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
        raise HTTPException(response.status_code, f'get_agent_v1_workspaces__workspace_id__agents__agent_id__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_Agent_(**body) if body is not None else SuccessResponse_Agent_()
async def delete_agent_v1_workspaces__workspace_id__agents__agent_id__delete(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], agent_id : str, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_NoneType_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/agents/{agent_id}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'delete',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'delete_agent_v1_workspaces__workspace_id__agents__agent_id__delete failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_NoneType_(**body) if body is not None else SuccessResponse_NoneType_()
async def update_agent_v1_workspaces__workspace_id__agents__agent_id__patch(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], agent_id : str, data : AgentUpdate, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Agent_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/agents/{agent_id}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'patch',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump()
                    )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'update_agent_v1_workspaces__workspace_id__agents__agent_id__patch failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_Agent_(**body) if body is not None else SuccessResponse_Agent_()
async def get_assignees_v1_workspaces__workspace_id__assignees__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_AssigneesData_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/assignees/'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
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
        raise HTTPException(response.status_code, f'get_assignees_v1_workspaces__workspace_id__assignees__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_AssigneesData_(**body) if body is not None else SuccessResponse_AssigneesData_()