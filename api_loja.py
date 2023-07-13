from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Response, APIRouter
from banco_dados.database import get_db
from banco_dados.models import Loja
from banco_dados.schemas import LojaBaseSchema


router = APIRouter()


@router.get('/api/loja/')
def all_loja(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ''):
    
    skip = (page - 1) * limit

    lojas = db.query(Loja).filter(
       Loja.name.contains(search)).limit(limit).offset(skip).all()
    return {'status': 'success', 'results': len(lojas), 'lojas': lojas}



@router.post('/api/save_loja', status_code=status.HTTP_201_CREATED)
def save_loja(payload:LojaBaseSchema , db: Session = Depends(get_db)):

    new_loja = Loja(**payload.dict())
    db.add(new_loja)
    db.commit()
    db.refresh(new_loja)
    return {"status": "success", "loja": new_loja}




@router.patch('/api/loja/{lojaId}')
def update_loja(lojaId: str, payload: LojaBaseSchema, db: Session = Depends(get_db)):
    loja_query = db.query(Loja).filter(Loja.id == lojaId)
    db_loja = loja_query.first()

    if not db_loja:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No loja with this id: {lojaId} found')
    update_data = payload.dict(exclude_unset=True)
    loja_query.filter(Loja.id == lojaId).update(update_data,
                                                       synchronize_session=False)
    db.commit()
    db.refresh(db_loja)
    return {"status": "success", "loja": db_loja}




@router.get('/api/loja/{lojaId}')
def get_loja(lojaId: str, db: Session = Depends(get_db)):

    loja = db.query(Loja).filter(Loja.id == lojaId).first()
    if not loja:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No loja with this id: {lojaId} found")
    return {"status": "success", "loja": loja}




@router.delete('/api/loja/{lojaId}')
def delete_loja(lojaId: str, db: Session = Depends(get_db)):

    loja_query = db.query(Loja).filter(Loja.id == lojaId)
    db_loja = loja_query.first()

    if not db_loja:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No loja with this id: {lojaId} found')
    loja_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


