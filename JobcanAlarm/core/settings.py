"""설정 저장/로드 모듈 - JSON 파일 기반"""

import json
import os
from pathlib import Path

SETTINGS_DIR = Path(os.environ.get("APPDATA", Path.home())) / "JobcanAlarm"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "alarms": [
        {
            "id": "clock_in",
            "label": "출근 알림",
            "time": "08:50",
            "message": "출근 체크할 시간입니다! Jobcan에서 출근 버튼을 눌러주세요.",
            "enabled": True,
        },
        {
            "id": "clock_out",
            "label": "퇴근 알림",
            "time": "18:00",
            "message": "퇴근 시간입니다! Jobcan에서 퇴근 버튼을 눌러주세요.",
            "enabled": True,
        },
    ],
    "start_minimized": False,
}


def load_settings() -> dict:
    """설정 파일을 읽어서 반환. 없으면 기본값 생성 후 반환."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 누락된 키가 있으면 기본값으로 채움
            for key, value in DEFAULT_SETTINGS.items():
                if key not in data:
                    data[key] = value
            return data
        except (json.JSONDecodeError, IOError):
            pass
    return json.loads(json.dumps(DEFAULT_SETTINGS))  # deep copy


def save_settings(settings: dict) -> None:
    """설정을 JSON 파일에 저장."""
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
