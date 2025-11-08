from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

def list_attempt_artifacts_v1_workspaces__workspace_id__attempts__attempt_id__artifacts__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], attempt_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_ArtifactListResponse_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/attempts/{attempt_id}/artifacts/'
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
        raise HTTPException(response.status_code, f'list_attempt_artifacts_v1_workspaces__workspace_id__attempts__attempt_id__artifacts__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_ArtifactListResponse_(**body) if body is not None else SuccessResponse_ArtifactListResponse_()
def create_artifact_v1_workspaces__workspace_id__attempts__attempt_id__artifacts__post(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], attempt_id : int, data : CreateArtifactRequest, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Artifact_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/attempts/{attempt_id}/artifacts/'
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
        raise HTTPException(response.status_code, f'create_artifact_v1_workspaces__workspace_id__attempts__attempt_id__artifacts__post failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return SuccessResponse_Artifact_(**body) if body is not None else SuccessResponse_Artifact_()
def get_artifact_v1_workspaces__workspace_id__artifacts__artifact_id__get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], artifact_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> SuccessResponse_Artifact_:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/artifacts/{artifact_id}'
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
        raise HTTPException(response.status_code, f'get_artifact_v1_workspaces__workspace_id__artifacts__artifact_id__get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return SuccessResponse_Artifact_(**body) if body is not None else SuccessResponse_Artifact_()
def download_artifact_v1_workspaces__workspace_id__artifacts__artifact_id__download_get(api_config_override : Optional[APIConfig] = None, *, workspace_id : Union[int,None], artifact_id : int, X_API_Key : Optional[Union[str,None]] = None, X_Test_User_Id : Optional[Union[str,None]] = None) -> Any:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/artifacts/{artifact_id}/download'
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
        raise HTTPException(response.status_code, f'download_artifact_v1_workspaces__workspace_id__artifacts__artifact_id__download_get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return body
