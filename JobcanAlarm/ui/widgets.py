"""알림 항목 위젯"""

import customtkinter as ctk


class AlarmRow(ctk.CTkFrame):
    """하나의 알림(출근/퇴근 등)을 표시·편집하는 행 위젯."""

    def __init__(self, master, alarm_data: dict, on_change=None, **kwargs):
        super().__init__(master, **kwargs)
        self.alarm_data = alarm_data
        self.on_change = on_change

        self.configure(fg_color="transparent")
        self.columnconfigure(1, weight=1)

        # 라벨
        self.label = ctk.CTkLabel(
            self, text=alarm_data["label"], font=("", 14, "bold"), width=100, anchor="w"
        )
        self.label.grid(row=0, column=0, padx=(10, 5), pady=8, sticky="w")

        # 시간 입력
        time_frame = ctk.CTkFrame(self, fg_color="transparent")
        time_frame.grid(row=0, column=1, padx=5, pady=8)

        hour, minute = alarm_data["time"].split(":")
        self.hour_var = ctk.StringVar(value=hour)
        self.minute_var = ctk.StringVar(value=minute)

        self.hour_menu = ctk.CTkOptionMenu(
            time_frame,
            values=[f"{h:02d}" for h in range(24)],
            variable=self.hour_var,
            width=70,
            command=lambda _: self._on_time_change(),
        )
        self.hour_menu.pack(side="left", padx=2)

        ctk.CTkLabel(time_frame, text=":", font=("", 16)).pack(side="left")

        self.minute_menu = ctk.CTkOptionMenu(
            time_frame,
            values=[f"{m:02d}" for m in range(0, 60, 5)],
            variable=self.minute_var,
            width=70,
            command=lambda _: self._on_time_change(),
        )
        self.minute_menu.pack(side="left", padx=2)

        # ON/OFF 스위치
        self.enabled_var = ctk.BooleanVar(value=alarm_data.get("enabled", True))
        self.switch = ctk.CTkSwitch(
            self,
            text="",
            variable=self.enabled_var,
            onvalue=True,
            offvalue=False,
            command=self._on_toggle,
            width=50,
        )
        self.switch.grid(row=0, column=2, padx=(5, 10), pady=8)

        # 상태 라벨
        self.status_label = ctk.CTkLabel(
            self,
            text="ON" if self.enabled_var.get() else "OFF",
            font=("", 12),
            width=30,
        )
        self.status_label.grid(row=0, column=3, padx=(0, 10), pady=8)

        # 메시지 입력
        self.message_entry = ctk.CTkEntry(
            self, placeholder_text="알림 메시지", width=350
        )
        self.message_entry.grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 8), sticky="ew")
        self.message_entry.insert(0, alarm_data.get("message", ""))
        self.message_entry.bind("<FocusOut>", lambda _: self._on_message_change())

    def _on_time_change(self):
        self.alarm_data["time"] = f"{self.hour_var.get()}:{self.minute_var.get()}"
        if self.on_change:
            self.on_change()

    def _on_toggle(self):
        self.alarm_data["enabled"] = self.enabled_var.get()
        self.status_label.configure(text="ON" if self.enabled_var.get() else "OFF")
        if self.on_change:
            self.on_change()

    def _on_message_change(self):
        self.alarm_data["message"] = self.message_entry.get()
        if self.on_change:
            self.on_change()

    def get_data(self) -> dict:
        """현재 위젯의 알림 데이터를 반환."""
        return {
            "id": self.alarm_data["id"],
            "label": self.alarm_data["label"],
            "time": f"{self.hour_var.get()}:{self.minute_var.get()}",
            "message": self.message_entry.get(),
            "enabled": self.enabled_var.get(),
        }
