FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN sed -i 's|http://deb.debian.org/debian|https://mirror.nju.edu.cn/debian|' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get install -y git curl zip
RUN git clone https://github.com/tagphi/czdb_searcher_python.git && \
    mv czdb_searcher_python/czdb . && \
    rm -rf czdb_searcher_python
RUN pip3 install -i https://mirror.nju.edu.cn/pypi/web/simple --no-cache-dir -r requirements.txt
COPY main.py .
COPY download.py .
VOLUME /app/data
CMD ["python3", "main.py"]
