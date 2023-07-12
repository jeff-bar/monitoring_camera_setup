#!/usr/bin/env python3

import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


import api_line, api_polygon, api_video, api_loja, api_heat_map, api_camera

app = FastAPI(title="Rest API Example", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_line.router, tags=['Line'])
app.include_router(api_polygon.router, tags=['Polygon'])
app.include_router(api_heat_map.router, tags=['Heat Map'])
app.include_router(api_video.router, tags=['Video'])
app.include_router(api_loja.router, tags=['Loja'])
app.include_router(api_camera.router, tags=['Camera'])
