import cv2
import numpy as np
import torch
from PIL import Image
from loguru import logger
import io
import imghdr
from model_manager import ModelManager
from model.utils import torch_gc
from schema import Config
import multiprocessing
import os
import random
from ultralytics import YOLO
from ultralytics.yolo.utils.ops import scale_image
from dataclasses import dataclass


os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"


NAME_MODEL_INPAINT="lama"
NAME_MODEL_MASK='yolov8x-seg.pt'
CONF=0.20


DEVIDE = 0 if torch.cuda.is_available() else "cpu"


from helper import (
    load_img,
    resize_max_size,
    pil_to_bytes,
)


NUM_THREADS = str(multiprocessing.cpu_count())

os.environ["OMP_NUM_THREADS"] = NUM_THREADS
os.environ["OPENBLAS_NUM_THREADS"] = NUM_THREADS
os.environ["MKL_NUM_THREADS"] = NUM_THREADS
os.environ["VECLIB_MAXIMUM_THREADS"] = NUM_THREADS
os.environ["NUMEXPR_NUM_THREADS"] = NUM_THREADS
if os.environ.get("CACHE_DIR"):
    os.environ["TORCH_HOME"] = os.environ["CACHE_DIR"]


@dataclass(frozen=True)
class CV2Flag():
    INPAINT_NS = 'INPAINT_NS',
    INPAINT_TELEA = 'INPAINT_TELEA',


@dataclass(frozen=True)
class SDSampler():
    ddim = 'ddim',
    pndm = 'pndm',
    klms = 'k_lms',
    kEuler = 'k_euler',
    kEulerA = 'k_euler_a',
    dpmPlusPlus = 'dpm++',
    uni_pc = 'uni_pc',


@dataclass(frozen=True)
class LAMA():
    hdStrategy: str ="Crop",
    hdStrategyResizeLimit:int = 2048,
    hdStrategyCropTrigerSize:int = 800,
    hdStrategyCropMargin:int =196,
    enabled:bool = True


@dataclass(frozen=True)
class LDM():
    hdStrategy = "Crop",
    hdStrategyResizeLimit = 1080,
    hdStrategyCropTrigerSize = 1080,
    hdStrategyCropMargin= 128,
    enabled= True



