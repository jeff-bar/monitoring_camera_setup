from datetime import datetime
from typing import List
from pydantic import BaseModel


class HeatMapBaseSchema(BaseModel):

    id: str = None
    name: str  = None
    type: str  = None
    position: str  = None
    points:  str  = None
    active: bool = False
    id_camera:  str = None
    createdAt: datetime = None
    updatedAt: datetime = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListHeatMapResponse(BaseModel):
    status: str
    results: int
    polygons: List[HeatMapBaseSchema]


class PolygonBaseSchema(BaseModel):

    id: str = None
    name: str = None
    type: str = None
    position: str = None
    sitting_person: bool = False
    points:  str = None
    active: bool = False
    id_camera:  str  = None
    createdAt: datetime = None
    updatedAt: datetime = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListPolygonResponse(BaseModel):
    status: str
    results: int
    polygons: List[PolygonBaseSchema]



class LineBaseSchema(BaseModel):

    id: str = None
    name: str = None
    type: str = None
    position: str = None
    camera: str = None
    sitting_person: bool = False
    larger_area: bool = False
    active: bool = False
    points:  str = None
    exclusion_points:  str = None
    id_camera:  str = None
    createdAt: datetime = None
    updatedAt: datetime = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListLineResponse(BaseModel):
    status: str
    results: int
    lines: List[LineBaseSchema]



class LojaBaseSchema(BaseModel):

    id: str = None
    name: str = None
    state: str = None
    city: str = None
    road: str = None
    zip_code: str = None
    number: str = None
    createdAt: datetime = None
    updatedAt: datetime = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListLojaResponse(BaseModel):
    status: str
    results: int
    lines: List[LineBaseSchema]




class CameraBaseSchema(BaseModel):

    id: str = None
    name: str = None
    id_loja: str = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListCameraResponse(BaseModel):
    status: str
    results: int
    lines: List[CameraBaseSchema]