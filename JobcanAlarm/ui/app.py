"""메인 윈도우 UI"""

import logging
import sys
import os
import threading
import customtkinter as ctk

from core.notifier import open_jobcan
from core.settings import load_settings, save_settings
from core.scheduler import AlarmScheduler
from ui.widgets import AlarmRow

logger = logging.getLogger(__name__)

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


def _create_tray_icon_image():
    """pystray용 트레이 아이콘 이미지를 생성한다."""
    from PIL import Image, ImageDraw

    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # 파란 원 배경
    draw.ellipse([4, 4, size - 4, size - 4], fill="#1E90FF")
    # 흰색 J 글자
    draw.text((22, 12), "J", fill="white")
    return img


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
        self.scheduler = AlarmScheduler(on_alarm=self._show_alarm_popup)
        self.alarm_rows: list[AlarmRow] = []
        self._tray_icon = None
        self._quitting = False

        self._build_ui()
        self._apply_alarms()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # 시스템 트레이 아이콘 시작
        self._start_tray_icon()

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

    # ── 시스템 트레이 ──

    def _start_tray_icon(self):
        """시스템 트레이 아이콘을 백그라운드 스레드에서 시작."""
        try:
            import pystray
        except ImportError:
            logger.warning("pystray 없음, 트레이 아이콘 비활성화")
            return

        image = _create_tray_icon_image()
        menu = pystray.Menu(
            pystray.MenuItem("설정 열기", self._tray_show_window, default=True),
            pystray.MenuItem("Jobcan 열기", lambda: open_jobcan()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("종료", self._tray_quit),
        )
        self._tray_icon = pystray.Icon("JobcanAlarm", image, "JobcanAlarm", menu)
        tray_thread = threading.Thread(target=self._tray_icon.run, daemon=True)
        tray_thread.start()

    def _tray_show_window(self):
        """트레이에서 설정 창을 다시 표시."""
        self.after(0, self._show_window)

    def _show_window(self):
        """창을 복원하여 표시."""
        self.deiconify()
        self.lift()
        self.focus_force()

    def _tray_quit(self):
        """트레이 메뉴에서 완전 종료."""
        self._quitting = True
        if self._tray_icon:
            self._tray_icon.stop()
        self.after(0, self._quit_app)

    def _quit_app(self):
        """앱 완전 종료."""
        self.scheduler.clear()
        self.destroy()

    # ── 알림 관련 ──

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
        self._show_alarm_popup("JobcanAlarm 테스트", "알림이 정상적으로 작동합니다!")

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
        # 저장 메시지가 표시 중이면 유지
        if "저장" not in current_text:
            self.status_bar.configure(text=info)
        self.after(1000, self._update_status)

    def _show_alarm_popup(self, title: str, message: str):
        """화면 정가운데에 큼직한 알림 팝업을 띄운다."""
        popup = ctk.CTkToplevel(self)
        popup.title("JobcanAlarm")
        popup.attributes("-topmost", True)
        popup.resizable(False, False)
        popup.configure(fg_color="#1a1a2e")

        # 팝업 크기
        pw, ph = 460, 280

        # 화면 정가운데 좌표 계산
        screen_w = popup.winfo_screenwidth()
        screen_h = popup.winfo_screenheight()
        x = (screen_w - pw) // 2
        y = (screen_h - ph) // 2
        popup.geometry(f"{pw}x{ph}+{x}+{y}")

        # 내용
        ctk.CTkLabel(
            popup, text=title,
            font=("", 24, "bold"), text_color="#FF6B35",
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            popup, text=message,
            font=("", 16), text_color="white", wraplength=400,
        ).pack(pady=(0, 20))

        # 버튼 행
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=(10, 20))

        ctk.CTkButton(
            btn_frame, text="Jobcan 열기",
            command=lambda: [open_jobcan(), popup.destroy()],
            width=150, height=40,
            fg_color="#FF6B35", hover_color="#E55A2B",
            font=("", 15, "bold"),
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="닫기",
            command=popup.destroy,
            width=120, height=40,
            fg_color="gray40", hover_color="gray50",
            font=("", 15),
        ).pack(side="left", padx=10)

        # 30초 후 자동 닫기
        popup.after(30000, lambda: popup.destroy() if popup.winfo_exists() else None)

        # 포커스
        popup.lift()
        popup.focus_force()

    def _on_close(self):
        """창 닫기 → 트레이로 최소화 (트레이 없으면 종료)."""
        if self._tray_icon and not self._quitting:
            self.withdraw()
        else:
            self.scheduler.clear()
            self.destroy()