class RemovePerson():

    def __init__(self, image_quality=100) -> None:
        
        self.name_model = NAME_MODEL_INPAINT
        self.model = ModelManager(name=self.name_model, device=DEVIDE)
        self.image_quality=image_quality


    def inpaint(self, origin_image_bytes , mask_image_bytes, gray ):

        image, alpha_channel, exif_infos = load_img(origin_image_bytes, return_exif=True)

        mask, _ = load_img( mask_image_bytes , gray=True)
        mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]

        if image.shape[:2] != mask.shape[:2]:
            return (
                f"Mask shape{mask.shape[:2]} not queal to Image shape{image.shape[:2]}",
                400,
            )

        original_shape = image.shape
        interpolation = cv2.INTER_CUBIC

        size_limit = max(image.shape)

        config = self.get_conf( )


        logger.info(f"Origin image shape: {original_shape}")
        image = resize_max_size(image, size_limit=size_limit, interpolation=interpolation)

        mask = resize_max_size(mask, size_limit=size_limit, interpolation=interpolation)

        try:
            res_np_img = self.model(image, mask, config)
        except RuntimeError as e:
            if "CUDA out of memory. " in str(e):
                # NOTE: the string may change?
                return "CUDA out of memory", 500
            else:
                logger.exception(e)
                return f"{str(e)}", 500
        finally:
            torch_gc()

        if gray:
            res_np_img = cv2.cvtColor(res_np_img.astype(np.uint8), cv2.COLOR_BGR2GRAY) 
        else:
            res_np_img = cv2.cvtColor(res_np_img.astype(np.uint8), cv2.COLOR_BGR2RGB)
        
        if alpha_channel is not None:
            if alpha_channel.shape[:2] != res_np_img.shape[:2]:
                alpha_channel = cv2.resize(
                    alpha_channel, dsize=(res_np_img.shape[1], res_np_img.shape[0])
                )
            res_np_img = np.concatenate(
                (res_np_img, alpha_channel[:, :, np.newaxis]), axis=-1
            )

        ext = self.get_image_ext(origin_image_bytes)

        bytes_io = io.BytesIO(
            pil_to_bytes(
                Image.fromarray(res_np_img),
                ext,
                quality=self.image_quality,
                exif_infos=exif_infos,
            )
        )

        return bytes_io



    def get_conf( self, ppaintByExampleImage=None ):

        if ppaintByExampleImage is not None:
            paint_by_example_example_image, _ = load_img( ppaintByExampleImage )
            paint_by_example_example_image = Image.fromarray(paint_by_example_example_image)
        else:
            paint_by_example_example_image = None

        config = Config(
            ldm_steps=25,
            ldm_sampler="plms",
            hd_strategy=LAMA.hdStrategy[0] if self.name_model=="lama" else LDM.hdStrategy[0] ,
            zits_wireframe=True,
            hd_strategy_crop_margin= LAMA.hdStrategyCropMargin[0] if self.name_model=="lama" else LDM.hdStrategyCropMargin[0] , 
            hd_strategy_crop_trigger_size=LAMA.hdStrategyCropTrigerSize[0] if self.name_model=="lama" else LDM.hdStrategyCropTrigerSize[0] ,
            hd_strategy_resize_limit=LAMA.hdStrategyResizeLimit[0] if self.name_model=="lama" else LDM.hdStrategyResizeLimit[0] ,
            prompt="",
            negative_prompt="",
            use_croper=False,
            croper_x=149,
            croper_y=284,
            croper_height=512,
            croper_width=512,
            sd_scale=1.0,
            sd_mask_blur=5,
            sd_strength=0.75,
            sd_steps=50,
            sd_guidance_scale=7.5,
            sd_sampler=SDSampler.uni_pc[0] ,
            sd_seed=179140097,
            sd_match_histograms=False,
            cv2_flag=CV2Flag.INPAINT_NS[0] ,
            cv2_radius=5,
            paint_by_example_steps=50,
            paint_by_example_guidance_scale= 7.5,
            paint_by_example_mask_blur=5,
            paint_by_example_seed=565760094,
            paint_by_example_match_histograms=False,
            paint_by_example_example_image=paint_by_example_example_image,
            p2p_steps=50,
            p2p_image_guidance_scale=1.5,
            p2p_guidance_scale=7.5,
            controlnet_conditioning_scale=0.4,
            controlnet_method="control_v11p_sd15_canny", #control_v11p_sd15_inpaint control_v11p_sd15_canny
        )

        if config.sd_seed == -1:
            config.sd_seed = random.randint(1, 999999999)
        if config.paint_by_example_seed == -1:
            config.paint_by_example_seed = random.randint(1, 999999999)

        return config


    def get_image_ext(self, img_bytes=None):
        return "png"
        #w = imghdr.what("", img_bytes)
        #if w is None:
        #    w = "jpeg"
        #return w



