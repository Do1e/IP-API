from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import os
import logging
from czdb.db_searcher import DbSearcher
from download import download

load_dotenv()

key = os.environ.get("KEY")
suburl = os.environ.get("SUBURL", "/")
if not suburl.startswith("/"):
    suburl = "/" + suburl
update_time = os.environ.get("UPDATE_TIME", "12:00")

logging.basicConfig(level=logging.INFO)
logging.info(f"key: {key}")
logging.info(f"suburl: {suburl}")
logging.info(f"update_time: {update_time}")

scheduler = AsyncIOScheduler()
db_path = "data"

if key:  # 如果配置可czdb的密钥，就会每天定时更新

    @scheduler.scheduled_job(
        "cron", hour=update_time.split(":")[0], minute=update_time.split(":")[1]
    )
    def update():
        download(db_path)

    @asynccontextmanager
    async def run_scheduler(app: FastAPI):
        if not os.path.exists(f"{db_path}/cz88_public_v4.czdb") or not os.path.exists(
            f"{db_path}/cz88_public_v6.czdb"
        ):
            download(db_path)
        try:
            scheduler.start()
            yield
        finally:
            scheduler.shutdown()

else:
    run_scheduler = None

app = FastAPI(lifespan=run_scheduler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(suburl)
async def get_ip(request: Request):
    client_ip = request.client.host
    try:
        if key:
            if "." in client_ip:
                db_searcher = DbSearcher(f"{db_path}/cz88_public_v4.czdb", "BTREE", key)
                db_update_time = (
                    db_searcher.search("255.255.255.255")
                    .decode("utf-8")
                    .split("\t")[1]
                    .replace("IP数据", "")
                )
            else:
                db_searcher = DbSearcher(f"{db_path}/cz88_public_v6.czdb", "BTREE", key)
                db_update_time = None
            region = db_searcher.search(client_ip).decode("utf-8")
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
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="*", port=port, reload=False)
