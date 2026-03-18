"""메인 윈도우 UI"""

import sys
import os
import customtkinter as ctk

from core.notifier import open_jobcan
from core.settings import load_settings, save_settings
from core.scheduler import AlarmScheduler
from ui.widgets import AlarmRow

STARTUP_REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_APP_NAME = "JobcanAlarm"


def _get_exe_path() -> str:
    """현재 실행 중인 exe 경로를 반환."""
    if getattr(sys, "frozen", False):
        return sys.executable
    return os.path.abspath(sys.argv[0])


def _is_autostart_enabled() -> bool:
    """레지스트리에 자동 실행이 등록되어 있는지 확인."""
    if sys.platform != "win32":
        return False
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REGISTRY_KEY, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, STARTUP_APP_NAME)
        winreg.CloseKey(key)
        return True
    except (FileNotFoundError, OSError):
        return False


def _set_autostart(enable: bool) -> None:
    """레지스트리에 자동 실행을 등록/해제."""
    if sys.platform != "win32":
        return
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REGISTRY_KEY, 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, STARTUP_APP_NAME, 0, winreg.REG_SZ, f'"{_get_exe_path()}"')
        else:
            try:
                winreg.DeleteValue(key, STARTUP_APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except OSError:
        pass


class JobcanAlarmApp(ctk.CTk):
    """JobcanAlarm 메인 윈도우."""

    def __init__(self):
        super().__init__()

        self.title("JobcanAlarm - 근태 알림")
        self.geometry("520x520")
        self.minsize(480, 460)
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

        # Jobcan 열기 버튼 (헤더 오른쪽)
        self.jobcan_btn = ctk.CTkButton(
            header,
            text="Jobcan 열기",
            command=open_jobcan,
            width=100,
            height=30,
            fg_color="#FF6B35",
            hover_color="#E55A2B",
            font=("", 13),
        )
        self.jobcan_btn.pack(side="right")

        # 구분선
        ctk.CTkFrame(self, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=5)

        # 알림 항목들 (스크롤 가능)
        self.alarms_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.alarms_frame.pack(fill="both", expand=True, padx=20, pady=5)

        for alarm_data in self.settings["alarms"]:
            row = AlarmRow(
                self.alarms_frame,
                alarm_data,
                on_change=self._on_alarm_changed,
                on_delete=self._delete_alarm,
            )
            row.pack(fill="x", pady=5)
            self.alarm_rows.append(row)

        # 구분선
        ctk.CTkFrame(self, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=(5, 0))

        # 하단 영역
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=20, pady=(8, 5))

        # 버튼 행
        btn_row = ctk.CTkFrame(bottom, fg_color="transparent")
        btn_row.pack(fill="x")

        self.save_btn = ctk.CTkButton(
            btn_row, text="저장 및 적용", command=self._save_and_apply,
            height=34, font=("", 13),
        )
        self.save_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.test_btn = ctk.CTkButton(
            btn_row,
            text="테스트 알림",
            command=self._test_notification,
            height=34,
            fg_color="gray40",
            hover_color="gray50",
            font=("", 13),
        )
        self.test_btn.pack(side="left", fill="x", expand=True, padx=4)

        self.add_btn = ctk.CTkButton(
            btn_row,
            text="+ 알림 추가",
            command=self._add_alarm,
            height=34,
            fg_color="#2FA572",
            hover_color="#1E8C5E",
            font=("", 13),
        )
        self.add_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # 옵션 행 (윈도우 시작 시 자동 실행 토글)
        option_row = ctk.CTkFrame(bottom, fg_color="transparent")
        option_row.pack(fill="x", pady=(8, 0))

        self.autostart_var = ctk.BooleanVar(value=_is_autostart_enabled())
        self.autostart_switch = ctk.CTkSwitch(
            option_row,
            text="윈도우 시작 시 자동 실행",
            variable=self.autostart_var,
            onvalue=True,
            offvalue=False,
            command=self._on_autostart_toggle,
            font=("", 12),
        )
        self.autostart_switch.pack(side="left")

        # 상태바
        self.status_bar = ctk.CTkLabel(
            self, text="", font=("", 11), text_color="gray", anchor="w"
        )
        self.status_bar.pack(fill="x", padx=20, pady=(2, 10))

    def _on_autostart_toggle(self):
        """윈도우 시작 시 자동 실행 토글."""
        _set_autostart(self.autostart_var.get())

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
        """스케줄러에 현재 알림 설정을 반영."""
        self.scheduler.clear()
        self.scheduler.update_alarms(self.settings["alarms"])

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
            self.alarms_frame, new_alarm,
            on_change=self._on_alarm_changed,
            on_delete=self._delete_alarm,
        )
        row.pack(fill="x", pady=5)
        self.alarm_rows.append(row)
        self._save_and_apply()

    def _delete_alarm(self, row: AlarmRow):
        """알림 항목을 삭제."""
        if row in self.alarm_rows:
            self.alarm_rows.remove(row)
            row.destroy()
            self._save_and_apply()

    def _update_status(self):
        """1초마다 스케줄을 확인하고 상태바를 갱신."""
        self.scheduler.tick()
        info = self.scheduler.get_next_run_info()
        current_text = self.status_bar.cget("text")
        # 저장 메시지가 표시 중이면 3초 후 원래로 복귀
        if "저장" not in current_text:
            self.status_bar.configure(text=info)
        self.after(1000, self._update_status)

    def _on_close(self):
        """앱 종료 시 스케줄러 정리."""
        self.scheduler.clear()
        self.destroy()