class CaptureImage():

    def __init__(self) -> None:
        self.device=DEVIDE
        self.conf=CONF
        self.modelYolo = YOLO(NAME_MODEL_MASK)
        self.caminho_repositorio_video = '../../../../videos/'

    def process(self, video):

        _video = os.path.join( self.caminho_repositorio_video, video ) 
        ret_val, frame = self.recuperaFrame( _video )
        if ret_val:
            return frame , self.mask( frame )


    def recuperaFrame(self, video):

        cap = cv2.VideoCapture(video)
        return cap.read()
            

    def mask(self, frame):

        results = self.modelYolo.predict(source=frame, 
                        conf=self.conf, 
                        classes=0,
                        iou=0.5,
                        device=self.device, 
                        half=True,
                        retina_masks=True, 
                        show=False, 
                        save=False, 
                        vid_stride=True,
                        save_txt=False)
    
        if results[0] is not None:

            boxes, masks = self.detect_person( results[0] )

            image_with_masks = np.copy(frame)

            ret,background = cv2.threshold(image_with_masks,255,255,cv2.THRESH_BINARY)

            if ret == False:
                raise("Erro para gerar o mask")

            for mask in masks:
                background = self.overlay(background, mask, color=(255,255,255), alpha=2.0)

            transparent_image_with_masks = self.transparent_image( background )    

            return transparent_image_with_masks



    def transparent_image(self,imgnp):

        rgba = cv2.cvtColor(imgnp, cv2.COLOR_RGB2RGBA)

        white = np.sum(rgba[:,:,:3], axis=2)
        white_mask = np.where(white != 255*3, 1, 0)

        alpha = np.where(white_mask, 0, rgba[:,:,-1])

        rgba[:,:,-1] = alpha 

        return rgba
    



    def overlay(self, image, mask, color, alpha, resize=None):

        """
        Params:
            image: Imagem de treino. np.ndarray,
            mask: Máscara de segmentação. np.ndarray,
            color: Cor para renderização da máscara de segmentação. tupla[int, int, int] = (255, 0, 0)
            alpha: Transparência da máscara de segmentação. flutuante = 0,5,
            resize: Se fornecido, a imagem e sua máscara são redimensionadas antes de serem mescladas. tuple[int, int] = (1024, 1024))

        Returns:
            image_combined: A imagem combinada. np.ndarray
        """
        color = color[::-1]
        colored_mask = np.expand_dims(mask, 0).repeat(3, axis=0)
        colored_mask = np.moveaxis(colored_mask, 0, -1)
        masked = np.ma.MaskedArray(image, mask=colored_mask, fill_value=color)
        image_overlay = masked.filled()

        if resize is not None:
            image = cv2.resize(image.transpose(1, 2, 0), resize)
            image_overlay = cv2.resize(image_overlay.transpose(1, 2, 0), resize)

        image_combined = cv2.addWeighted(image, 1 - alpha, image_overlay, alpha, 0)

        return image_combined



    def detect_person(self, result):

        # result.boxes.xyxy   # box with xyxy format, (N, 4)
        #cls = result.boxes.cls.cpu().numpy()    # cls, (N, 1)
        #probs = result.boxes.conf.cpu().numpy()  # confidence score, (N, 1)
        boxes = result.boxes.xyxy.cpu().numpy()   # box with xyxy format, (N, 4)

        # segmentation
        masks = result.masks.masks.cpu().numpy()     # masks, (N, H, W)
        masks = np.moveaxis(masks, 0, -1) # masks, (H, W, N)
        # rescale masks to original image
        #masks = scale_image(masks.shape[:2], masks, result.masks.orig_shape)
        masks = np.moveaxis(masks, -1, 0) # masks, (N, H, W)

        return boxes, masks



def start(original_image, gray=True ):

    '''
    capture_image = CaptureImage()

    image, mask = capture_image.process( original_image  )

    res_np_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    '''
    res_np_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY) 
    
    bytes_io = io.BytesIO(
            pil_to_bytes(
                Image.fromarray(res_np_img),
                "png",
                quality=95
            )
        )

    return bytes_io


    '''
    is_success_img, buffer_image = cv2.imencode(".png", image)
    is_success_mask, buffer_mask = cv2.imencode(".png", mask)

    if is_success_img == True and is_success_mask == True:

        remove_person = RemovePerson()
        return remove_person.inpaint(buffer_image , buffer_mask , gray )

    else:
        raise("Não é possível ler a imagem")

    '''   


if __name__ == '__main__':

    #caminho_imagem_original="imagens/jefferson_4.jpeg"
    #caminho_imagem_original="imagens/bus.jpg"
    #caminho_imagem_original="imagens/remove/Imagen3.png"
    #caminho_imagem_original="imagens/remove/teste.png"
    caminho_imagem_original="ENTRADA_2_2023-06-10_13_38_03_646.asf"


   
    name_model_mask="yolov8x-seg.pt" 
    name_model_inpaint="lama"
    #name_model_inpaint="ldm"

    img = start(
        original_image=caminho_imagem_original, 
        name_model_mask=name_model_mask,
        name_model_inpaint=name_model_inpaint
    )

    with open("teste_ok.jpeg", "wb") as f:
        f.write(img.getbuffer())




