# IP-API

一个部署在服务器上的支持跨域的IP查询服务，返回访问者的IP及其地理位置信息。

<p>IP地址位置数据由<a href="https://www.cz88.net">纯真CZ88</a>提供支持</p>

## 环境变量

1. `KEY`: 用于czdb解码的密钥，不配置则关闭解析地理位置信息
2. `DOWNLOAD_KEY`：下载czdb的UUID，指下载链接后面的key参数
3. `UPDATE_TIME`：每天更新czdb的时间，默认为`12:00`，需要注意的是这个时间默认为格林威治标准时间。
4. `SUBURL`：api的子路径，默认为`/`
5. `PORT`：端口，默认为`8000`
6. `DB_PATH`：czdb文件路径，默认为`./data`

## 使用

### Docker

#### 无CZDB启动，仅返回IP

```bash
docker run -d --restart=always --name ipapi \
    -e PORT=5125 \
    -e SUBURL=/get-ip \
    --network host \
    do1e/ip-api:latest
```

#### 使用CZDB解析地理位置信息

```bash
docker run -d --restart=always --name ipapi \
    -e PORT=5125 \
    -e SUBURL=/get-ip \
    -e DOWNLOAD_KEY=abcdefgh-0312-2001-3012-666666666666 \
    -e KEY=ABCDEFGhijklmnopqrsTUV== \
    -v ./data:/app/data \
    --network host \
    do1e/ip-api:latest
```

#### nginx反代参考

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name example.com;
    access_log /var/log/nginx/ipapi.access.log;
    error_log /var/log/nginx/ipapi.error.log;
    location /get-ip {
        proxy_pass http://127.0.0.1:5125;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Real-PORT $remote_port;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

加上`-v /etc/localtime:/etc/localtime:ro`以使用系统时间进行更新。或者`-e TZ=xxx`指定时区，如`-e TZ=Asia/Shanghai`。

#### 返回示例

IPv4  
```json
{
  "ip": "114.xxx.xxx.xxx",
  "region": "中国–江苏–南京 教育网/南京大学",
  "error": null
}
```

IPv6  
```json
{
  "ip": "2001:xxxx:xxxx:xxxx::xxxx",
  "region": "中国 教育网",
  "error": null
}
```

### 本地或Vercel部署

```bash
git clone https://github.com/tagphi/czdb_searcher_python.git
mv czdb_searcher_python/czdb .
rm -rf czdb_searcher_python
pip install -r requirements.txt
```

新建`.env`文件如下，填入环境变量，然后运行`python main.py`即可。

```dotenv
PORT=5125
SUBURL=get-ip
DOWNLOAD_KEY=abcdefgh-0312-2001-3012-666666666666
KEY=ABCDEFGhijklmnopqrsTUV==
DB_PATH=/tmp
UPDATE_TIME=12:00
```

完成上述配置后，可以使用`vercel`部署。

```bash
npm install -g vercel
vercel login
vercel --prod
```

注：Vercel部署时`DB_PATH`仅能在/tmp目录下
