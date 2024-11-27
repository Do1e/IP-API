import os
import subprocess
import logging


def download(db_path):
    filenames = ["czdb.zip", "cz88_public_v4.czdb", "cz88_public_v6.czdb"]
    filenames = [f"{db_path}/{filename}" for filename in filenames]
    key = os.environ.get("DOWNLOAD_KEY")
    if not key:
        raise ValueError("Please set the DOWNLOAD_KEY environment variable")
    link = f"https://www.cz88.net/api/communityIpAuthorization/communityIpDbFile?fn=czdb&key={key}"
    result = subprocess.run(
        ["curl", "-o", filenames[0], link], capture_output=True, text=True
    )
    if result.returncode != 0:
        logging.warning(result.stderr)
    if not os.path.exists(filenames[0]):
        logging.error("Download failed")
        return False
    result = subprocess.run(
        ["unzip", "-o", filenames[0], "-d", db_path], capture_output=True, text=True
    )
    if result.returncode != 0:
        logging.error(result.stderr)
        return False
    if not os.path.exists(filenames[1]) or not os.path.exists(filenames[2]):
        logging.error("Unzip failed")
        return False
    if os.path.exists(filenames[0]):
        os.remove(filenames[0])
    return True


if __name__ == "__main__":
    print(download())
