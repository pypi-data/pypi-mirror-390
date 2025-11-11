from kystdatahuset.file_storage import publish, list, delete
from uuid import UUID
from typing import List

def test_list(auth_jwt):
    list_res = list(jwt_token=auth_jwt, resource_uuid=UUID("64127fc2-2644-4ed9-b886-fecfb914c4b5"))
    assert isinstance(list_res, List) and len(list_res) >= 0, "Expected non-empty file list"

def test_publish(upload_filename, auth_jwt):
    publish_res = publish(jwt_token=auth_jwt, resource_uuid=UUID("64127fc2-2644-4ed9-b886-fecfb914c4b5"), file_path=upload_filename, title="Test Upload", upload_file_type="csv", description="This is a test upload", categories=["test", "upload"], compressed=True)
    assert publish_res is not None, "Expected publish to return True"

def test_delete(auth_jwt):
    list_res = list(jwt_token=auth_jwt, resource_uuid=UUID("64127fc2-2644-4ed9-b886-fecfb914c4b5"))
    delete_res = delete(jwt_token=auth_jwt, file_uuid=list_res[0].uuid)
    assert delete_res == True, "Expected delete to return True"
