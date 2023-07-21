import remove_person as rp
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Response, APIRouter
from banco_dados.database import get_db
from banco_dados.models import Line, Camera, Loja
from banco_dados.schemas import LineBaseSchema


router = APIRouter()



@router.patch('/api/line/active/{lineId}/{active}')
def update_line(lineId: str, active: bool, db: Session = Depends(get_db)):
    line_query = db.query(Line).filter(Line.id == lineId)
    db_line = line_query.first()

    if not db_line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No line with this id: {lineId} found')
    
    line_query.filter(Line.id == lineId).update({Line.active: active },
                                                       synchronize_session=False)
    db.commit()
    db.refresh(db_line)
    return {"status": "success", "line": db_line}



@router.get('/api/line/process')
def all_line(db: Session = Depends(get_db)):

    line_process = db.query(
                            Line, Loja, Camera
                        ).join(
                            Camera, Line.id_camera == Camera.id
                        ).join(
                            Loja, Camera.id_loja == Loja.id 
                        ).filter(  
                            Line.active == True 
                        ).all()

    return {'status': 'success', 'results': len(line_process), 'lines': line_process}



@router.get('/api/line/')
def all_line(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ''):
    
    skip = (page - 1) * limit

    lines = db.query(Line).filter(
       Line.name.contains(search)).limit(limit).offset(skip).all()
    return {'status': 'success', 'results': len(lines), 'lines': lines}



@router.post('/api/save_line', status_code=status.HTTP_201_CREATED)
def save_line(payload:LineBaseSchema , db: Session = Depends(get_db)):

    if payload.space_enterece is not None and payload.space_enterece != "BIG" and payload.space_enterece != "SMALL":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Space_enterece field must be "BIG", "SMALL" or NULL')

    new_line = Line(**payload.dict())
    db.add(new_line)
    db.commit()
    db.refresh(new_line)
    return {"status": "success", "line": new_line}




@router.patch('/api/line/{lineId}')
def update_line(lineId: str, payload: LineBaseSchema, db: Session = Depends(get_db)):

    if payload.space_enterece is not None and payload.space_enterece != "BIG" and payload.space_enterece != "SMALL":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Space_enterece field must be "BIG", "SMALL" or NULL')

    line_query = db.query(Line).filter(Line.id == lineId)
    db_line = line_query.first()

    if not db_line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No line with this id: {lineId} found')
    update_data = payload.dict(exclude_unset=True)
    line_query.filter(Line.id == lineId).update(update_data,
                                                       synchronize_session=False)
    db.commit()
    db.refresh(db_line)
    return {"status": "success", "line": db_line}




@router.get('/api/line/{lineId}')
def get_line(lineId: str, db: Session = Depends(get_db)):

    line = db.query(Line).filter(Line.id == lineId).first()
    if not line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No line with this id: {lineId} found")
    return {"status": "success", "line": line}




@router.delete('/api/line/{lineId}')
def delete_line(lineId: str, db: Session = Depends(get_db)):

    line_query = db.query(Line).filter(Line.id == lineId)
    db_line = line_query.first()

    if not db_line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No line with this id: {lineId} found')
    line_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)