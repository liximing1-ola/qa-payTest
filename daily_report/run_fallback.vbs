' Daily-report fallback launcher: runs github_dispatch_fallback.ps1 fully
' hidden (wscript GUI host + window style 0), so the PowerShell console
' window never flashes at trigger points.
' bWaitOnReturn = False: wscript exits right away, PowerShell keeps running
' in the background; results are recorded in fallback_dispatch.log.
CreateObject("WScript.Shell").Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""D:\qa-payTest\daily_report\github_dispatch_fallback.ps1""", 0, False
