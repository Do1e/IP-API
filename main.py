from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
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
db_path = os.environ.get("DB_PATH", "data")

logging.basicConfig(level=logging.INFO)
logging.info(f"key: {key}")
logging.info(f"suburl: {suburl}")
logging.info(f"update_time: {update_time}")
logging.info(f"db_path: {db_path}")

if key:  # 如果配置可czdb的密钥，就会每天定时更新
    if not os.path.exists(f"{db_path}/cz88_public_v4.czdb") or not os.path.exists(f"{db_path}/cz88_public_v6.czdb"):
        download(db_path)

app = FastAPI()

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
    if request.query_params.get("ip"):
        client_ip = request.query_params["ip"]
    try:
        if key:
            if not os.path.exists(f"{db_path}/cz88_public_v4.czdb") or not os.path.exists(f"{db_path}/cz88_public_v6.czdb"):
                download(db_path)
            if "." in client_ip:
                db_searcher = DbSearcher(f"{db_path}/cz88_public_v4.czdb", "BTREE", key)
                res = db_searcher.search("255.255.255.255")
                if isinstance(res, bytes):
                    res = res.decode("utf-8")
                db_update_time = res.split("\t")[1].replace("IP数据", "")
            else:
                db_searcher = DbSearcher(f"{db_path}/cz88_public_v6.czdb", "BTREE", key)
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


@app.get("/updatedb")
async def update_db(request: Request):
    if "download_key" not in request.query_params:
        return JSONResponse(
            content={"error": "Please provide the download key"}, status_code=400
        )
    if request.query_params["download_key"] != os.environ.get("DOWNLOAD_KEY"):
        return JSONResponse(content={"error": "Invalid download key"}, status_code=400)
    if download(db_path):
        return JSONResponse(content={"message": "Update succeeded"})
    else:
        return JSONResponse(content={"error": "Update failed"}, status_code=500)


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        download,
        "cron",
        hour=update_time.split(":")[0],
        minute=update_time.split(":")[1],
        args=[db_path],
    )
    scheduler.start()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="*", port=port, reload=False)
