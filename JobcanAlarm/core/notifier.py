"""Windows 토스트 알림 모듈"""

import sys
import subprocess


def send_notification(title: str, message: str) -> None:
    """Windows 토스트 알림을 표시한다.

    winotify가 있으면 사용하고, 없으면 PowerShell 폴백.
    """
    try:
        from winotify import Notification, audio

        toast = Notification(
            app_id="JobcanAlarm",
            title=title,
            msg=message,
            duration="long",
        )
        toast.set_audio(audio.Default, loop=False)
        toast.show()
    except ImportError:
        _fallback_notification(title, message)


def _fallback_notification(title: str, message: str) -> None:
    """winotify 사용 불가 시 PowerShell로 알림 표시."""
    if sys.platform != "win32":
        print(f"[알림] {title}: {message}")
        return

    ps_script = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null

    $template = @"
    <toast>
        <visual>
            <binding template="ToastText02">
                <text id="1">{title}</text>
                <text id="2">{message}</text>
            </binding>
        </visual>
        <audio src="ms-winsoundevent:Notification.Default"/>
    </toast>
"@

    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("JobcanAlarm").Show($toast)
    """
    subprocess.Popen(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
