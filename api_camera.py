from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Response, APIRouter
from banco_dados.database import get_db
from banco_dados.models import  Camera
from banco_dados.schemas import CameraBaseSchema


router = APIRouter()




@router.get('/api/camera/')
def all_camera(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ''):
    
    skip = (page - 1) * limit

    cameras = db.query(Camera).filter(
       Camera.name.contains(search)).limit(limit).offset(skip).all()
    return {'status': 'success', 'results': len(cameras), 'camera': cameras}



@router.post('/api/save_camera', status_code=status.HTTP_201_CREATED)
def save_loja(payload:CameraBaseSchema , db: Session = Depends(get_db)):

    new_camera = Camera(**payload.dict())
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return {"status": "success", "camera": new_camera}




@router.patch('/api/camera/{cameraId}')
def update_camera(cameraId: str, payload: CameraBaseSchema, db: Session = Depends(get_db)):
    camera_query = db.query(Camera).filter(Camera.id == cameraId)
    db_camera = camera_query.first()

    if not db_camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No camera with this id: {cameraId} found')
    update_data = payload.dict(exclude_unset=True)
    camera_query.filter(Camera.id == cameraId).update(update_data,
                                                       synchronize_session=False)
    db.commit()
    db.refresh(db_camera)
    return {"status": "success", "camera": db_camera}




@router.get('/api/camera/{cameraId}')
def get_camera(cameraId: str, db: Session = Depends(get_db)):

    camera = db.query(Camera).filter(Camera.id == cameraId).first()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No camera with this id: {cameraId} found")
    return {"status": "success", "camera": camera}



@router.get('/api/camera/loja/{lojaId}')
def get_camera(lojaId: str, db: Session = Depends(get_db)):

    cameras = db.query(Camera).filter(Camera.id_loja == lojaId).all()
    if len(cameras) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No camera with this id loja: {lojaId} found")

    return {'status': 'success', 'results': len(cameras), 'camera': cameras}





@router.delete('/api/camera/{cameraId}')
def delete_camera(cameraId: str, db: Session = Depends(get_db)):

    camera_query = db.query(Camera).filter(Camera.id == cameraId)
    db_camera = camera_query.first()

    if not db_camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No camera with this id: {cameraId} found')
    camera_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)