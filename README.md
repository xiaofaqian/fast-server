# fast-server 部署说明

本文档记录在阿里云 Ubuntu 20.04 (root) 环境中部署本项目（FastAPI + MongoDB + Redis）的完整步骤。

## 1. 基础环境

- 操作系统：Ubuntu 20.04.6 LTS
- Python：3.8.10（系统自带）
- MongoDB：3.6.8（APT 安装）
- Redis：5.0.7（APT 安装）
- 部署目录：`/opt/fast-server`
- systemd 服务名：`fast-server`

## 2. 安装系统依赖

```bash
apt-get update
apt-get install -y git python3-venv python3-pip python3-dev \
  build-essential libffi-dev libssl-dev libpq-dev \
  mongodb redis-server
```

安装完毕后建议执行以下命令确认可用：

```bash
git --version
python3 --version
mongo --eval 'db.runCommand({ ping: 1 })'
redis-cli ping
```

## 3. 克隆仓库并创建虚拟环境

```bash
rm -rf /opt/fast-server
git clone https://<token>@github.com/xiaofaqian/fast-server.git /opt/fast-server
python3 -m venv /opt/fast-server/venv
source /opt/fast-server/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install PyJWT requests
```

> 说明：`PyJWT` 与 `requests` 为运行过程中实际用到但未在原始依赖中声明的库，需手动补充安装。

## 4. 环境变量与配置

项目启动时会读取工作目录下的 `.env` 文件，可基于仓库提供的 `.env.example` 创建：

```bash
cp .env.example .env
```

示例配置：

```dotenv
API_V1_STR=/api/v1
PROJECT_NAME=Fast Server
MONGODB_URL=mongodb://127.0.0.1:27017
MONGODB_DATABASE=fastserver
REDIS_URL=redis://127.0.0.1:6379
SECRET_KEY=dBqk3X_wLv-5KBxZgATHf8Xr4YpvjqHKM2Qh9tRnUJs
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

如需自定义 CORS 白名单，可在 `.env` 中新增 `BACKEND_CORS_ORIGINS`，使用 JSON 数组格式（例如 `["http://example.com"]`）。

## 5. 初始化管理员账号（可选）

仓库提供脚本 `scripts/init_admin.py`，可在虚拟环境中运行以创建默认管理员（用户名 `nongfu`，密码 `shanquan`）：

```bash
source /opt/fast-server/venv/bin/activate
python scripts/init_admin.py
```

脚本会自动连接 MongoDB：若管理员不存在则创建，已存在则输出提示。

## 6. 配置 systemd 服务

新建 `/etc/systemd/system/fast-server.service`：

```ini
[Unit]
Description=Fast Server FastAPI Service
After=network.target mongodb.service redis-server.service

[Service]
User=root
WorkingDirectory=/opt/fast-server
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/fast-server/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8003
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

加载并启动服务：

```bash
systemctl daemon-reload
systemctl enable --now fast-server
```

常用运维命令：

```bash
systemctl status fast-server
journalctl -u fast-server -n 100 --no-pager
systemctl restart fast-server
systemctl stop fast-server
```

## 7. 运行验证

确认服务启动后，可通过以下命令检查：

```bash
curl http://127.0.0.1:8003/
# 期望输出：{"Hello":"World"}
```

若要验证数据库连接：

```bash
mongo --eval 'db.runCommand({ ping: 1 })'
redis-cli ping
```

## 8. 日志位置

默认通过 `journalctl` 查看服务日志：

```bash
journalctl -u fast-server -f
```

如需输出到独立文件，可在 systemd 单元内调整 `StandardOutput` / `StandardError`。

## 9. 更新流程

```bash
cd /opt/fast-server
source venv/bin/activate
git pull
pip install -r requirements.txt
systemctl restart fast-server
```

请在发布新版本或调整配置后，更新相关运维文档与日志记录。
