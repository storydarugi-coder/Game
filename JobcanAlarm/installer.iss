; Inno Setup Script for JobcanAlarm
; 빌드 방법:
; 1. 먼저 pyinstaller build.spec 로 exe 빌드
; 2. Inno Setup 설치 (https://jrsoftware.org/isinfo.php)
; 3. 이 파일을 Inno Setup으로 열고 컴파일

[Setup]
AppName=JobcanAlarm
AppVersion=1.0.0
AppPublisher=JobcanAlarm
DefaultDirName={autopf}\JobcanAlarm
DefaultGroupName=JobcanAlarm
OutputDir=installer_output
OutputBaseFilename=JobcanAlarm_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayName=JobcanAlarm
; 아이콘이 있으면 아래 주석 해제
; SetupIconFile=assets\icon.ico

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Files]
Source: "dist\JobcanAlarm.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\JobcanAlarm"; Filename: "{app}\JobcanAlarm.exe"
Name: "{group}\JobcanAlarm 제거"; Filename: "{uninstallexe}"
Name: "{autodesktop}\JobcanAlarm"; Filename: "{app}\JobcanAlarm.exe"; Tasks: desktopicon
Name: "{userstartup}\JobcanAlarm"; Filename: "{app}\JobcanAlarm.exe"; Tasks: startupicon

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 바로가기 만들기"; GroupDescription: "추가 옵션:"
Name: "startupicon"; Description: "윈도우 시작 시 자동 실행"; GroupDescription: "추가 옵션:"; Flags: unchecked

[Run]
Filename: "{app}\JobcanAlarm.exe"; Description: "JobcanAlarm 실행"; Flags: nowait postinstall skipifsilent
