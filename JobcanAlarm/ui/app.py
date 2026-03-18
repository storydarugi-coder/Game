"""메인 윈도우 UI"""

import customtkinter as ctk

from core.notifier import open_jobcan
from core.settings import load_settings, save_settings
from core.scheduler import AlarmScheduler
from ui.widgets import AlarmRow


class JobcanAlarmApp(ctk.CTk):
    """JobcanAlarm 메인 윈도우."""

    def __init__(self):
        super().__init__()

        self.title("JobcanAlarm - 근태 알림")
        self.geometry("500x480")
        self.minsize(450, 400)
        self.resizable(True, True)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.settings = load_settings()
        self.scheduler = AlarmScheduler()
        self.alarm_rows: list[AlarmRow] = []

        self._build_ui()
        self._apply_alarms()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # 상태바 업데이트 타이머
        self._update_status()

    def _build_ui(self):
        # 헤더
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header, text="JobcanAlarm", font=("", 22, "bold")
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="근태 알림 설정", font=("", 13), text_color="gray"
        ).pack(side="left", padx=10)

        # 구분선
        ctk.CTkFrame(self, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=5)

        # 알림 항목들
        self.alarms_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.alarms_frame.pack(fill="both", expand=True, padx=20, pady=5)

        for alarm_data in self.settings["alarms"]:
            row = AlarmRow(
                self.alarms_frame,
                alarm_data,
                on_change=self._on_alarm_changed,
            )
            row.pack(fill="x", pady=5)
            self.alarm_rows.append(row)

        # 하단 버튼 영역
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=20, pady=(5, 5))

        self.save_btn = ctk.CTkButton(
            bottom, text="저장 및 적용", command=self._save_and_apply, width=140
        )
        self.save_btn.pack(side="left", padx=5)

        self.test_btn = ctk.CTkButton(
            bottom,
            text="테스트 알림",
            command=self._test_notification,
            width=120,
            fg_color="gray40",
            hover_color="gray50",
        )
        self.test_btn.pack(side="left", padx=5)

        self.jobcan_btn = ctk.CTkButton(
            bottom,
            text="Jobcan 열기",
            command=open_jobcan,
            width=120,
            fg_color="#FF6B35",
            hover_color="#E55A2B",
        )
        self.jobcan_btn.pack(side="left", padx=5)

        self.add_btn = ctk.CTkButton(
            bottom,
            text="+ 알림 추가",
            command=self._add_alarm,
            width=120,
            fg_color="green",
            hover_color="darkgreen",
        )
        self.add_btn.pack(side="right", padx=5)

        # 상태바
        self.status_bar = ctk.CTkLabel(
            self, text="", font=("", 11), text_color="gray", anchor="w"
        )
        self.status_bar.pack(fill="x", padx=20, pady=(0, 10))

    def _on_alarm_changed(self):
        """알림 설정이 변경되면 자동 저장 및 적용."""
        self._save_and_apply()

    def _save_and_apply(self):
        """현재 UI 상태를 저장하고 스케줄러에 적용."""
        alarms = [row.get_data() for row in self.alarm_rows]
        self.settings["alarms"] = alarms
        save_settings(self.settings)
        self._apply_alarms()
        self.status_bar.configure(text="설정이 저장되었습니다.")

    def _apply_alarms(self):
        """스케줄러에 현재 알림 설정을 반영하고 시작."""
        self.scheduler.stop()
        self.scheduler.update_alarms(self.settings["alarms"])
        self.scheduler.start()

    def _test_notification(self):
        """테스트 알림 발송."""
        from core.notifier import send_notification

        send_notification("JobcanAlarm 테스트", "알림이 정상적으로 작동합니다!")

    def _add_alarm(self):
        """새 알림 항목을 추가."""
        new_alarm = {
            "id": f"custom_{len(self.alarm_rows) + 1}",
            "label": f"알림 {len(self.alarm_rows) + 1}",
            "time": "12:00",
            "message": "Jobcan을 확인하세요!",
            "enabled": True,
        }
        row = AlarmRow(
            self.alarms_frame, new_alarm, on_change=self._on_alarm_changed
        )
        row.pack(fill="x", pady=5)
        self.alarm_rows.append(row)
        self._save_and_apply()

    def _update_status(self):
        """1초마다 상태바의 다음 알림 정보를 갱신."""
        info = self.scheduler.get_next_run_info()
        current_text = self.status_bar.cget("text")
        # 저장 메시지가 표시 중이면 3초 후 원래로 복귀
        if "저장" not in current_text:
            self.status_bar.configure(text=info)
        self.after(1000, self._update_status)

    def _on_close(self):
        """앱 종료 시 스케줄러 정리."""
        self.scheduler.stop()
        self.destroy()
