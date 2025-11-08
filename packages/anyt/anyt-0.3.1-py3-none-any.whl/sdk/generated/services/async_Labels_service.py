from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

async def list_labels_v1_workspaces__workspace_id__labels__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_List_Label__:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/labels/'
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
        raise HTTPException(response.status_code, f'list_labels_v1_workspaces__workspace_id__labels__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_List_Label__(**body) if body is not None else SuccessResponse_List_Label__()
async def create_label_v1_workspaces__workspace_id__labels__post(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], data : LabelCreate, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Label_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/labels/'
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
        raise HTTPException(response.status_code, f'create_label_v1_workspaces__workspace_id__labels__post failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return SuccessResponse_Label_(**body) if body is not None else SuccessResponse_Label_()
async def get_label_v1_workspaces__workspace_id__labels__label_id__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], label_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Label_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/labels/{label_id}'
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
        raise HTTPException(response.status_code, f'get_label_v1_workspaces__workspace_id__labels__label_id__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_Label_(**body) if body is not None else SuccessResponse_Label_()
async def delete_label_v1_workspaces__workspace_id__labels__label_id__delete(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], label_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_dict_str__Any__:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/labels/{label_id}'
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
        raise HTTPException(response.status_code, f'delete_label_v1_workspaces__workspace_id__labels__label_id__delete failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_dict_str__Any__(**body) if body is not None else SuccessResponse_dict_str__Any__()
async def update_label_v1_workspaces__workspace_id__labels__label_id__patch(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], label_id : int, data : LabelUpdate, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Label_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/labels/{label_id}'
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
        raise HTTPException(response.status_code, f'update_label_v1_workspaces__workspace_id__labels__label_id__patch failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_Label_(**body) if body is not None else SuccessResponse_Label_()