Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

[System.Windows.Forms.Application]::EnableVisualStyles()

$script:SRC_ROOT = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
if (-not $script:SRC_ROOT -or -not (Test-Path $script:SRC_ROOT)) {
    $script:SRC_ROOT = (Get-Location).Path
}

$script:DEFAULT_INSTALL = Join-Path $env:ProgramFiles "PERCEPTA Defence"
$script:USER_DATA_DIR = Join-Path $env:LOCALAPPDATA "PERCEPTA Defence"

# Main Form
$form = New-Object System.Windows.Forms.Form
$form.Text = "PERCEPTA Defence Setup"
$form.Size = New-Object System.Drawing.Size(620, 480)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.MinimizeBox = $true
$form.BackColor = [System.Drawing.Color]::FromArgb(11, 15, 25)
$form.ForeColor = [System.Drawing.Color]::FromArgb(243, 244, 246)

# Header Banner
$headerPanel = New-Object System.Windows.Forms.Panel
$headerPanel.Size = New-Object System.Drawing.Size(620, 70)
$headerPanel.Dock = "Top"
$headerPanel.BackColor = [System.Drawing.Color]::FromArgb(17, 24, 39)
$form.Controls.Add($headerPanel)

$headerTitle = New-Object System.Windows.Forms.Label
$headerTitle.Text = "PERCEPTA DEFENCE SETUP"
$headerTitle.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$headerTitle.ForeColor = [System.Drawing.Color]::FromArgb(0, 229, 255)
$headerTitle.Location = New-Object System.Drawing.Point(24, 14)
$headerTitle.AutoSize = $true
$headerPanel.Controls.Add($headerTitle)

$headerSub = New-Object System.Windows.Forms.Label
$headerSub.Text = "Autonomous AI Border Surveillance Command & Control"
$headerSub.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$headerSub.ForeColor = [System.Drawing.Color]::FromArgb(156, 163, 175)
$headerSub.Location = New-Object System.Drawing.Point(24, 38)
$headerSub.AutoSize = $true
$headerPanel.Controls.Add($headerSub)

# Footer Panel
$footerPanel = New-Object System.Windows.Forms.Panel
$footerPanel.Size = New-Object System.Drawing.Size(620, 54)
$footerPanel.Dock = "Bottom"
$footerPanel.BackColor = [System.Drawing.Color]::FromArgb(17, 24, 39)
$form.Controls.Add($footerPanel)

$btnCancel = New-Object System.Windows.Forms.Button
$btnCancel.Text = "Cancel"
$btnCancel.Location = New-Object System.Drawing.Point(510, 12)
$btnCancel.Size = New-Object System.Drawing.Size(85, 30)
$btnCancel.BackColor = [System.Drawing.Color]::FromArgb(39, 39, 42)
$btnCancel.ForeColor = [System.Drawing.Color]::White
$btnCancel.FlatStyle = "Flat"
$btnCancel.Add_Click({ $form.Close() })
$footerPanel.Controls.Add($btnCancel)

$btnNext = New-Object System.Windows.Forms.Button
$btnNext.Text = "Next >"
$btnNext.Location = New-Object System.Drawing.Point(415, 12)
$btnNext.Size = New-Object System.Drawing.Size(85, 30)
$btnNext.BackColor = [System.Drawing.Color]::FromArgb(0, 229, 255)
$btnNext.ForeColor = [System.Drawing.Color]::Black
$btnNext.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
$btnNext.FlatStyle = "Flat"
$footerPanel.Controls.Add($btnNext)

$btnBack = New-Object System.Windows.Forms.Button
$btnBack.Text = "< Back"
$btnBack.Location = New-Object System.Drawing.Point(320, 12)
$btnBack.Size = New-Object System.Drawing.Size(85, 30)
$btnBack.BackColor = [System.Drawing.Color]::FromArgb(39, 39, 42)
$btnBack.ForeColor = [System.Drawing.Color]::White
$btnBack.FlatStyle = "Flat"
$btnBack.Enabled = $false
$footerPanel.Controls.Add($btnBack)

