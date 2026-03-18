"""JobcanAlarm - 개인용 근태 알림 프로그램

실행: python main.py
"""

import logging
import sys
import os

# PyInstaller로 빌드 시 경로 보정
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 모듈 경로 추가 (프로젝트 루트)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import JobcanAlarmApp


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )
    app = JobcanAlarmApp()
    app.mainloop()


if __name__ == "__main__":
    main()
