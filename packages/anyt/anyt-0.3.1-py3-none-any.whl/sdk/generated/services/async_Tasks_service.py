from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

async def create_task_v1_projects__project_id__tasks__post(api_config_override : Optional[APIConfig] = None, *, project_id : int, data : CreateTaskRequest, workspace_id : Optional[Union[int,None]] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Task_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/projects/{project_id}/tasks/'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'workspace_id' : workspace_id
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
        raise HTTPException(response.status_code, f'create_task_v1_projects__project_id__tasks__post failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return SuccessResponse_Task_(**body) if body is not None else SuccessResponse_Task_()
async def bulk_update_tasks_v1_workspaces__workspace_id__bulk_tasks_patch(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], data : BulkUpdateTasksRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_BulkUpdateTasksResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/bulk-tasks'
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
        raise HTTPException(response.status_code, f'bulk_update_tasks_v1_workspaces__workspace_id__bulk_tasks_patch failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_BulkUpdateTasksResponse_(**body) if body is not None else SuccessResponse_BulkUpdateTasksResponse_()
async def list_tasks_v1_workspaces__workspace_id__tasks__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], project : Optional[Union[int,None]] = None, status : Optional[Union[str,None]] = None, priority : Optional[Union[int,None]] = None, priority_gte : Optional[Union[int,None]] = None, priority_lte : Optional[Union[int,None]] = None, owner : Optional[Union[str,None]] = None, creator : Optional[Union[str,None]] = None, labels : Optional[Union[str,None]] = None, parent : Optional[Union[str,None]] = None, has_subtasks : Optional[Union[bool,None]] = None, created_after : Optional[Union[str,None]] = None, updated_after : Optional[Union[str,None]] = None, completed_after : Optional[Union[str,None]] = None, completed_before : Optional[Union[str,None]] = None, limit : Optional[int] = None, offset : Optional[int] = None, sort_by : Optional[str] = None, order : Optional[str] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_TaskListResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key,
'X-Test-User-Id' : X_Test_User_Id
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'project' : project,
'status' : status,
'priority' : priority,
'priority_gte' : priority_gte,
'priority_lte' : priority_lte,
'owner' : owner,
'creator' : creator,
'labels' : labels,
'parent' : parent,
'has_subtasks' : has_subtasks,
'created_after' : created_after,
'updated_after' : updated_after,
'completed_after' : completed_after,
'completed_before' : completed_before,
'limit' : limit,
'offset' : offset,
'sort_by' : sort_by,
'order' : order
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
        raise HTTPException(response.status_code, f'list_tasks_v1_workspaces__workspace_id__tasks__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_TaskListResponse_(**body) if body is not None else SuccessResponse_TaskListResponse_()
async def get_task_v1_workspaces__workspace_id__tasks__task_identifier__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], task_identifier : str, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Task_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}'
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
        raise HTTPException(response.status_code, f'get_task_v1_workspaces__workspace_id__tasks__task_identifier__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_Task_(**body) if body is not None else SuccessResponse_Task_()
async def delete_task_v1_workspaces__workspace_id__tasks__task_identifier__delete(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], task_identifier : str, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_dict_str__Any__:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}'
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
        raise HTTPException(response.status_code, f'delete_task_v1_workspaces__workspace_id__tasks__task_identifier__delete failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_dict_str__Any__(**body) if body is not None else SuccessResponse_dict_str__Any__()
async def update_task_v1_workspaces__workspace_id__tasks__task_identifier__patch(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], task_identifier : str, data : TaskUpdate, If_Match : Optional[Union[int,None]] = None, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Task_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'If-Match' : If_Match,
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
        raise HTTPException(response.status_code, f'update_task_v1_workspaces__workspace_id__tasks__task_identifier__patch failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_Task_(**body) if body is not None else SuccessResponse_Task_()
async def auto_fill_task_v1_workspaces__workspace_id__tasks__task_identifier__auto_fill_post(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], task_identifier : str, data : AutoFillRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_AutoFillResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}/auto-fill'
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

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'auto_fill_task_v1_workspaces__workspace_id__tasks__task_identifier__auto_fill_post failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_AutoFillResponse_(**body) if body is not None else SuccessResponse_AutoFillResponse_()