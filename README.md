# portscan

基于多线程、服务器端口扫描脚本，支持B段和C段。

## Usage

```bash
python36 portscan.py <target ip or ips> <port or ports> <threads_number>
python36 portscan.py 127.0.0.1 80 20
python36 portscan.py 127.0.0.1-255 80,81 50
python36 portscan.py 127.0.0.1-255 80-100 50
```
