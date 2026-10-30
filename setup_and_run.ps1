# TensorFlow may emit diagnostics on stderr even when the import is caught.
# Keep native stderr non-terminating and check each native command's exit code.
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot

$neuralPython = Join-Path $PSScriptRoot ".venv-deepface\Scripts\python.exe"
$fallbackPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
$appPython = $null

# Prefer the supported neural runtime so Victim Search can compare real
# DeepFace embeddings. Keep the lightweight install available when Python 3.12
# is not installed on a machine.
$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
$hasPython312 = $false
if ($pythonLauncher) {
    & py -3.12 -c "import sys; assert sys.version_info[:2] == (3, 12)" 2>$null
    $hasPython312 = ($LASTEXITCODE -eq 0)
}

if ($hasPython312) {
    if (-not (Test-Path -LiteralPath $neuralPython)) {
        Write-Host "Creating the Python 3.12 DeepFace environment..."
        & py -3.12 -m venv (Join-Path $PSScriptRoot ".venv-deepface")
        if ($LASTEXITCODE -ne 0) { throw "Could not create the Python 3.12 environment." }
    }

    $appPython = $neuralPython
    $runtimeError = & $appPython -c "import deepface_adapter as a; print(a.DEEPFACE_IMPORT_ERROR or '')" 2>$null
    $runtimeErrorText = ($runtimeError -join " ").Trim()
    $blockedByApplicationControl = $runtimeErrorText -match "Application Control policy has blocked"
    if ($LASTEXITCODE -ne 0 -or ($runtimeErrorText -and -not $blockedByApplicationControl)) {
        Write-Host "Installing DeepFace, TensorFlow, and the app dependencies..."
        & $appPython -m pip install --upgrade pip
        if ($LASTEXITCODE -ne 0) { throw "Could not upgrade pip in the DeepFace environment." }
        & $appPython -m pip install -r (Join-Path $PSScriptRoot "requirements-deepface.txt")
        if ($LASTEXITCODE -ne 0) { throw "DeepFace installation failed. Check the network and requirements-deepface.txt." }
    }

    $runtimeError = & $appPython -c "import deepface_adapter as a; print(a.DEEPFACE_IMPORT_ERROR or '')" 2>$null
    $runtimeErrorText = ($runtimeError -join " ").Trim()
    if ($LASTEXITCODE -ne 0 -or $runtimeErrorText) {
        & $appPython -c "import streamlit, cv2, pandas"
        if ($LASTEXITCODE -ne 0) {
            throw "The app dependencies are incomplete. Install requirements-deepface.txt, then restart."
        }
        Write-Warning "DeepFace could not load: $runtimeErrorText. N-ONE will start in face-detection fallback mode; identity matching stays disabled."
    } else {
        Write-Host "Full DeepFace identity matching is available."
    }
} else {
    Write-Warning "Python 3.12 is unavailable. Starting the OpenCV fallback; victim identity matching requires the DeepFace runtime."
    if (-not (Test-Path -LiteralPath $fallbackPython)) {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCommand) { throw "Install Python 3.12 for Victim Search, or Python 3.10+ for fallback mode." }
        & python -m venv (Join-Path $PSScriptRoot "venv")
        if ($LASTEXITCODE -ne 0) { throw "Could not create the fallback environment." }
    }
    $appPython = $fallbackPython
    & $appPython -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "Could not install the fallback requirements." }
}

Write-Host "Starting N-ONE..."
& $appPython -m streamlit run (Join-Path $PSScriptRoot "app.py")
exit $LASTEXITCODE
