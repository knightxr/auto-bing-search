[Setup]
AppId={{8FBB3B13-8E5E-4E93-B0B9-9A3A9D6D9B21}}
AppName=Auto Bing Search
AppVersion=1.2.1
DefaultDirName={userpf}\Auto Bing Search
DefaultGroupName=Auto Bing Search
PrivilegesRequired=lowest
OutputBaseFilename=AutoBingSearch-Setup
OutputDir=C:\Users\jacqu\OneDrive\Documents\GitHub\auto-bing-search\Auto Bing Search\dist_win
Compression=lzma2
SolidCompression=yes
SetupIconFile=C:\Users\jacqu\OneDrive\Documents\GitHub\auto-bing-search\Auto Bing Search\assets\app.ico
WizardImageFile=C:\Users\jacqu\OneDrive\Documents\GitHub\auto-bing-search\Auto Bing Search\dist_win\branding\wizard.bmp
WizardSmallImageFile=C:\Users\jacqu\OneDrive\Documents\GitHub\auto-bing-search\Auto Bing Search\dist_win\branding\wizard-small.bmp
UninstallDisplayIcon={app}\Auto Bing Search.exe
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "C:\Users\jacqu\OneDrive\Documents\GitHub\auto-bing-search\Auto Bing Search\dist_win\Auto Bing Search\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Auto Bing Search"; Filename: "{app}\Auto Bing Search.exe"; IconFilename: "{app}\Auto Bing Search.exe"
Name: "{userdesktop}\Auto Bing Search"; Filename: "{app}\Auto Bing Search.exe"; IconFilename: "{app}\Auto Bing Search.exe"

[Run]
Filename: "{app}\Auto Bing Search.exe"; Description: "Launch Auto Bing Search"; Flags: nowait postinstall skipifsilent
