"""알림 스케줄 관리 모듈"""

import logging
import threading
import time
import schedule

from core.notifier import send_notification

logger = logging.getLogger(__name__)


class AlarmScheduler:
    """설정된 알림 시간에 맞춰 Windows 알림을 발송하는 스케줄러."""

    def __init__(self):
        self._running = False
        self._thread: threading.Thread | None = None
        self._scheduler = schedule.Scheduler()
        self._lock = threading.Lock()

    def update_alarms(self, alarms: list[dict]) -> None:
        """알림 목록을 받아 스케줄을 재설정한다."""
        with self._lock:
            self._scheduler.clear()
            for alarm in alarms:
                if not alarm.get("enabled", False):
                    continue
                alarm_time = alarm["time"]  # "HH:MM"
                label = alarm.get("label", "Jobcan 알림")
                message = alarm.get("message", "Jobcan을 확인하세요!")

                self._scheduler.every().day.at(alarm_time).do(
                    self._safe_notify, title=label, message=message
                )
                logger.info("알림 등록: %s %s (%s)", label, alarm_time, message)

    def start(self) -> None:
        """백그라운드 스레드에서 스케줄러를 실행한다."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """스케줄러를 정지하고 기존 스레드 종료를 기다린다."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=3)
            self._thread = None
        with self._lock:
            self._scheduler.clear()

    @staticmethod
    def _safe_notify(title: str, message: str) -> None:
        """예외를 잡아서 스케줄러 스레드가 죽지 않도록 알림을 발송."""
        try:
            logger.info("알림 발송 시도: %s - %s", title, message)
            send_notification(title=title, message=message)
            logger.info("알림 발송 완료: %s", title)
        except Exception:
            logger.exception("알림 발송 중 오류 발생")

    def _run_loop(self) -> None:
        """1초 간격으로 스케줄을 확인하는 루프."""
        while self._running:
            try:
                with self._lock:
                    self._scheduler.run_pending()
            except Exception:
                logger.exception("스케줄러 run_pending 중 오류 발생")
            time.sleep(1)

    def get_next_run_info(self) -> str:
        """다음 알림까지 남은 시간 정보를 문자열로 반환."""
        jobs = self._scheduler.get_jobs()
        if not jobs:
            return "예약된 알림 없음"
        next_job = min(jobs, key=lambda j: j.next_run)
        return f"다음 알림: {next_job.next_run.strftime('%H:%M:%S')}"
