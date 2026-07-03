import logging
from pathlib import Path

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from czdb.db_searcher import DbSearcher
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from .config import settings
from .download import download


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info(f"key: {settings.key[:4]}*****")
logging.info(f"update_time: {settings.update_time}")
logging.info(f"db_path: {settings.db_path}")

if settings.key:
    if (
        not Path(f"{settings.db_path}/cz88_public_v4.czdb").exists()
        or not Path(f"{settings.db_path}/cz88_public_v6.czdb").exists()
    ):
        download(settings.db_path, settings.download_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    html = Path("html/index.html").read_text(encoding="utf-8")
    html = html.replace("{{ IPV4_BASEURL }}", settings.ipv4_baseurl)
    html = html.replace("{{ IPV6_BASEURL }}", settings.ipv6_baseurl)
    return HTMLResponse(content=html)


@app.get("/get-ip")
async def get_ip(request: Request):
    client_ip = request.client.host
    if request.query_params.get("ip"):
        client_ip = request.query_params["ip"]
    try:
        if settings.key:
            if (
                not Path(f"{settings.db_path}/cz88_public_v4.czdb").exists()
                or not Path(f"{settings.db_path}/cz88_public_v6.czdb").exists()
            ):
                download(settings.db_path, settings.download_key)
            if "." in client_ip:
                db_searcher = DbSearcher(
                    f"{settings.db_path}/cz88_public_v4.czdb", "BTREE", settings.key
                )
                res = db_searcher.search("255.255.255.255")
                if isinstance(res, bytes):
                    res = res.decode("utf-8")
                db_update_time = res.split("\t")[1].replace("IP数据", "")
            else:
                db_searcher = DbSearcher(
                    f"{settings.db_path}/cz88_public_v6.czdb", "BTREE", settings.key
                )
                res = db_searcher.search("::1")
                if isinstance(res, bytes):
                    res = res.decode("utf-8")
                db_update_time = res.split("\t")[1].replace("IP数据", "")
            region = db_searcher.search(client_ip)
            if isinstance(region, bytes):
                region = region.decode("utf-8")
            region = region.replace("\t", " ") if region else None
        else:
            region = None
            db_update_time = None
        return JSONResponse(
            content={
                "ip": client_ip,
                "region": region,
                "db_update_time": db_update_time,
                "error": None,
            }
        )
    except Exception as e:
        region = None
        db_update_time = None
        return JSONResponse(
            content={
                "ip": client_ip,
                "region": region,
                "db_update_time": db_update_time,
                "error": str(e),
            },
            status_code=500,
        )


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        download,
        "cron",
        hour=settings.update_time.split(":")[0],
        minute=settings.update_time.split(":")[1],
        args=[settings.db_path, settings.download_key],
    )
    scheduler.start()
    uvicorn.run(app, host="*", port=settings.port, reload=False, log_config=None)
