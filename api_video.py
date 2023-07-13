from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import remove_person as rp

router = APIRouter()

@router.post("/api/process")
def process(caminho_imagem_original: str, gray: bool):

    image_stream = rp.start(
        original_image=caminho_imagem_original, gray=gray
    )
    return StreamingResponse(content=image_stream, media_type="image/png")



