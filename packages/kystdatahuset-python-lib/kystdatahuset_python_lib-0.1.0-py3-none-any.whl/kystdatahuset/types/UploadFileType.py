from typing import Literal, TypeAlias

UploadFileType: TypeAlias = Literal[
    "csv",              # Comma Separated Variables
    "shp-compressed",   # Compressed ESRI Shapefile
    "fgdb-compressed",  # Compressed ESRI filegeodatabase
    "json",             # JSON file
    "geojson",          # GeoJSON file
    "png",              # Portable Network Graphics image
    "jpg",              # JPEG image
    "pdf",              # Portable Document Format
    "xlsx",             # Microsoft Excel spreadsheet
    "xml",              # XML file
    "docx",             # Microsoft Word document
    "NetCDF",           # Network Common Data Form (NetCDF)
    "tiff",             # Tagged Image File Format (*.tif)
    "geotiff",          # Georeferenced Tagged Image File Format (*.tif)
]