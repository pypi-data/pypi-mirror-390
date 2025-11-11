from pydantic import BaseModel, Field
from typing import List
from uuid import UUID


class FileListing(BaseModel):
    uuid: UUID = Field(..., description="Unique identifier for this file record")
    title: str = Field(..., description="Title or display name of the uploaded file")
    description: str = Field(..., description="Descriptive text about the file contents")
    categories: List[str] = Field(..., description="List of category tags assigned to the file")
    filetype: str = Field(..., description="Type or format of the uploaded file, e.g. csv, pdf")
    compressed: bool = Field(..., description="True if the file was uploaded as compressed archive")
    filename: str = Field(..., description="Server-side absolute file path")
    origFilename: str = Field(..., description="Original filename on the client before upload")
    resourceUuid: UUID = Field(..., description="UUID of the resource to which this file belongs")


# # ✅ Example usage:
# example_json = {
#     'uuid': '69d47723-206c-4a89-8d67-654f23706e24',
#     'title': 'Test Upload',
#     'description': 'This is a test upload',
#     'categories': ['test', 'upload'],
#     'filetype': 'csv',
#     'compressed': True,
#     'filename': r'E:\storage\kystdathuset\catalog\2025\11\64\12\7f\64127fc2-2644-4ed9-b886-fecfb914c4b5\C_Users_runar.bergheim_Documents_Development_kystdatahuset-python-lib_test_data_content.txt',
#     'origFilename': r'C:\\Users\\runar.bergheim\\Documents\\Development\\kystdatahuset-python-lib\\test_data\\content.txt',
#     'resourceUuid': '64127fc2-2644-4ed9-b886-fecfb914c4b5'
# }

# listing = FileListing(**example_json)
# print(listing.title)
# print(listing.resourceUuid)
