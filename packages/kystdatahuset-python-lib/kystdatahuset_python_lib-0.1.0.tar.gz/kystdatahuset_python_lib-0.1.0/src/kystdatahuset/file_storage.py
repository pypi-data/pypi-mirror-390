from uuid import UUID
from typing import Sequence, List
from kystdatahuset.models import FileListing, WebServiceResponse
from kystdatahuset.types import UploadFileType
import os
from kystdatahuset.api_client import post_api_formdata, get_api, delete_api

def list(*, jwt_token: str, resource_uuid: UUID) -> List[FileListing]:
    """
    Placeholder for listing files in storage.
    """
    list_res = get_api(jwt_token, f"api/file-storage/list/{resource_uuid}")
    file_listings = WebServiceResponse[List[FileListing]](**list_res)   
    return file_listings.data

def delete(* , jwt_token: str, file_uuid: UUID) -> bool:
    """
    Placeholder for deleting a file in storage.
    """
    delete_res = delete_api(jwt_token, f"api/file-storage/delete/{file_uuid}")
    return delete_res.success

def publish(
    *,
    jwt_token: str,
    resource_uuid: UUID,
    file_path: str,
    title: str,
    upload_file_type: UploadFileType,
    description: str = "",
    categories: Sequence[str] = "",
    compressed: bool = False,
) -> bool:
    """
    Upload a file and metadata to the Kystdatahuset API.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Convert categories to multiple form fields (ASP.NET supports repeated keys)
    # or as a JSON-like string, depending on the API’s binding expectations.
    # The safe bet for ASP.NET [FromForm(Name="categories")] string[] is to repeat the key.
    data = [
        ("title", title),
        ("description", description),
        ("type", upload_file_type),
        ("compressed", str(compressed).lower()),  # ASP.NET expects 'true'/'false'
    ] + [("categories", c) for c in categories]

    response = post_api_formdata(jwt_token, f"api/file-storage/publish/{resource_uuid}", data, file_path)
    return response.success


