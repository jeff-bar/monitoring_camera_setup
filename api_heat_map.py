import remove_person as rp
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Response, APIRouter
from banco_dados.database import get_db
from banco_dados.models import HeatMap, Camera, Loja
from banco_dados.schemas import HeatMapBaseSchema


router = APIRouter()


@router.patch('/api/heat_map/active/{heatMapId}/{active}')
def update_line(heatMapId: str, active: bool, db: Session = Depends(get_db)):
    heat_map_query = db.query(HeatMap).filter(HeatMap.id == heatMapId)
    db_line = heat_map_query.first()

    if not db_line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No heat_map with this id: {heatMapId} found')
    
    heat_map_query.filter(HeatMap.id == heatMapId).update({HeatMap.active: active },
                                                       synchronize_session=False)
    db.commit()
    db.refresh(db_line)
    return {"status": "success", "heat_map": db_line}


@router.get('/api/heat_map/process')
def all_line(db: Session = Depends(get_db)):
    
    #heat_maps_process = db.query(HeatMap,Camera,Loja).filter(
    #    HeatMap.active == True and HeatMap.id_camera == Camera.id and Camera.id_loja == Loja.id 
    #).all()

    heat_maps_process = db.query(
                            HeatMap, Loja, Camera
                        ).join(
                            Camera, HeatMap.id_camera == Camera.id
                        ).join(
                            Loja, Camera.id_loja == Loja.id 
                        ).filter(  
                            HeatMap.active == True 
                        ).all()

    return {'status': 'success', 'results': len(heat_maps_process), 'heat_maps': heat_maps_process}



@router.get('/api/heat_map/')
def all_line(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ''):
    
    skip = (page - 1) * limit

    heat_maps = db.query(HeatMap).filter(
       HeatMap.name.contains(search)).limit(limit).offset(skip).all()
    return {'status': 'success', 'results': len(heat_maps), 'heat_maps': heat_maps}



@router.post('/api/save_heat_map', status_code=status.HTTP_201_CREATED)
def save_line(payload:HeatMapBaseSchema , db: Session = Depends(get_db)):

    new_heat_maps = HeatMap(**payload.dict())
    db.add(new_heat_maps)
    db.commit()
    db.refresh(new_heat_maps)
    return {"status": "success", "heat_map": new_heat_maps}




@router.patch('/api/heat_map/{heatMapId}')
def update_line(heatMapId: str, payload: HeatMapBaseSchema, db: Session = Depends(get_db)):
    heat_map_query = db.query(HeatMap).filter(HeatMap.id == heatMapId)
    db_line = heat_map_query.first()

    if not db_line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No heat_map with this id: {heatMapId} found')
    update_data = payload.dict(exclude_unset=True)
    heat_map_query.filter(HeatMap.id == heatMapId).update(update_data,
                                                       synchronize_session=False)
    db.commit()
    db.refresh(db_line)
    return {"status": "success", "heat_map": db_line}




@router.get('/api/heat_map/{heatMapId}')
def get_line(heatMapId: str, db: Session = Depends(get_db)):

    heat_map = db.query(HeatMap).filter(HeatMap.id == heatMapId).first()
    if not heat_map:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No heat_map with this id: {heatMapId} found")
    return {"status": "success", "heat_map": heat_map}




@router.delete('/api/heat_map/{heatMapId}')
def delete_line(heatMapId: str, db: Session = Depends(get_db)):

    heat_map_query = db.query(HeatMap).filter(HeatMap.id == heatMapId)
    db_line = heat_map_query.first()

    if not db_line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No heat_map with this id: {heatMapId} found')
    heat_map_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)