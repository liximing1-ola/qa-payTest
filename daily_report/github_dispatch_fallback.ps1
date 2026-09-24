# Daily-report fallback dispatcher (local timer, runs via Windows Task Scheduler).
# Purpose: when GitHub's own `schedule` does not fire the daily reports, this
#          local timer pokes GitHub Actions over REST API (workflow_dispatch).
#          Whether a report is really sent is decided by the idempotent `check`
#          job inside each workflow, so this script can NEVER cause duplicates:
#          it only fires a dispatch when no run succeeded yet "today" (Beijing).
# Task:    DailyReport_FallbackDispatch -- daily at 10:50, 11:10, 11:40, 12:10,
#          12:40, 13:10, 13:40, 14:10, 14:40, 15:10, 15:40 (machine local time).
#          Register from PowerShell (non-admin). Launched via wscript.exe +
#          run_fallback.vbs (window style 0) so the PowerShell console window
#          never flashes on screen at trigger points:
#            $a = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument '"D:\qa-payTest\daily_report\run_fallback.vbs"'
#            $t = '10:50','11:10','11:40','12:10','12:40','13:10','13:40','14:10','14:40','15:10','15:40' |
#                 ForEach-Object { New-ScheduledTaskTrigger -Daily -At $_ }
#            Register-ScheduledTask -TaskName 'DailyReport_FallbackDispatch' -Action $a -Trigger $t -Force
# Auth:    reads the GCM-cached GitHub token via `git credential fill`
#          (never printed, never written to disk).
# Log:     daily_report/fallback_dispatch.log
# Alerts:  on hard failure sends ONE WeCom alert per day (webhook from .env).
# Harmony: NOT dispatched before 12:05 local time -- AGC refreshes yesterday's
#          download-report columns late in the morning (columns appear one by
#          one), so the HarmonyOS report is held until data is ready. The iOS
#          (ASC) report keeps the early schedule. The workflow itself also
#          checks readiness and force-sends after 15:00 as last resort.
# NOTE: keep this file ASCII-only: PowerShell 5.1 in task context would
#       misread non-ASCII source text (no UTF-8 BOM guaranteed).

$ErrorActionPreference = 'Stop'
$repo = 'liximing1-ola/qa-payTest'
$base = "https://api.github.com/repos/$repo"
$logFile = Join-Path $PSScriptRoot 'fallback_dispatch.log'
$alertMarker = Join-Path $env:TEMP ('daily_report_fallback_alert_' + (Get-Date -Format 'yyyyMMdd') + '.txt')

function Write-Log([string]$msg) {
    $line = ('{0}  {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

function Send-Alert([string]$msg) {
    try {
        if (Test-Path $alertMarker) { return }   # at most one alert per day
        $envFile = Join-Path $PSScriptRoot '.env'
        if (-not (Test-Path $envFile)) { return }
        $m = Select-String -Path $envFile -Pattern '^WECOM_WEBHOOK=(\S+)' | Select-Object -First 1
        if (-not $m) { return }
        $wh = $m.Matches[0].Groups[1].Value
        $body = @{ msgtype = 'text'; text = @{ content = $msg } } | ConvertTo-Json -Depth 4
        Invoke-RestMethod -Method Post -Uri $wh -ContentType 'application/json' -Body $body | Out-Null
        Set-Content -Path $alertMarker -Value 'sent' -Encoding UTF8
    } catch { }
}

try {
    $env:GIT_TERMINAL_PROMPT = '0'
    $env:GCM_INTERACTIVE = 'Never'
    $cred = "protocol=https`nhost=github.com`n`n" | git credential fill 2>$null
    $token = (($cred | Select-String '^password=').Line) -replace '^password=', ''
    if (-not $token) { throw 'git credential fill returned no cached GitHub token' }
    $headers = @{ Authorization = "Bearer $token"; Accept = 'application/vnd.github+json'; 'User-Agent' = 'daily-report-fallback' }

    # UTC instant of "today 00:00" Beijing (= machine local time here)
    $bjNow = [DateTime]::UtcNow.AddHours(8)
    $cut = $bjNow.Date.AddHours(-8)
    # Earliest local minute-of-day to dispatch each workflow (12:05 = 725):
    # HarmonyOS AGC report columns are not ready in the morning.
    $earliest = @{ 'asc_daily.yml' = 0; 'harmony_daily.yml' = 725 }

    foreach ($wf in @('asc_daily.yml', 'harmony_daily.yml')) {
        if (($bjNow.Hour * 60 + $bjNow.Minute) -lt $earliest[$wf]) {
            Write-Log ('HOLD     {0}: before 12:05, waiting for AGC data readiness' -f $wf)
            continue
        }
        $runs = Invoke-RestMethod -Headers $headers -Uri "$base/actions/workflows/$wf/runs?per_page=20"
        $active = @($runs.workflow_runs | Where-Object {
            $raw = $_.created_at
            if ($raw -is [DateTime]) { $t = $raw.ToUniversalTime() } else { $t = [DateTimeOffset]::Parse([string]$raw).UtcDateTime }
            ($t -ge $cut) -and ($_.conclusion -eq 'success' -or $_.status -in @('queued', 'in_progress', 'pending', 'waiting', 'requested'))
        })
        if ($active.Count -gt 0) {
            Write-Log ('SKIP     {0}: already success/queued/in_progress today ({1} run(s))' -f $wf, $active.Count)
        } else {
            Invoke-RestMethod -Method Post -Headers $headers -ContentType 'application/json' -Body '{"ref":"main"}' -Uri "$base/actions/workflows/$wf/dispatches" | Out-Null
            Write-Log ('DISPATCH {0}: no success today, workflow_dispatch sent' -f $wf)
        }
    }
    exit 0
} catch {
    Write-Log ('ERROR    ' + $_.Exception.Message)
    Send-Alert ('[Daily report fallback] GitHub dispatch failed: ' + $_.Exception.Message)
    exit 1
}
