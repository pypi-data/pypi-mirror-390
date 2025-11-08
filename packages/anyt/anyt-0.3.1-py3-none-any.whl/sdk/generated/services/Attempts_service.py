from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

def start_attempt_v1_workspaces__workspace_id__tasks__task_identifier__attempts_start_post(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], task_identifier : str, data : StartAttemptRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_AttemptResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}/attempts/start'
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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'post',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump()
                    )

    if response.status_code != 201:
        raise HTTPException(response.status_code, f'start_attempt_v1_workspaces__workspace_id__tasks__task_identifier__attempts_start_post failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return SuccessResponse_AttemptResponse_(**body) if body is not None else SuccessResponse_AttemptResponse_()
def finish_attempt_v1_workspaces__workspace_id__attempts__attempt_id__finish_post(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], attempt_id : int, data : FinishAttemptRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_AttemptResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/attempts/{attempt_id}/finish'
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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'post',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump()
                    )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'finish_attempt_v1_workspaces__workspace_id__attempts__attempt_id__finish_post failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_AttemptResponse_(**body) if body is not None else SuccessResponse_AttemptResponse_()
def get_attempt_v1_workspaces__workspace_id__attempts__attempt_id__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], attempt_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_AttemptResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/attempts/{attempt_id}'
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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'get_attempt_v1_workspaces__workspace_id__attempts__attempt_id__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_AttemptResponse_(**body) if body is not None else SuccessResponse_AttemptResponse_()
def update_attempt_v1_workspaces__workspace_id__attempts__attempt_id__patch(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], attempt_id : int, data : AttemptUpdate, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_AttemptResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/attempts/{attempt_id}'
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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'patch',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump()
                    )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'update_attempt_v1_workspaces__workspace_id__attempts__attempt_id__patch failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_AttemptResponse_(**body) if body is not None else SuccessResponse_AttemptResponse_()
def list_task_attempts_v1_workspaces__workspace_id__tasks__task_identifier__attempts__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], task_identifier : str, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_AttemptListResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}/attempts/'
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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'list_task_attempts_v1_workspaces__workspace_id__tasks__task_identifier__attempts__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_AttemptListResponse_(**body) if body is not None else SuccessResponse_AttemptListResponse_()