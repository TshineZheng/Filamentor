import http
import http.server
import json
import os
import threading
from typing import Any, Union
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from src.utils.log import LOGI
from src.web.printer.router import router as printer_router
from src.web.sys.router import router as sys_router
from src.web.controller.router import router as controller_router
import src.core_services as core_services
from fastapi.middleware.cors import CORSMiddleware


class StandardResponse(BaseModel):
    code: int
    msg: str
    data: Union[Any, None] = None


class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        response = await call_next(request)

        if not request.url.path.startswith("/api"):
            return response

        # 获取响应内容
        response_body = [section async for section in response.body_iterator]
        response_body = b''.join(response_body).decode('utf-8')

        # 尝试解析响应内容为 JSON 对象
        try:
            response_data = json.loads(response_body)
        except json.JSONDecodeError:
            response_data = response_body

        # 根据状态码包装响应内容
        if response.status_code == 200:
            new_response = JSONResponse(
                status_code=response.status_code,
                content={
                    "code": response.status_code,
                    "message": "success",
                    "data": response_data
                }
            )
        else:
            msg = 'unknown error'
            if 'detail' in response_data:
                if isinstance(response_data['detail'], str):
                    msg = response_data['detail']
                elif isinstance(response_data['detail'], list):
                    detail = response_data['detail'][0]
                    if 'msg' in detail:
                        msg = detail['msg']

            new_response = JSONResponse(
                status_code=response.status_code,
                content={
                    "code": response.status_code,
                    "message": msg,
                    "data": None,
                    "error": response_data
                }
            )

        # new_response.headers["Access-Control-Allow-Origin"] = "*"
        # new_response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE, PUT"
        # new_response.headers["Access-Control-Allow-Headers"] = "*"

        # 返回新的响应对象
        return new_response


app = FastAPI()
httpfront: http.server.HTTPServer = None


class Handler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, directory='web')

    def log_message(self, format: str, *args: Any) -> None:
        pass


@app.on_event("startup")
async def startup_event():
    from loguru import logger
    import sys
    import src.consts as consts

    logger.remove(0)
    logger.add(sys.stderr, level="INFO")

    LOGI(f'startup_event')

    consts.setup()
    core_services.start()

    if os.path.exists('web'):
        global httpfront
        httpfront = http.server.HTTPServer(('', 8001), Handler)
        threading.Thread(target=httpfront.serve_forever).start()
        print("===================================")
        print("| 管理后台: http://localhost:8001 |")
        print("===================================")


@app.on_event("shutdown")
async def shutdown_event():
    core_services.stop()
    if httpfront:
        httpfront.shutdown()


app.add_middleware(CustomMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

api_router = APIRouter()
api_router.include_router(sys_router, prefix='/sys')
api_router.include_router(printer_router, prefix='/printer')
api_router.include_router(controller_router, prefix='/controller')

app.include_router(api_router, prefix="/api")
