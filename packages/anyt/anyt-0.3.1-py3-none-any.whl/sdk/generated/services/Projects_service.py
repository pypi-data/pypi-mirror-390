from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

def list_projects_v1_workspaces__workspace_id__projects__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], status : Optional[Union[str,None]] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_ProjectListResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'status' : status
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
        raise HTTPException(response.status_code, f'list_projects_v1_workspaces__workspace_id__projects__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_ProjectListResponse_(**body) if body is not None else SuccessResponse_ProjectListResponse_()
def create_project_v1_workspaces__workspace_id__projects__post(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], data : CreateProjectRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Project_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/'
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
        raise HTTPException(response.status_code, f'create_project_v1_workspaces__workspace_id__projects__post failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return SuccessResponse_Project_(**body) if body is not None else SuccessResponse_Project_()
def get_current_project_v1_workspaces__workspace_id__projects_current_get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Project_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/current'
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
        raise HTTPException(response.status_code, f'get_current_project_v1_workspaces__workspace_id__projects_current_get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_Project_(**body) if body is not None else SuccessResponse_Project_()
def get_project_v1_workspaces__workspace_id__projects__project_id__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], project_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Project_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/{project_id}'
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
        raise HTTPException(response.status_code, f'get_project_v1_workspaces__workspace_id__projects__project_id__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_Project_(**body) if body is not None else SuccessResponse_Project_()
def delete_project_v1_workspaces__workspace_id__projects__project_id__delete(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], project_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_dict_str__Any__:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/{project_id}'
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
            'delete',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'delete_project_v1_workspaces__workspace_id__projects__project_id__delete failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_dict_str__Any__(**body) if body is not None else SuccessResponse_dict_str__Any__()
def update_project_v1_workspaces__workspace_id__projects__project_id__patch(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], project_id : int, data : ProjectUpdate, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Project_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/projects/{project_id}'
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
        raise HTTPException(response.status_code, f'update_project_v1_workspaces__workspace_id__projects__project_id__patch failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_Project_(**body) if body is not None else SuccessResponse_Project_()