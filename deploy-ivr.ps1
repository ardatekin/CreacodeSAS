param(
    [switch]$all,
    [switch]$help,
    [int]$Step,
    [string]$InstallDir = "C:\CreacodeSAS",
    [string]$PgInstaller = ".\postgresql-17.6-1-windows-x64.exe",
    [string]$PgInstallerUrl = "https://get.enterprisedb.com/postgresql/postgresql-17.6-1-windows-x64.exe",
    [string]$OdbcMsi = ".\psqlodbc_x64.msi",
    [string]$VcRedist = ".\VC_redist.x64.exe",
    [string]$DsnName = "creacodesas_pg_local",
    [string]$DbName = "creacodesas",
    [string]$DbUser = "postgres",
    [string]$DbPassword = "postgres",
    [string]$DbRestoreFile = ".\creacodesas_postgres_backup.sql",
    [switch]$Debug,

    # --- Voice prerequisites global variables ---
    [string]$PythonUrl = "https://www.python.org/ftp/python/3.13.7/python-3.13.7-amd64.exe",
    [string]$PythonDir = "C:\Python313",
    [string]$FfmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
    [string]$FfmpegDir = "C:\ffmpeg-8.0",
    [string]$VoiceGenScript = ".\Voice\GenerateVoiceFiles\generate_all_voice.py"
)

# --- Help output ---
if ($help) {
    Write-Host "Creacode SIP Application Server deployment script usage" -ForegroundColor Cyan
    Write-Host "  .\deploy-ivr.ps1 -all        # Run all 12 steps"
    Write-Host "  .\deploy-ivr.ps1 -Step N     # Run a specific step (1..12)"
    Write-Host "  .\deploy-ivr.ps1 -help       # Show this help message"
    Write-Host ""
    Write-Host "Steps:" -ForegroundColor Yellow
    Write-Host "  1. VC++ Redistributable"
    Write-Host "  2. Telnet Client"
    Write-Host "  3. Folder structure"
    Write-Host "  4. Copy Bin contents"
    Write-Host "  5. Copy resource directories"
    Write-Host "  6. PostgreSQL install"
    Write-Host "  7. ODBC driver install"
    Write-Host "  8. Create DSN"
    Write-Host "  9. Restore database"
    Write-Host " 10. Voice generation prerequisites (Python, gTTS, pydub, ffmpeg)"
    Write-Host " 11. Generate voice files"
    Write-Host " 12. Patch ini + Compile scripts + Service install/start + Firewall rule"
    exit
}

# --- Utility functions ---
function Ensure-Dir($path) {
    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null }
}

function Get-ActiveIPv4 {
    Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -notlike "169.*" -and $_.IPAddress -ne "127.0.0.1" } |
        Sort-Object -Property PrefixLength |
        Select-Object -First 1 -ExpandProperty IPAddress
}

function Get-ValidPostgresDriver {
    $base = "HKLM:\SOFTWARE\ODBC\ODBCINST.INI"
    $driversKey = "$base\ODBC Drivers"
    $valid = @()

    if (Test-Path $driversKey) {
        $drivers = Get-ItemProperty $driversKey
        foreach ($d in $drivers.PSObject.Properties) {
            if ($d.Name -like "PostgreSQL*") {
                $driverKey = Join-Path $base $d.Name
                try {
                    $dll = (Get-ItemProperty $driverKey).Driver
                    if ($dll -and (Test-Path $dll)) {
                        $valid += $d.Name
                    }
                } catch {}
            }
        }
    }
    return $valid
}

Write-Host "== Creacode SIP Application Server Deployment ==" -ForegroundColor Cyan

# --- Step implementations ---

function Run-Step1 {
    if (Test-Path $VcRedist) {
        Write-Host "Installing VC++ Redistributable..." -ForegroundColor Yellow
        Start-Process (Resolve-Path $VcRedist).Path -ArgumentList "/quiet","/norestart" -Wait
    }
}

function Run-Step2 {
    Write-Host "Ensuring Telnet Client is installed..." -ForegroundColor Yellow
    Start-Process (Get-Command dism.exe).Source -ArgumentList "/online","/Enable-Feature","/FeatureName:TelnetClient","/All","/NoRestart" -Wait -NoNewWindow
}