# Content Panel
$contentPanel = New-Object System.Windows.Forms.Panel
$contentPanel.Dock = "Fill"
$contentPanel.Padding = New-Object System.Windows.Forms.Padding(24)
$form.Controls.Add($contentPanel)

$script:CurrentStep = 1
$script:TargetDir = $script:DEFAULT_INSTALL
$script:CreateDesktop = $true
$script:CreateStartMenu = $true
$script:LaunchAfter = $true

function Show-Step {
    param([int]$Step)
    $script:CurrentStep = $Step
    $contentPanel.Controls.Clear()

    if ($Step -eq 1) {
        $btnBack.Enabled = $false
        $btnNext.Text = "Next >"
        $btnNext.BackColor = [System.Drawing.Color]::FromArgb(0, 229, 255)

        $lblTitle = New-Object System.Windows.Forms.Label
        $lblTitle.Text = "Welcome to the PERCEPTA Defence Setup Wizard"
        $lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Bold)
        $lblTitle.ForeColor = [System.Drawing.Color]::White
        $lblTitle.Location = New-Object System.Drawing.Point(24, 20)
        $lblTitle.Size = New-Object System.Drawing.Size(550, 30)
        $contentPanel.Controls.Add($lblTitle)

        $lblDesc = New-Object System.Windows.Forms.Label
        $lblDesc.Text = "This wizard will install PERCEPTA Defence on your computer.`n`nPERCEPTA provides autonomous AI border surveillance, real-time YOLOv8 intrusion detection, virtual tripwires, multi-spectral thermal/IR analysis, and cryptographic chain-of-custody evidence inspection.`n`nClick Next to continue, or Cancel to exit Setup."
        $lblDesc.Font = New-Object System.Drawing.Font("Segoe UI", 9)
        $lblDesc.ForeColor = [System.Drawing.Color]::FromArgb(156, 163, 175)
        $lblDesc.Location = New-Object System.Drawing.Point(24, 65)
        $lblDesc.Size = New-Object System.Drawing.Size(550, 180)
        $contentPanel.Controls.Add($lblDesc)
    }
    elseif ($Step -eq 2) {
        $btnBack.Enabled = $true
        $btnNext.Text = "I Agree >"

        $lblTitle = New-Object System.Windows.Forms.Label
        $lblTitle.Text = "End-User Tactical Clearance & License Terms"
        $lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
        $lblTitle.ForeColor = [System.Drawing.Color]::White
        $lblTitle.Location = New-Object System.Drawing.Point(24, 15)
        $lblTitle.Size = New-Object System.Drawing.Size(550, 25)
        $contentPanel.Controls.Add($lblTitle)

        $txtTerms = New-Object System.Windows.Forms.TextBox
        $txtTerms.Multiline = $true
        $txtTerms.ReadOnly = $true
        $txtTerms.ScrollBars = "Vertical"
        $txtTerms.Text = "PERCEPTA DEFENCE SOFTWARE LICENSE AGREEMENT`r`n-------------------------------------------`r`n1. PROPRIETARY DEFENCE DEPLOYMENT`r`nThis software is provided for authorized tactical operations, border control, and forensic surveillance monitoring.`r`n`r`n2. ISOLATED USER WORKSPACES`r`nEach operator identity is allocated an isolated sandbox under %LOCALAPPDATA%\PERCEPTA Defence.`r`nOperator logs, database records, and captured incident clips are strictly partitioned.`r`n`r`n3. FORENSIC EVIDENCE INTEGRITY`r`nIncident recordings and timeline clips utilize SHA-256 HMAC cryptographic signatures.`r`nTampering with evidence logs invalidates court admissibility."
        $txtTerms.Location = New-Object System.Drawing.Point(24, 45)
        $txtTerms.Size = New-Object System.Drawing.Size(550, 220)
        $txtTerms.BackColor = [System.Drawing.Color]::FromArgb(17, 24, 39)
        $txtTerms.ForeColor = [System.Drawing.Color]::FromArgb(243, 244, 246)
        $txtTerms.Font = New-Object System.Drawing.Font("Consolas", 8)
        $contentPanel.Controls.Add($txtTerms)
    }
    elseif ($Step -eq 3) {
        $btnBack.Enabled = $true
        $btnNext.Text = "Next >"

        $lblTitle = New-Object System.Windows.Forms.Label
        $lblTitle.Text = "Choose Installation Location"
        $lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
        $lblTitle.ForeColor = [System.Drawing.Color]::White
        $lblTitle.Location = New-Object System.Drawing.Point(24, 15)
        $lblTitle.Size = New-Object System.Drawing.Size(550, 25)
        $contentPanel.Controls.Add($lblTitle)

        $lblDesc = New-Object System.Windows.Forms.Label
        $lblDesc.Text = "Setup will install PERCEPTA Defence into the following folder.`nTo install into a different folder, click Browse."
        $lblDesc.Font = New-Object System.Drawing.Font("Segoe UI", 9)
        $lblDesc.ForeColor = [System.Drawing.Color]::FromArgb(156, 163, 175)
        $lblDesc.Location = New-Object System.Drawing.Point(24, 45)
        $lblDesc.Size = New-Object System.Drawing.Size(550, 40)
        $contentPanel.Controls.Add($lblDesc)

        $txtPath = New-Object System.Windows.Forms.TextBox
        $txtPath.Text = $script:TargetDir
        $txtPath.Location = New-Object System.Drawing.Point(24, 95)
        $txtPath.Size = New-Object System.Drawing.Size(445, 25)
        $txtPath.BackColor = [System.Drawing.Color]::FromArgb(31, 41, 55)
        $txtPath.ForeColor = [System.Drawing.Color]::White
        $contentPanel.Controls.Add($txtPath)

        $btnBrowse = New-Object System.Windows.Forms.Button
        $btnBrowse.Text = "Browse..."
        $btnBrowse.Location = New-Object System.Drawing.Point(480, 93)
        $btnBrowse.Size = New-Object System.Drawing.Size(95, 28)
        $btnBrowse.BackColor = [System.Drawing.Color]::FromArgb(55, 65, 81)
        $btnBrowse.ForeColor = [System.Drawing.Color]::White
        $btnBrowse.FlatStyle = "Flat"
        $btnBrowse.Add_Click({
            $dlg = New-Object System.Windows.Forms.FolderBrowserDialog
            $dlg.SelectedPath = $txtPath.Text
            if ($dlg.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
                $txtPath.Text = $dlg.SelectedPath
                $script:TargetDir = $dlg.SelectedPath
            }
        })
        $contentPanel.Controls.Add($btnBrowse)

        $lblNote = New-Object System.Windows.Forms.Label
        $lblNote.Text = "Evidence Protection Architecture:`nImmutable application binaries will reside in Program Files.`nUser databases, incident recordings, and forensic evidence will be isolated under:`n$script:USER_DATA_DIR"
        $lblNote.Font = New-Object System.Drawing.Font("Segoe UI", 8)
        $lblNote.ForeColor = [System.Drawing.Color]::FromArgb(0, 229, 255)
        $lblNote.Location = New-Object System.Drawing.Point(24, 150)
        $lblNote.Size = New-Object System.Drawing.Size(550, 90)
        $contentPanel.Controls.Add($lblNote)
    }
    elseif ($Step -eq 4) {
        $btnBack.Enabled = $true
        $btnNext.Text = "Install"

        $lblTitle = New-Object System.Windows.Forms.Label
        $lblTitle.Text = "Select Additional Shortcuts"
        $lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
        $lblTitle.ForeColor = [System.Drawing.Color]::White
        $lblTitle.Location = New-Object System.Drawing.Point(24, 15)
        $lblTitle.Size = New-Object System.Drawing.Size(550, 25)
        $contentPanel.Controls.Add($lblTitle)

        $chkDesk = New-Object System.Windows.Forms.CheckBox
        $chkDesk.Text = "Create Desktop Shortcut (PERCEPTA Defence)"
        $chkDesk.Checked = $script:CreateDesktop
        $chkDesk.Location = New-Object System.Drawing.Point(28, 55)
        $chkDesk.Size = New-Object System.Drawing.Size(500, 25)
        $chkDesk.Add_CheckedChanged({ $script:CreateDesktop = $chkDesk.Checked })
        $contentPanel.Controls.Add($chkDesk)

        $chkMenu = New-Object System.Windows.Forms.CheckBox
        $chkMenu.Text = "Create Start Menu Entry (PERCEPTA Defence)"
        $chkMenu.Checked = $script:CreateStartMenu
        $chkMenu.Location = New-Object System.Drawing.Point(28, 85)
        $chkMenu.Size = New-Object System.Drawing.Size(500, 25)
        $chkMenu.Add_CheckedChanged({ $script:CreateStartMenu = $chkMenu.Checked })
        $contentPanel.Controls.Add($chkMenu)
    }
    elseif ($Step -eq 5) {
        $btnBack.Enabled = $false
        $btnNext.Enabled = $false
        $btnCancel.Enabled = $false

        $lblTitle = New-Object System.Windows.Forms.Label
        $lblTitle.Text = "Installing PERCEPTA Defence..."
        $lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
        $lblTitle.ForeColor = [System.Drawing.Color]::White
        $lblTitle.Location = New-Object System.Drawing.Point(24, 20)
        $lblTitle.Size = New-Object System.Drawing.Size(550, 25)
        $contentPanel.Controls.Add($lblTitle)

        $script:lblProgress = New-Object System.Windows.Forms.Label
        $script:lblProgress.Text = "Preparing application binaries..."
        $script:lblProgress.ForeColor = [System.Drawing.Color]::FromArgb(156, 163, 175)
        $script:lblProgress.Location = New-Object System.Drawing.Point(24, 60)
        $script:lblProgress.Size = New-Object System.Drawing.Size(550, 20)
        $contentPanel.Controls.Add($script:lblProgress)

        $script:progBar = New-Object System.Windows.Forms.ProgressBar
        $script:progBar.Location = New-Object System.Drawing.Point(24, 85)
        $script:progBar.Size = New-Object System.Drawing.Size(550, 20)
        $contentPanel.Controls.Add($script:progBar)

        # Run installation in background
        $timer = New-Object System.Windows.Forms.Timer
        $timer.Interval = 200
        $stepCount = 0
        $timer.Add_Tick({
            $stepCount++
            if ($stepCount -eq 1) {
                $script:progBar.Value = 20
                $script:lblProgress.Text = "Copying neural weights (YOLOv8 & ByteTrack)..."
                Install-PerceptaFiles -Step 1
            }
            elseif ($stepCount -eq 3) {
                $script:progBar.Value = 50
                $script:lblProgress.Text = "Deploying C2 Command & Control UI (dist)..."
                Install-PerceptaFiles -Step 2
            }
            elseif ($stepCount -eq 5) {
                $script:progBar.Value = 80
                $script:lblProgress.Text = "Configuring Windows shortcuts & Add/Remove Programs..."
                Install-PerceptaFiles -Step 3
            }
            elseif ($stepCount -ge 7) {
                $timer.Stop()
                $script:progBar.Value = 100
                $script:lblProgress.Text = "Installation complete."
                Show-Step 6
            }
        })
        $timer.Start()
    }
    elseif ($Step -eq 6) {
        $btnBack.Visible = $false
        $btnCancel.Visible = $false
        $btnNext.Enabled = $true
        $btnNext.Text = "Finish"
        $btnNext.BackColor = [System.Drawing.Color]::FromArgb(16, 185, 129)
        $btnNext.Add_Click({
            if ($script:LaunchAfter) {
                $exePath = Join-Path $script:TargetDir "PERCEPTA.exe"
                if (Test-Path $exePath) {
                    Start-Process -FilePath $exePath -WorkingDirectory $script:TargetDir
                }
            }
            $form.Close()
        })

        $lblTitle = New-Object System.Windows.Forms.Label
        $lblTitle.Text = "Completing the PERCEPTA Defence Setup"
        $lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Bold)
        $lblTitle.ForeColor = [System.Drawing.Color]::FromArgb(16, 185, 129)
        $lblTitle.Location = New-Object System.Drawing.Point(24, 20)
        $lblTitle.Size = New-Object System.Drawing.Size(550, 30)
        $contentPanel.Controls.Add($lblTitle)

        $lblDesc = New-Object System.Windows.Forms.Label
        $lblDesc.Text = "PERCEPTA Defence has been installed successfully on your computer.`n`nApplication files: $script:TargetDir`nUser Sandboxes: $script:USER_DATA_DIR`n`nThe application can be launched from the Desktop or Windows Search."
        $lblDesc.Font = New-Object System.Drawing.Font("Segoe UI", 9)
        $lblDesc.ForeColor = [System.Drawing.Color]::FromArgb(156, 163, 175)
        $lblDesc.Location = New-Object System.Drawing.Point(24, 65)
        $lblDesc.Size = New-Object System.Drawing.Size(550, 100)
        $contentPanel.Controls.Add($lblDesc)

        $chkLaunch = New-Object System.Windows.Forms.CheckBox
        $chkLaunch.Text = "Launch PERCEPTA Defence"
        $chkLaunch.Checked = $script:LaunchAfter
        $chkLaunch.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
        $chkLaunch.Location = New-Object System.Drawing.Point(28, 175)
        $chkLaunch.Size = New-Object System.Drawing.Size(400, 25)
        $chkLaunch.Add_CheckedChanged({ $script:LaunchAfter = $chkLaunch.Checked })
        $contentPanel.Controls.Add($chkLaunch)
    }
}

