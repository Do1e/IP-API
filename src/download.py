import logging
import zipfile
from pathlib import Path

import requests


def download(db_path, key):
    if not Path(db_path).exists():
        Path(db_path).mkdir(parents=True)
    filenames = ["czdb.zip", "cz88_public_v4.czdb", "cz88_public_v6.czdb"]
    filenames = [f"{db_path}/{filename}" for filename in filenames]
    if not key:
        raise ValueError("Please provide the download key")
    link = f"https://www.cz88.net/api/communityIpAuthorization/communityIpDbFile?fn=czdb&key={key}"
    try:
        response = requests.get(link)
        with Path(filenames[0]).open("wb") as f:
            f.write(response.content)
    except requests.exceptions.RequestException as e:
        logging.error(f"Download failed: {e}")
        return False

    try:
        with zipfile.ZipFile(filenames[0], "r") as zip_ref:
            zip_ref.extractall(db_path)
    except zipfile.BadZipFile as e:
        logging.error(f"Bad zip file: {e}")
        return False

    if not Path(filenames[1]).exists() or not Path(filenames[2]).exists():
        logging.error("Unzip failed")
        return False
    if Path(filenames[0]).exists():
        Path(filenames[0]).unlink()
    logging.info("Update succeeded")
    return True
