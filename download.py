import os
import logging
import zipfile
import requests


def download(db_path):
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    filenames = ["czdb.zip", "cz88_public_v4.czdb", "cz88_public_v6.czdb"]
    filenames = [f"{db_path}/{filename}" for filename in filenames]
    key = os.environ.get("DOWNLOAD_KEY")
    if not key:
        raise ValueError("Please set the DOWNLOAD_KEY environment variable")
    link = f"https://www.cz88.net/api/communityIpAuthorization/communityIpDbFile?fn=czdb&key={key}"
    try:
        response = requests.get(link)
        with open(filenames[0], "wb") as f:
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

    if not os.path.exists(filenames[1]) or not os.path.exists(filenames[2]):
        logging.error("Unzip failed")
        return False
    if os.path.exists(filenames[0]):
        os.remove(filenames[0])
    logging.info("Update succeeded")
    return True


if __name__ == "__main__":
    print(download())
