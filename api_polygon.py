

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Response, APIRouter
from banco_dados.database import get_db
from banco_dados.models import Polygon
from banco_dados.schemas import PolygonBaseSchema


router = APIRouter()


@router.get('/api/polygon/')
def all_polygon(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ''):
    
    skip = (page - 1) * limit

    polygons = db.query(Polygon).filter(
       Polygon.name.contains(search)).limit(limit).offset(skip).all()
    return {'status': 'success', 'results': len(polygons), 'polygons': polygons}



@router.post('/api/save_polygon', status_code=status.HTTP_201_CREATED)
def save_polygon(payload:PolygonBaseSchema , db: Session = Depends(get_db)):

    new_polygon = Polygon(**payload.dict())
    db.add(new_polygon)
    db.commit()
    db.refresh(new_polygon)
    return {"status": "success", "polygon": new_polygon}




@router.patch('/api/polygon/{polygonId}')
def update_polygon(polygonId: str, payload: PolygonBaseSchema, db: Session = Depends(get_db)):
    polygon_query = db.query(Polygon).filter(Polygon.id == polygonId)
    db_polygon = polygon_query.first()

    if not db_polygon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No polygon with this id: {polygonId} found')
    update_data = payload.dict(exclude_unset=True)
    polygon_query.filter(Polygon.id == polygonId).update(update_data,
                                                       synchronize_session=False)
    db.commit()
    db.refresh(db_polygon)
    return {"status": "success", "polygon": db_polygon}




@router.get('/api/polygon/{polygonId}')
def get_polygon(polygonId: str, db: Session = Depends(get_db)):

    polygon = db.query(Polygon).filter(Polygon.id == polygonId).first()
    if not polygon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No polygon with this id: {polygonId} found")
    return {"status": "success", "polygon": polygon}




@router.delete('/api/polygon/{polygonId}')
def delete_polygon(polygonId: str, db: Session = Depends(get_db)):

    polygon_query = db.query(Polygon).filter(Polygon.id == polygonId)
    db_polygon = polygon_query.first()

    if not db_polygon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No polygon with this id: {polygonId} found')
    polygon_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)