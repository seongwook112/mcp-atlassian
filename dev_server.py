#!/usr/bin/env python3
"""
개발용 자동 재시작 서버
파일 변경 시 자동으로 MCP 서버를 재시작합니다.
"""

import subprocess
import sys
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ServerRestartHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_server()

    def on_modified(self, event):
        if event.is_directory:
            return

        # Python 파일만 감지
        if event.src_path.endswith(".py"):
            print(f"\n📝 파일 변경 감지: {event.src_path}")
            self.restart_server()

    def restart_server(self):
        if self.process:
            print("🔄 서버 중지 중...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

        print("🚀 서버 재시작 중...")
        # mcp-atlassian 명령 직접 사용
        self.process = subprocess.Popen(
            [
                "mcp-atlassian",
                "--transport",
                "streamable-http",
                "--port",
                "8000",
            ]
        )
        print("✅ 서버가 http://0.0.0.0:8000/mcp 에서 실행 중입니다")

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()


def main():
    print("🔍 개발용 자동 재시작 서버 시작")
    print("💡 Python 파일 변경 시 자동으로 서버를 재시작합니다")
    print("🛑 Ctrl+C로 종료할 수 있습니다\n")

    # 현재 디렉터리에서 src 폴더 감지
    watch_path = Path("src")
    if not watch_path.exists():
        watch_path = Path(".")

    event_handler = ServerRestartHandler()
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 서버 종료 중...")
        event_handler.stop()
        observer.stop()

    observer.join()
    print("👋 서버가 종료되었습니다")


if __name__ == "__main__":
    main()
