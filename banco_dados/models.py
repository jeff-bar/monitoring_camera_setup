from .database import Base
from sqlalchemy import TIMESTAMP, Column, String, Boolean, ARRAY, INTEGER
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
from sqlalchemy.orm import relationship




class HeatMap(Base):
    __tablename__ = 'heat_map'
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default='heat_map' )
    position = Column(String, nullable=False, default='bottom' )
    active = Column(Boolean, nullable=False, default=False)
    id_camera =  Column(GUID, nullable=True)
    camera = relationship(
        'Camera',
        backref='heat_map_camera',
        primaryjoin='HeatMap.id_camera == Camera.id', foreign_keys=id_camera,
    )

    points = Column(String, nullable=False)
    createdAt = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())


class Polygon(Base):
    __tablename__ = 'polygons'
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default='polygon' )
    position = Column(String, nullable=False, default='bottom' )
    active = Column(Boolean, nullable=False, default=False)
    id_camera =  Column(GUID, nullable=True)
    camera = relationship(
        'Camera',
        backref='polygon_camera',
        primaryjoin='Polygon.id_camera == Camera.id', foreign_keys=id_camera,
    )

    sitting_person = Column(Boolean, nullable=False, default=False)
    points = Column(String, nullable=False)
    createdAt = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())



class Line(Base):
    __tablename__ = 'lines'
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default='line' )
    position = Column(String, nullable=False, default='bottom' )
    active = Column(Boolean, nullable=False, default=False)
    id_camera =  Column(GUID, nullable=True)
    camera = relationship(
        'Camera',
        backref='line_camera',
        primaryjoin='Line.id_camera == Camera.id', foreign_keys=id_camera,
    )

    sitting_person = Column(Boolean, nullable=False, default=False)
    larger_area = Column(Boolean, nullable=False, default=True)
    points = Column(String, nullable=False)
    exclusion_points = Column(String, nullable=False)
    createdAt = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())
    


class Loja(Base):
    __tablename__ = 'loja'
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    name = Column(String, nullable=True)
    state = Column(String, nullable=True)
    city = Column(String, nullable=True)
    road = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    number = Column(String, nullable=True)

    createdAt = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())

class Camera(Base):
    __tablename__ = 'camera'
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    name = Column(String, nullable=False)
    
    id_loja =  Column(GUID, nullable=True)
    loja = relationship(
        'Loja',
        backref='camera_loja',
        primaryjoin='Camera.id_loja == Loja.id', foreign_keys=id_loja,
    )

    createdAt = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updatedAt = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())
