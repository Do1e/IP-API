# IP-API

一个部署在服务器上的支持跨域的IP查询服务，返回访问者的IP及其地理位置信息。

<p>IP地址位置数据由<a href="https://www.cz88.net">纯真CZ88</a>提供支持</p>

## 环境变量

1. `KEY`: 用于czdb解码的密钥，不配置则关闭解析地理位置信息
2. `DOWNLOAD_KEY`：下载czdb的UUID，指下载链接后面的key参数
3. `UPDATE_TIME`：每天更新czdb的时间，默认为`12:00`秒
4. `SUBURL`：api的子路径，默认为`/`
5. `PORT`：端口，默认为`8000`

## 使用

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
