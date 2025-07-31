# rust-wasm/build.ps1
$CrateDir = Get-Location
$CrateName = "wasm_analytics"
$Target = "bundler"
$OutputDir = "pkg"

Write-Host "Building WebAssembly module for $CrateName with target $Target..."

# Check wasm-pack version
if (-not (Get-Command wasm-pack -ErrorAction SilentlyContinue)) {
    Write-Host "Installing wasm-pack..."
    cargo install wasm-pack --force
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install wasm-pack."
        exit 1
    }
}
Write-Host "wasm-pack version: $(wasm-pack --version)"

# Clean previous build artifacts with retry
Write-Host "Cleaning previous build artifacts..."
$maxRetries = 5  # Increased retries
$retryCount = 0
$cleanSuccess = $false

while (-not $cleanSuccess -and $retryCount -lt $maxRetries) {
    try {
        # Terminate potential locking processes
        Stop-Process -Name "rustc" -Force -ErrorAction SilentlyContinue
        Stop-Process -Name "cargo" -Force -ErrorAction SilentlyContinue
        Stop-Process -Name "wasm-pack" -Force -ErrorAction SilentlyContinue

        if (Test-Path $OutputDir) {
            Remove-Item -Path $OutputDir -Recurse -Force -ErrorAction Stop
        }
        if (Test-Path "target") {
            Remove-Item -Path "target" -Recurse -Force -ErrorAction Stop
        }
        cargo clean
        $cleanSuccess = $true
    } catch {
        $retryCount++
        Write-Host "Clean attempt $retryCount failed: $_"
        Start-Sleep -Seconds 3  # Increased delay
    }
}

if (-not $cleanSuccess) {
    Write-Host "Error: Failed to clean artifacts after $maxRetries attempts."
    Write-Host "Try running as Administrator or rebooting."
    exit 1
}

# Run wasm-pack build with verbose output
Write-Host "Running wasm-pack build --target $Target..."
wasm-pack build --target $Target --out-dir $OutputDir --out-name $CrateName --release --verbose

# Check if the build was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful! Output files are in $CrateDir\$OutputDir"
} else {
    Write-Host "Error: Build failed. Check the error messages above."
    exit 1
}

# Verify init export
Write-Host "Checking for init export in wasm_analytics.js..."
$JsFile = Join-Path -Path $OutputDir -ChildPath "wasm_analytics.js"
if (Test-Path $JsFile) {
    $JsContent = Get-Content -Path $JsFile -Raw
    if ($JsContent -match "export\s+async\s+function\s+init") {
        Write-Host "Found init export in wasm_analytics.js"
    } else {
        Write-Host "Error: init export not found in wasm_analytics.js"
        Write-Host "First 100 lines of wasm_analytics.js:"
        Get-Content -Path $JsFile -TotalCount 100
    }
} else {
    Write-Host "Error: wasm_analytics.js not found in $OutputDir"
}

# Verify wasm_analytics.d.ts
Write-Host "Checking for init export in wasm_analytics.d.ts..."
$TsFile = Join-Path -Path $OutputDir -ChildPath "wasm_analytics.d.ts"
if (Test-Path $TsFile) {
    if (Select-String -Path $TsFile -Pattern "export function init") {
        Write-Host "Found init export in wasm_analytics.d.ts"
    } else {
        Write-Host "Error: init export not found in wasm_analytics.d.ts"
        Get-Content -Path $TsFile
    }
} else {
    Write-Host "Error: wasm_analytics.d.ts not found in $OutputDir"
}

# List generated files
Write-Host "Generated files:"
Get-ChildItem -Path $OutputDir | Format-Table -AutoSize