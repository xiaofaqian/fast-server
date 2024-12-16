import os
import psutil
import subprocess

def find_and_kill_process_using_port(port):
    """查找并终止使用指定端口的进程"""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    print(f"终止进程 {proc.info['name']} (PID: {proc.info['pid']}) 使用端口 {port}")
                    proc.terminate()
                    proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def start_uvicorn(port):
    """启动 Uvicorn 服务器"""
    cmd = f"nohup uvicorn app.main:app --host 0.0.0.0 --port {port} --reload  > {port}.log 2>&1 &"
    print(f"启动 Uvicorn 在端口 {port}")
    subprocess.run(cmd, shell=True, check=True)

def main():
    for port in range(5001, 5006):
        find_and_kill_process_using_port(port)
        start_uvicorn(port)

if __name__ == '__main__':
    main()