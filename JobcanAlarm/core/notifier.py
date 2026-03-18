"""Windows 토스트 알림 모듈"""

import logging
import sys
import subprocess
import webbrowser

logger = logging.getLogger(__name__)

JOBCAN_URL = "https://id.jobcan.jp/users/sign_in"


def open_jobcan():
    """Jobcan 로그인 페이지를 브라우저에서 연다."""
    webbrowser.open(JOBCAN_URL)


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
        toast.add_actions(label="Jobcan 열기", launch=JOBCAN_URL)
        toast.show()
        logger.info("winotify 알림 발송 성공: %s", title)
    except ImportError:
        logger.warning("winotify 없음, PowerShell 폴백 사용")
        _fallback_notification(title, message)
    except Exception:
        logger.exception("winotify 알림 발송 실패, PowerShell 폴백 사용")
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