function Install-PerceptaFiles {
    param([int]$Step)
    $target = $script:TargetDir
    if (-not (Test-Path $target)) {
        New-Item -ItemType Directory -Path $target -Force | Out-Null
    }

    if ($Step -eq 1) {
        # Models & Videos
        $resModels = Join-Path $target "resources\models"
        $resVideos = Join-Path $target "resources\videos"
        New-Item -ItemType Directory -Path $resModels -Force | Out-Null
        New-Item -ItemType Directory -Path $resVideos -Force | Out-Null

        $srcModel = Join-Path $script:SRC_ROOT "models\yolov8n.pt"
        if (Test-Path $srcModel) {
            Copy-Item -Path $srcModel -Destination (Join-Path $resModels "yolov8n.pt") -Force
            New-Item -ItemType Directory -Path (Join-Path $target "models") -Force | Out-Null
            Copy-Item -Path $srcModel -Destination (Join-Path $target "models\yolov8n.pt") -Force
        }

        $srcVideo = Join-Path $script:SRC_ROOT "storage\virat_cctv.mp4"
        if (-not (Test-Path $srcVideo)) {
            $srcVideo = Join-Path $script:SRC_ROOT "frontend\public\videos\virat_cctv.mp4"
        }
        if (Test-Path $srcVideo) {
            Copy-Item -Path $srcVideo -Destination (Join-Path $resVideos "virat_cctv.mp4") -Force
        }
    }
    elseif ($Step -eq 2) {
        # Copy UI dist
        $srcDist = Join-Path $script:SRC_ROOT "frontend\dist"
        if (-not (Test-Path $srcDist)) {
            $srcDist = Join-Path $script:SRC_ROOT "offline\frontend\dist"
        }
        if (Test-Path $srcDist) {
            $dstDist = Join-Path $target "resources\dist"
            Copy-Item -Path $srcDist -Destination $dstDist -Recurse -Force
        }

        # Copy backend, offline, and config
        foreach ($folder in @("backend", "offline", "config")) {
            $sf = Join-Path $script:SRC_ROOT $folder
            if (Test-Path $sf) {
                Copy-Item -Path $sf -Destination (Join-Path $target $folder) -Recurse -Force
            }
        }

        # Copy executable
        $srcExe = Join-Path $script:SRC_ROOT "dist\PERCEPTA.exe"
        $dstExe = Join-Path $target "PERCEPTA.exe"
        if (Test-Path $srcExe) {
            Copy-Item -Path $srcExe -Destination $dstExe -Force
        } else {
            # Fallback launcher wrapper
            $launchBat = Join-Path $target "PERCEPTA.bat"
            Set-Content -Path $launchBat -Value "@echo off`r`nstart python offline\desktop\launcher.py"
        }
    }
    elseif ($Step -eq 3) {
        $exeTarget = Join-Path $target "PERCEPTA.exe"
        if (-not (Test-Path $exeTarget)) {
            $exeTarget = Join-Path $target "PERCEPTA.bat"
        }

        # Windows Shortcuts
        $WshShell = New-Object -ComObject WScript.Shell
        if ($script:CreateDesktop) {
            $deskLnk = Join-Path ([Environment]::GetFolderPath("Desktop")) "PERCEPTA Defence.lnk"
            $sc = $WshShell.CreateShortcut($deskLnk)
            $sc.TargetPath = $exeTarget
            $sc.WorkingDirectory = $target
            $sc.Description = "PERCEPTA Defence Command & Control"
            $sc.Save()
        }
        if ($script:CreateStartMenu) {
            $menuDir = [Environment]::GetFolderPath("Programs")
            $menuLnk = Join-Path $menuDir "PERCEPTA Defence.lnk"
            $sc = $WshShell.CreateShortcut($menuLnk)
            $sc.TargetPath = $exeTarget
            $sc.WorkingDirectory = $target
            $sc.Description = "PERCEPTA Defence Command & Control"
            $sc.Save()
        }

        # Write Uninstaller
        $uninstallerPath = Join-Path $target "uninstall.bat"
        $uninstContent = @"
@echo off
echo ====================================================
echo          PERCEPTA DEFENCE UNINSTALL WIZARD
echo ====================================================
echo.
echo Removing PERCEPTA Defence from your computer...
echo.
echo EVIDENCE PRESERVATION NOTICE:
echo Your local incident evidence and forensic database at:
echo   $script:USER_DATA_DIR
echo are safely PRESERVED by default.
echo.
set /p REMOVE_DATA="Do you also want to remove your user data and evidence? (Y/N, default N): "
del "%USERPROFILE%\Desktop\PERCEPTA Defence.lnk" 2>nul
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\PERCEPTA Defence.lnk" 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\PERCEPTA Defence" /f 2>nul
if /i "%REMOVE_DATA%"=="Y" (
    rmdir /S /Q "$script:USER_DATA_DIR" 2>nul
)
echo.
echo PERCEPTA Defence has been removed successfully.
pause
"@
        Set-Content -Path $uninstallerPath -Value $uninstContent

        # Add/Remove Programs Registry Entry
        $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\PERCEPTA Defence"
        New-Item -Path $regPath -Force | Out-Null
        Set-ItemProperty -Path $regPath -Name "DisplayName" -Value "PERCEPTA Defence"
        Set-ItemProperty -Path $regPath -Name "DisplayVersion" -Value "1.0.0"
        Set-ItemProperty -Path $regPath -Name "Publisher" -Value "PERCEPTA Defence Systems"
        Set-ItemProperty -Path $regPath -Name "InstallLocation" -Value $target
        Set-ItemProperty -Path $regPath -Name "UninstallString" -Value "`"$uninstallerPath`""
        Set-ItemProperty -Path $regPath -Name "NoModify" -Value 1
        Set-ItemProperty -Path $regPath -Name "NoRepair" -Value 1
    }
}

$btnNext.Add_Click({
    if ($script:CurrentStep -lt 4) {
        Show-Step ($script:CurrentStep + 1)
    }
    elseif ($script:CurrentStep -eq 4) {
        Show-Step 5
    }
})

$btnBack.Add_Click({
    if ($script:CurrentStep -gt 1) {
        Show-Step ($script:CurrentStep - 1)
    }
})

Show-Step 1
$form.ShowDialog() | Out-Null
