$ErrorActionPreference = "Stop"
$repo = "https://github.com/karthiklabs7/K-Programming.git"
$dest = Join-Path $env:LOCALAPPDATA "K-Programming"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "Git is required. Install Git for Windows, then rerun."
}
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
  throw "Python 3 is required. Install Python 3, then rerun."
}
if (Test-Path $dest) {
  throw "Install folder already exists: $dest. No files changed."
}
git clone --depth 1 $repo $dest
$launcher = Join-Path $dest "k.cmd"
@'
@echo off
set "ROOT=%LOCALAPPDATA%\K-Programming"
cd /d "%ROOT%" || exit /b 1
if exist "%ROOT%\interpreter\k_1_0_dev.py" (
  py -3 "%ROOT%\interpreter\k_1_0_dev.py" %*
  exit /b %errorlevel%
)
if exist "%ROOT%\interpreter\k.py" (
  py -3 "%ROOT%\interpreter\k.py" %*
  exit /b %errorlevel%
)
echo K interpreter entry point not found.
exit /b 1
'@ | Set-Content -Encoding ASCII $launcher
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (($userPath -split ";") -notcontains $dest) {
  [Environment]::SetEnvironmentVariable("Path", (($userPath.TrimEnd(";") + ";" + $dest).TrimStart(";")), "User")
}
Write-Host "K installed. Open a new terminal and run: k examples/hello.k"
