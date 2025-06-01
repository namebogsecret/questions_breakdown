Param(
    [switch]$quiet,
    [switch]$noColor,
    [int]$port = 8000
)

$LogDir = "logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$LogFile = Join-Path $LogDir "run-$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log($level, $step, $message) {
    $ts = (Get-Date).ToString('yyyy-MM-dd HH:mm:sszzz')
    $line = "$ts [$level] $step – $message"
    if ($quiet -and $level -eq 'INFO') { return }
    if (-not $noColor) {
        switch ($level) {
            'INFO' { $color = 'Green' }
            'WARN' { $color = 'Yellow' }
            'ERROR' { $color = 'Red' }
            default { $color = 'White' }
        }
        Write-Host $line -ForegroundColor $color
    } else {
        Write-Host $line
    }
    Add-Content -Path $LogFile -Value $line
}

function Run-Cmd($step, $cmd) {
    Write-Log 'INFO' $step $cmd
    Invoke-Expression $cmd 2>&1 | Tee-Object -FilePath $LogFile -Append
    if ($LASTEXITCODE -ne 0) {
        Write-Log 'ERROR' $step "Exit code $LASTEXITCODE; see above for stderr"
        exit $LASTEXITCODE
    }
}

trap { Write-Log 'ERROR' 'main' 'Aborted (signal)'; exit 2 }

Run-Cmd 'git' 'git pull --ff-only'

if (Test-Path 'requirements.txt') {
    Run-Cmd 'deps' 'python -m pip install -r requirements.txt'
} elseif (Test-Path 'package.json') {
    Run-Cmd 'deps' 'npm ci --ignore-scripts'
} else {
    Write-Log 'INFO' 'deps' 'no dependency files'
}

$started = $false
if (Test-Path 'start.sh') {
    Run-Cmd 'start' 'bash start.sh'; $started = $true
} elseif (Test-Path 'package.json' -and (Get-Content package.json | Select-String '"start"')) {
    Run-Cmd 'start' 'npm start'; $started = $true
} elseif (Test-Path 'main.py') {
    Run-Cmd 'start' 'python main.py'; $started = $true
} elseif (Test-Path 'index.html') {
    $busy = @(Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue)
    if ($busy) {
        Write-Log 'WARN' 'start' "port $port busy; attempting to free"
        foreach ($b in $busy) { Stop-Process -Id $b.OwningProcess -Force }
    }
    Run-Cmd 'start' "python -m http.server $port"; $started = $true
} else {
    Write-Log 'ERROR' 'start' 'No start command found'
    exit 1
}

if ($started) {
    Write-Log 'INFO' 'main' '✓ SUCCESS'
} else {
    Write-Log 'ERROR' 'main' '✗ FAILED'
    exit 1
}
