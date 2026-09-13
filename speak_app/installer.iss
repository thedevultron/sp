; SPEAK v2.1 — Inno Setup 6 — Production One-Click — Amir Bagawan
; Compile with: python build.py --installer
;   or: iscc installer.iss  (Inno Setup 6.2+)
; One file out: installer\SPEAK_Setup_v2.1.exe — send it, receiver double-clicks, done.
; No admin required (PrivilegesRequired=lowest), free tier works with no key.

#define MyAppName "SPEAK"
#define MyAppVersion "2.1.0"
#define MyAppPublisher "Amir Bagawan"
#define MyAppURL "https://github.com/speak-ai"
#define MyAppExeName "SPEAK.exe"

[Setup]
AppId={{E4A8D19F-124B-4E38-9E28-84C8F0E23902}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppCopyright=Copyright (C) 2026 Amir Bagawan
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=SPEAK_Setup_v2.1
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=100,100
; No admin — safe for anyone to install
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible
CloseApplications=yes
RestartApplications=no
AllowNoIcons=yes
MinVersion=10.0
VersionInfoVersion={#MyAppVersion}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoCopyright=Copyright (C) 2026 Amir Bagawan
VersionInfoDescription=SPEAK - Voice dictation and AI companion (Amir Bagawan)
InfoBeforeFile=installer\README.txt
UninstallDisplayName=SPEAK (Amir Bagawan)
; Signing workaround - if signtool available, build.py signs before Inno
; SignTool=amir signtool sign /fd SHA256 /f cert.pfx /p $q$password$q$ $f
; SignedUninstaller=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Launch on Windows startup"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
Source: "dist\SPEAK.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer\README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\assets\icon.ico"
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\assets"

[Code]
function InitializeUninstall(): Boolean;
begin
  Result := True;
end;