function Run-Step3 {
    Write-Host "Creating folder structure..." -ForegroundColor Yellow
    foreach ($f in "Bin","LOG","RadiusDictionary","Record","Scripts","Voice") { Ensure-Dir (Join-Path $InstallDir $f) }
}

function Run-Step4 {
    $binDir = Join-Path $InstallDir "Bin"
    Ensure-Dir $binDir
    if (Test-Path ".\Bin") {
        Write-Host "Copying Bin directory contents..." -ForegroundColor Yellow
        Copy-Item ".\Bin\*" $binDir -Recurse -Force
    }
}

function Run-Step5 {
    foreach ($dir in "Voice","Scripts","Record","RadiusDictionary","LOG") {
        if (Test-Path ".\$dir") {
            Write-Host "Copying $dir..." -ForegroundColor Yellow
            Copy-Item ".\$dir\*" (Join-Path $InstallDir $dir) -Recurse -Force
        }
    }
}

function Run-Step6 {
    if (-not (Test-Path $PgInstaller)) {
        Write-Host "Downloading PostgreSQL installer..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $PgInstallerUrl -OutFile $PgInstaller
    }
    if (Test-Path $PgInstaller) {
        Write-Host "Launching PostgreSQL installer GUI..." -ForegroundColor Yellow
        Start-Process (Resolve-Path $PgInstaller).Path -Wait
    }
}

function Run-Step7 {
    if (Test-Path $OdbcMsi) {
        Write-Host "Installing PostgreSQL ODBC driver..." -ForegroundColor Yellow
        Start-Process msiexec.exe -ArgumentList "/i `"$((Resolve-Path $OdbcMsi).Path)`" /qn /norestart ALLUSERS=1 /L*v `"$env:TEMP\psqlodbc_install.log`"" -Wait -NoNewWindow
    }
}

function Run-Step8 {
    Write-Host "Creating System DSN $DsnName..." -ForegroundColor Yellow
    $validDrivers = Get-ValidPostgresDriver
    if ($validDrivers.Count -gt 0) {
        $driver = $validDrivers | Where-Object { $_ -like "*Unicode(x64)*" } | Select-Object -First 1
        if (-not $driver) { $driver = $validDrivers[0] }
        Write-Host "Using ODBC driver: $driver" -ForegroundColor Green
        $dsn = "DSN=$DsnName|Server=localhost|Database=$DbName|UID=$DbUser|PWD=$DbPassword|Port=5432"
        cmd.exe /c "odbcconf.exe /A {CONFIGSYSDSN `"$driver`" `"$dsn`"}"
    }
}

function Run-Step9 {
    if (Test-Path $DbRestoreFile) {
        Write-Host "Restoring database..." -ForegroundColor Yellow
        $psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
        if (Test-Path $psql) {
            $env:PGPASSWORD = $DbPassword
            $confirm = Read-Host "Drop and recreate database '$DbName'? This will ERASE all existing data. Type Y to confirm"
            if ($confirm -eq "Y" -or $confirm -eq "y") {
                if ($DbName -eq "postgres") {
                    Write-Host "Cannot drop 'postgres'. Resetting schema 'public' instead..." -ForegroundColor Yellow
                    & $psql -U $DbUser -d $DbName -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
                } else {
                    Write-Host "Dropping and recreating database $DbName..." -ForegroundColor Yellow
                    & $psql -U $DbUser -d postgres -c "DROP DATABASE IF EXISTS $DbName;"
                    & $psql -U $DbUser -d postgres -c "CREATE DATABASE $DbName OWNER $DbUser;"
                }
            }
            & $psql -U $DbUser -d $DbName -f $DbRestoreFile
        }
    }
}

