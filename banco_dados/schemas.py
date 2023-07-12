from datetime import datetime
from typing import List
from pydantic import BaseModel


class HeatMapBaseSchema(BaseModel):

    id: str | None = None
    name: str | None = None
    type: str | None = None
    position: str | None = None
    points:  str | None = None
    active: bool = False
    id_camera:  str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListHeatMapResponse(BaseModel):
    status: str
    results: int
    polygons: List[HeatMapBaseSchema]


class PolygonBaseSchema(BaseModel):

    id: str | None = None
    name: str | None = None
    type: str | None = None
    position: str | None = None
    sitting_person: bool = False
    points:  str | None = None
    active: bool = False
    id_camera:  str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListPolygonResponse(BaseModel):
    status: str
    results: int
    polygons: List[PolygonBaseSchema]



class LineBaseSchema(BaseModel):

    id: str | None = None
    name: str | None = None
    type: str | None = None
    position: str | None = None
    camera: str | None = None
    sitting_person: bool = False
    larger_area: bool = False
    active: bool = False
    points:  str | None = None
    exclusion_points:  str | None = None
    id_camera:  str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListLineResponse(BaseModel):
    status: str
    results: int
    lines: List[LineBaseSchema]



class LojaBaseSchema(BaseModel):

    id: str | None = None
    name: str | None = None
    state: str | None = None
    city: str | None = None
    road: str | None = None
    zip_code: str | None = None
    number: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListLojaResponse(BaseModel):
    status: str
    results: int
    lines: List[LineBaseSchema]




class CameraBaseSchema(BaseModel):

    id: str | None = None
    name: str | None = None
    id_loja: str | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListCameraResponse(BaseModel):
    status: str
    results: int
    lines: List[CameraBaseSchema]