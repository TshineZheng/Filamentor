from fastapi import FastAPI
import src.web as web

app = FastAPI()
web.init(app)


@app.on_event("startup")
async def startup_event():
    from loguru import logger
    import sys
    import src.consts as consts
    import src.core_services as core_services
    import src.web.front as front
    from dotenv import load_dotenv

    load_dotenv()

    logger.remove(0)
    logger.add(sys.stderr, level="INFO")

    consts.setup()
    core_services.start()
    front.start()


@app.on_event("shutdown")
async def shutdown_event():
    import src.core_services as core_services
    import src.web.front as front
    core_services.stop()
    front.stop()
