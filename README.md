# IP-API

一个部署在服务器上的支持跨域的 IP 查询服务，返回访问者的 IP 及其地理位置信息。

<p>IP地址位置数据由 <a href="https://www.cz88.net">纯真 CZ88</a> 提供支持</p>

## 环境变量

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `KEY` | czdb 解码密钥。**不配置则关闭地理位置解析，仅返回 IP** | 空 |
| `DOWNLOAD_KEY` | 下载 czdb 的 UUID，即下载链接后的 `key` 参数 | 空 |
| `UPDATE_TIME` | 每天定时更新 czdb 的时间（格林威治标准时间） | `12:00` |
| `PORT` | 监听端口 | `8000` |
| `DB_PATH` | czdb 文件存放路径 | `data` |
| `IPV4_BASEURL` | 首页 HTML 中 IPv4 查询接口的基础地址 | 空 |
| `IPV6_BASEURL` | 首页 HTML 中 IPv6 查询接口的基础地址 | 空 |

## 接口

- `GET /` 返回查询页面（HTML）
- `GET /get-ip` 返回当前请求者的 IP 信息（JSON）
  - 可选查询参数 `?ip=<目标IP>`，查询指定 IP

### 返回示例

配置了 `KEY` 时（IPv4）：

```json
{
  "ip": "114.xxx.xxx.xxx",
  "region": "中国 江苏 南京 教育网/南京大学",
  "db_update_time": "2026-07-03",
  "error": null
}
```

未配置 `KEY` 时，仅返回 IP，`region` 与 `db_update_time` 为 `null`：

```json
{
  "ip": "114.xxx.xxx.xxx",
  "region": null,
  "db_update_time": null,
  "error": null
}
```

## 部署

### Docker

#### 无 CZDB 启动，仅返回 IP

```bash
docker run -d --restart=always --name ipapi \
    -e PORT=8000 \
    --network host \
    do1e/ip-api:latest
```

#### 使用 CZDB 解析地理位置信息

```bash
docker run -d --restart=always --name ipapi \
    -e PORT=8000 \
    -e DOWNLOAD_KEY=abcdefgh-0312-2001-3012-666666666666 \
    -e KEY=ABCDEFGhijklmnopqrsTUV== \
    -v ./data:/app/data \
    --network host \
    do1e/ip-api:latest
```

> 定时更新使用容器内时间，`-e TZ=Asia/Shanghai` 指定时区。

#### nginx 反代参考

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name ipapi.example.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
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


#### 双栈部署（IPv4 + IPv6）

通过两个域名解析到同一台服务器，分别只走 IPv4 / IPv6 链路，从而在前端分别获取访问者的 IPv4 和 IPv6 地址。

1. 准备两个域名，DNS 只各配一种记录：

   | 域名 | 记录类型 | 指向 |
   | --- | --- | --- |
   | `ip4.example.com` | A | 服务器 IPv4 地址 |
   | `ip6.example.com` | AAAA | 服务器 IPv6 地址 |

   客户端访问 `ip4.example.com` 时只会拿到 IPv4 地址，自然走 IPv4 链路；`ip6.example.com` 同理只走 IPv6 链路。

2. nginx 为两个域名各建一个 server，都反代到本机同一个服务：

   ```nginx
   server {
       listen 443 ssl;
       listen [::]:443 ssl;
       server_name ip4.example.com ip6.example.com;
       location / {
           proxy_pass http://127.0.0.1:8000;
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

3. 设置环境变量，让首页按协议请求对应域名：

   ```bash
   IPV4_BASEURL=https://ip4.example.com
   IPV6_BASEURL=https://ip6.example.com
   ```

   前端点击「IPv4」会请求 `ip4.example.com/get-ip`，点击「IPv6」会请求 `ip6.example.com/get-ip`，分别拿到访问者在两条链路上的真实地址。

### 本地运行

需 Python ≥ 3.14，推荐使用 [uv](https://docs.astral.sh/uv/)：

```bash
uv sync
uv run python -m src.main
```
