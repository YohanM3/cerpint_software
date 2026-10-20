$ErrorActionPreference = "Stop"

$securePassword = Read-Host "Contraseña de ferreteria_app" -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)

try {
    $env:FERRETERIA_DB_HOST = "localhost"
    $env:FERRETERIA_DB_PORT = "3307"
    $env:FERRETERIA_DB_NAME = "ferreteria_cerpint"
    $env:FERRETERIA_DB_USER = "ferreteria_app"
    $env:FERRETERIA_DB_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    & "$PSScriptRoot\.venv\Scripts\python.exe" "$PSScriptRoot\main.py"
}
finally {
    Remove-Item Env:FERRETERIA_DB_PASSWORD -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
}