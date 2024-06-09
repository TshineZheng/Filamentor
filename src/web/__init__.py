from src.web.controller.router import router as controller_router
from src.web.sys.router import router as sys_router
from src.web.printer.router import router as printer_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, FastAPI
import json
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class ResponseMiddleware(BaseHTTPMiddleware):
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

        # 返回新的响应对象
        return new_response


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and len(record.args) >= 3 and record.args[2] != "/api/sys/sync"


def init(fast_api: FastAPI):
    # Add filter to the logger
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

    fast_api.add_middleware(ResponseMiddleware)

    fast_api.add_middleware(
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

    fast_api.include_router(api_router, prefix="/api")
