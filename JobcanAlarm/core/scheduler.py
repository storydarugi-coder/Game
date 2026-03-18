"""알림 스케줄 관리 모듈

schedule 라이브러리 없이 직접 시간을 비교하여 알림을 발송한다.
메인 스레드(Tkinter after 루프)에서 tick()을 호출해야 한다.
"""

import logging
from datetime import datetime

from core.notifier import send_notification

logger = logging.getLogger(__name__)


class AlarmScheduler:
    """매 초 현재 시각과 알림 시각을 비교하여 알림을 발송하는 스케줄러."""

    def __init__(self):
        self._alarms: list[dict] = []
        self._fired_today: set[str] = set()  # 오늘 이미 발송한 알림 ID
        self._last_date: str = ""  # 날짜 변경 감지용

    def update_alarms(self, alarms: list[dict]) -> None:
        """알림 목록을 받아 스케줄을 재설정한다."""
        self._alarms = [a for a in alarms if a.get("enabled", False)]
        self._fired_today.clear()
        for alarm in self._alarms:
            logger.info(
                "알림 등록: %s %s (%s)",
                alarm.get("label", "알림"),
                alarm["time"],
                alarm.get("message", ""),
            )

    def tick(self) -> None:
        """메인 스레드에서 매 초 호출. 현재 시각과 알림 시각을 비교하여 발송."""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")

        # 날짜가 바뀌면 발송 기록 초기화
        if today != self._last_date:
            self._fired_today.clear()
            self._last_date = today

        for alarm in self._alarms:
            alarm_id = alarm.get("id", alarm["time"])
            if alarm_id in self._fired_today:
                continue
            if alarm["time"] == current_time:
                self._fired_today.add(alarm_id)
                title = alarm.get("label", "Jobcan 알림")
                message = alarm.get("message", "Jobcan을 확인하세요!")
                try:
                    logger.info("알림 발송 시도: %s - %s", title, message)
                    send_notification(title=title, message=message)
                    logger.info("알림 발송 완료: %s", title)
                except Exception:
                    logger.exception("알림 발송 중 오류 발생")

    def clear(self) -> None:
        """등록된 모든 알림을 제거한다."""
        self._alarms.clear()
        self._fired_today.clear()

    def get_next_run_info(self) -> str:
        """다음 알림까지 남은 시간 정보를 문자열로 반환."""
        if not self._alarms:
            return "예약된 알림 없음"

        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # 오늘 남은 알림 중 가장 가까운 것
        future = [a["time"] for a in self._alarms if a["time"] > current_time]
        if future:
            return f"다음 알림: {min(future)}"

        # 오늘 남은 게 없으면 내일 첫 알림
        all_times = sorted(a["time"] for a in self._alarms)
        return f"다음 알림: 내일 {all_times[0]}"
