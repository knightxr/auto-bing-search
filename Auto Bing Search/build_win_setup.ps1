$ErrorActionPreference = "Stop"
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

$Version = Read-Host "Enter version (e.g., 1.2.3)"
if (-not $Version) { throw "Version is required." }

python -m pip install --upgrade pip wheel
python -m pip install -r requirements.txt
python -m pip install pyinstaller

$spec = Get-ChildItem -File -Filter "*win*.spec" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $spec) { $spec = Get-ChildItem -File -Filter "*.spec" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 }
$specPath = if ($spec) { $spec.FullName } else { "auto_bing_search.py" }

Remove-Item -Recurse -Force dist_win, build_win -ErrorAction SilentlyContinue
python -m PyInstaller -y --clean --distpath dist_win --workpath build_win "$specPath"

$distRoot = (Resolve-Path "dist_win").Path
$appDir = (Get-ChildItem -Path $distRoot -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1)
if (-not $appDir) { throw "No build output found in dist_win." }
$exe = Get-ChildItem -Path $appDir.FullName -Filter "*.exe" -File -Recurse | Select-Object -First 1
if (-not $exe) { throw "No .exe found under $($appDir.FullName)." }
$exeName = $exe.Name

Add-Type -AssemblyName System.Drawing
function Load-ImageAbs([string]$p){$abs=(Resolve-Path $p).Path;$fs=[System.IO.File]::OpenRead($abs);try{[System.Drawing.Image]::FromStream($fs)}finally{$fs.Close()}}
function Save-BmpSafe([System.Drawing.Image]$img,[string]$out,[int]$w,[int]$h){$dir=Split-Path -Parent $out;if(-not(Test-Path $dir)){New-Item -ItemType Directory -Force -Path $dir|Out-Null}if(Test-Path $out){[System.IO.File]::SetAttributes($out,[System.IO.FileAttributes]::Normal);Remove-Item $out -Force}$bmp=New-Object System.Drawing.Bitmap($w,$h);$g=[System.Drawing.Graphics]::FromImage($bmp);$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::HighQuality;$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;$g.PixelOffsetMode=[System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality;$g.Clear([System.Drawing.Color]::White);$g.DrawImage($img,0,0,$w,$h)|Out-Null;$ms=New-Object System.IO.MemoryStream;$bmp.Save($ms,[System.Drawing.Imaging.ImageFormat]::Bmp);$g.Dispose();$bmp.Dispose();[System.IO.File]::WriteAllBytes($out,$ms.ToArray());$ms.Dispose()}

$pngPath = "assets\app.png"
$icoPath = "assets\app.ico"
if(Test-Path $pngPath){$img=Load-ImageAbs $pngPath}
elseif(Test-Path $icoPath){$icoAbsTmp=(Resolve-Path $icoPath).Path;$icoObj=New-Object System.Drawing.Icon($icoAbsTmp);$img=$icoObj.ToBitmap();$icoObj.Dispose()}
else{throw "Missing icon: assets\app.png or assets\app.ico"}

$brandDir = Join-Path $distRoot "branding"
$big = Join-Path $brandDir "wizard.bmp"
$small = Join-Path $brandDir "wizard-small.bmp"
Save-BmpSafe $img $big 164 314
Save-BmpSafe $img $small 55 58
$img.Dispose()

$icoAbs = if(Test-Path $icoPath){(Resolve-Path $icoPath).Path}else{$null}
$appName = "Auto Bing Search"

$iss = @"
[Setup]
AppId={{8FBB3B13-8E5E-4E93-B0B9-9A3A9D6D9B21}}
AppName=$appName
AppVersion=$Version
DefaultDirName={userpf}\$appName
DefaultGroupName=$appName
PrivilegesRequired=lowest
OutputBaseFilename=AutoBingSearch-Setup-$Version
OutputDir="$distRoot"
Compression=lzma2
SolidCompression=yes
WizardImageFile="$big"
WizardSmallImageFile="$small"
UninstallDisplayIcon={app}\$exeName
DisableProgramGroupPage=yes
"@
if ($icoAbs) { $iss += "SetupIconFile=`"$icoAbs`"`r`n" }
$iss += @"
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "$($appDir.FullName)\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\$appName"; Filename: "{app}\$exeName"; IconFilename: "{app}\$exeName"
Name: "{userdesktop}\$appName"; Filename: "{app}\$exeName"; IconFilename: "{app}\$exeName"

[Run]
Filename: "{app}\$exeName"; Description: "Launch $appName"; Flags: nowait postinstall skipifsilent
"@

Set-Content -Path "build_installer_$($Version).iss" -Value $iss -Encoding ASCII

$compiler=$null
$cmd=Get-Command iscc -ErrorAction SilentlyContinue
if($cmd){$compiler=$cmd.Source}
if(-not $compiler){
  $probe=Get-ChildItem -Path "C:\Program Files*", "C:\Users\*\AppData\Local\Programs" -Recurse -Include "ISCC.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
  if($probe){$compiler=$probe.FullName}
}
if(-not $compiler){throw "ISCC.exe not found"}

& "$compiler" "build_installer_$($Version).iss"

Write-Host "`nDone. Installer is in $distRoot (AutoBingSearch-Setup-$Version.exe)" -ForegroundColor Green