function Run-Step10 {
    Write-Host "Installing prerequisites for IVR voice file generation..." -ForegroundColor Cyan

    # --- Python ---
    $pythonExe = Join-Path $PythonDir "python.exe"
    if (-not (Test-Path $pythonExe)) {
        Write-Host "Downloading and installing Python..." -ForegroundColor Yellow
        $installer = "$env:TEMP\python-installer.exe"
        Invoke-WebRequest -Uri $PythonUrl -OutFile $installer
        Start-Process $installer -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 TargetDir=$PythonDir" -Wait
    }

    # Detect Python if installed elsewhere (fallback to Program Files)
    if (-not (Test-Path $pythonExe)) {
        $altPath = "C:\Program Files\Python313\python.exe"
        if (Test-Path $altPath) {
            $pythonExe = $altPath
            Write-Host "Detected Python at $pythonExe" -ForegroundColor Yellow
        }
    }

    if (Test-Path $pythonExe) {
        & $pythonExe -m pip install --upgrade pip
        & $pythonExe -m pip install gTTS pydub
    } else {
        Write-Host "ERROR: Python installation failed or not found." -ForegroundColor Red
    }

    foreach ($p in @("$PythonDir\", "$PythonDir\Scripts\")) {
        $envPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
        if ($envPath -notlike "*$p*") {
            Write-Host "Adding $p to PATH" -ForegroundColor Yellow
            setx /M PATH ($envPath + ";" + $p) | Out-Null
        }
    }

    # --- FFmpeg ---
    $ffmpegExe = Join-Path $FfmpegDir "bin\ffmpeg.exe"
    if (-not (Test-Path $ffmpegExe)) {
        Write-Host "Downloading and installing FFmpeg..." -ForegroundColor Yellow
        $zip = "$env:TEMP\ffmpeg.zip"
        Invoke-WebRequest -Uri $FfmpegUrl -OutFile $zip
        Expand-Archive -Path $zip -DestinationPath "C:\"
        $extracted = Get-ChildItem "C:\ffmpeg-*" | Where-Object { $_.PSIsContainer } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($extracted) { Rename-Item $extracted.FullName $FfmpegDir -Force }
    } else {
        Write-Host "FFmpeg already installed at $ffmpegExe" -ForegroundColor Green
    }

    $ffPath = Join-Path $FfmpegDir "bin"
    $envPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($envPath -notlike "*$ffPath*") {
        Write-Host "Adding $ffPath to PATH" -ForegroundColor Yellow
        setx /M PATH ($envPath + ";" + $ffPath) | Out-Null
    }
}

function Run-Step11 {
    Write-Host "Generating IVR voice files..." -ForegroundColor Cyan

    $confirm = Read-Host "Voice file generation may take a long time. Do you want to continue? (Y/N)"
    if ($confirm -notin @("Y","y")) {
        Write-Host "Step 11 cancelled by user." -ForegroundColor Yellow
        return
    }

    $pythonExe = Join-Path $PythonDir "python.exe"
    if (-not (Test-Path $pythonExe)) {
        $altPath = "C:\Program Files\Python313\python.exe"
        if (Test-Path $altPath) { $pythonExe = $altPath }
    }
    if (-not (Test-Path $pythonExe)) {
        Write-Host "ERROR: Python not found. Please run Step 10 first." -ForegroundColor Red
        return
    }

    $ffmpegExe = Join-Path $FfmpegDir "bin\ffmpeg.exe"
    if (-not (Test-Path $ffmpegExe)) {
        Write-Host "ERROR: FFmpeg not found. Please run Step 10 first." -ForegroundColor Red
        return
    }

    try {
        & $pythonExe -c "import gtts, pydub" 2>$null
    } catch {
        Write-Host "ERROR: Required Python modules gTTS/pydub not available. Run Step 10 first." -ForegroundColor Red
        return
    }

    if (-not (Test-Path $VoiceGenScript)) {
        Write-Host "Voice generation script not found: $VoiceGenScript" -ForegroundColor Red
        return
    }

    Write-Host "Running $VoiceGenScript..." -ForegroundColor Yellow
    Push-Location (Split-Path $VoiceGenScript)
    & $pythonExe (Split-Path -Leaf $VoiceGenScript)
    Pop-Location

    $generatedDir = Join-Path (Split-Path $VoiceGenScript) "CreacodeSAS"
    $targetDir = Join-Path $InstallDir "Voice\CreacodeSAS"
    if (Test-Path $generatedDir) {
        if (Test-Path $targetDir) { Remove-Item $targetDir -Recurse -Force }
        Move-Item $generatedDir $targetDir
        Write-Host "Voice files moved to $targetDir" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Generated voice directory not found: $generatedDir" -ForegroundColor Red
    }
}

function Run-Step12 {
    $binDir = Join-Path $InstallDir "Bin"
    $iniPath = Join-Path $binDir "ivr.ini"
    $targetExe = Join-Path $binDir "CreacodeSAS.exe"

    if (Test-Path $iniPath) {
        $ipv4 = Get-ActiveIPv4
        Write-Host "Patching ivr.ini with LocalIP=$ipv4 and paths under $InstallDir" -ForegroundColor Yellow
        (Get-Content $iniPath) -replace 'LocalIP=.*', "LocalIP=$ipv4" -replace 'C:\\IVR', $InstallDir | Set-Content $iniPath -Encoding UTF8
    }

    if (Test-Path $iniPath) {
        $scriptPath = Select-String -Path $iniPath -Pattern '^ScriptPath=' | ForEach-Object { ($_ -split '=')[1].Trim() }
        if ($scriptPath -and (Test-Path $scriptPath)) {
            Write-Host "Compiling IVR script in $scriptPath ..." -ForegroundColor Yellow
            Push-Location $scriptPath
            $sccExe = Join-Path $binDir "SCC.exe"
            if (Test-Path $sccExe) { & $sccExe main.txt out.sc }
            Pop-Location
        }
    }

    $svcName = "Creacode SAS Service"
    $service = Get-Service -Name $svcName -ErrorAction SilentlyContinue
    if (-not $service) {
        Write-Host "Installing service via application self-install..." -ForegroundColor Yellow
        Start-Process $targetExe -ArgumentList "-install" -WorkingDirectory $binDir -Wait
        Start-Sleep -Seconds 2
        $service = Get-Service -Name $svcName -ErrorAction SilentlyContinue
    } else {
        Write-Host "Service '$svcName' already installed." -ForegroundColor Yellow
    }

    if ($service) {
        try {
            if ($service.Status -eq "Running") {
                Write-Host "Service '$svcName' is running. Restarting..." -ForegroundColor Yellow
                Restart-Service -Name $svcName -Force -ErrorAction Stop
            } else {
                Write-Host "Service '$svcName' is not running. Starting..." -ForegroundColor Yellow
                Start-Service -Name $svcName -ErrorAction Stop
            }
            $svc = Get-Service -Name $svcName
            Write-Host "Service state: $($svc.Status)" -ForegroundColor Green
        } catch {
            Write-Host "ERROR: could not start or restart service '$svcName'." -ForegroundColor Red
        }
    }

    $ruleName = "Creacode SIP Application Server"
    $fwRule = netsh advfirewall firewall show rule name="$ruleName" | Select-String "$ruleName"
    if (-not $fwRule) {
        Write-Host "Adding firewall rule '$ruleName'..." -ForegroundColor Yellow
        netsh advfirewall firewall add rule `
            name="$ruleName" `
            dir=in action=allow program="$targetExe" enable=yes profile=public protocol=UDP
    } else {
        Write-Host "Firewall rule '$ruleName' already exists. Skipping." -ForegroundColor Yellow
    }
}

# --- Dispatcher ---
if ($all) {
    Run-Step1; Run-Step2; Run-Step3; Run-Step4; Run-Step5;
    Run-Step6; Run-Step7; Run-Step8; Run-Step9; Run-Step10; Run-Step11; Run-Step12
}
elseif ($Step) {
    switch ($Step) {
        1  { Run-Step1 }
        2  { Run-Step2 }
        3  { Run-Step3 }
        4  { Run-Step4 }
        5  { Run-Step5 }
        6  { Run-Step6 }
        7  { Run-Step7 }
        8  { Run-Step8 }
        9  { Run-Step9 }
        10 { Run-Step10 }
        11 { Run-Step11 }
        12 { Run-Step12 }
        default { Write-Host "Invalid step. Use -help to see usage." -ForegroundColor Red }
    }
}
else {
    Write-Host "No argument specified. Use -help for usage." -ForegroundColor Yellow
}
