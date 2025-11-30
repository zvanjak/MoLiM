<#
.SYNOPSIS
    Configure PowerShell to run scripts from anywhere on the system.

.DESCRIPTION
    This script:
    1. Sets the execution policy to RemoteSigned
    2. Optionally adds script directories to PATH
    3. Verifies the configuration

.PARAMETER AddToPath
    If specified, adds the scripts directory to the system PATH

.EXAMPLE
    .\Enable-PowerShellScripts.ps1
    
.EXAMPLE
    .\Enable-PowerShellScripts.ps1 -AddToPath
#>

[CmdletBinding()]
param(
    [switch]$AddToPath
)

Write-Host "=== PowerShell Script Enablement Tool ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check current execution policy
Write-Host "1. Checking current execution policy..." -ForegroundColor Yellow
$currentPolicy = Get-ExecutionPolicy
$policyList = Get-ExecutionPolicy -List
Write-Host "Current effective policy: $currentPolicy" -ForegroundColor White
Write-Host ""
$policyList | Format-Table -AutoSize
Write-Host ""

# Step 2: Set execution policy
Write-Host "2. Setting execution policy to RemoteSigned..." -ForegroundColor Yellow

try {
    # Try to set for LocalMachine (requires admin)
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine -Force -ErrorAction Stop
    Write-Host "✓ Execution policy set to RemoteSigned for LocalMachine (all users)" -ForegroundColor Green
}
catch {
    Write-Host "⚠ Cannot set LocalMachine policy (requires Administrator)" -ForegroundColor Yellow
    Write-Host "  Attempting to set for CurrentUser instead..." -ForegroundColor Yellow
    
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force -ErrorAction Stop
        Write-Host "✓ Execution policy set to RemoteSigned for CurrentUser" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to set execution policy: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 3: Verify the change
Write-Host "3. Verifying new execution policy..." -ForegroundColor Yellow
$newPolicy = Get-ExecutionPolicy
$newPolicyList = Get-ExecutionPolicy -List
Write-Host "New effective policy: $newPolicy" -ForegroundColor White
Write-Host ""
$newPolicyList | Format-Table -AutoSize
Write-Host ""

# Step 4: Add scripts directory to PATH (optional)
if ($AddToPath) {
    Write-Host "4. Adding scripts directory to PATH..." -ForegroundColor Yellow
    
    $scriptsPath = Join-Path $PSScriptRoot ".."
    $scriptsPath = (Resolve-Path $scriptsPath).Path
    
    # Get current PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    if ($currentPath -notlike "*$scriptsPath*") {
        try {
            # Add to user PATH
            $newPath = "$currentPath;$scriptsPath"
            [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
            Write-Host "✓ Added '$scriptsPath' to user PATH" -ForegroundColor Green
            Write-Host "  Note: Restart your terminal for PATH changes to take effect" -ForegroundColor Cyan
        }
        catch {
            Write-Host "✗ Failed to add to PATH: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "✓ Scripts directory already in PATH" -ForegroundColor Green
    }
    Write-Host ""
}

# Step 5: Show execution policy details
Write-Host "=== Execution Policy Explained ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "RemoteSigned Policy:" -ForegroundColor White
Write-Host "  • Local scripts can run without a signature" -ForegroundColor Gray
Write-Host "  • Downloaded scripts must be signed by a trusted publisher" -ForegroundColor Gray
Write-Host "  • Use 'Unblock-File' to run downloaded unsigned scripts" -ForegroundColor Gray
Write-Host ""

# Step 6: Create a test script
Write-Host "5. Creating test script..." -ForegroundColor Yellow
$testScriptPath = Join-Path $PSScriptRoot "Test-ScriptExecution.ps1"
$testScriptContent = @'
Write-Host "✓ PowerShell scripts are working correctly!" -ForegroundColor Green
Write-Host "  Script executed from: $PSScriptRoot" -ForegroundColor Cyan
'@

try {
    Set-Content -Path $testScriptPath -Value $testScriptContent -Force
    Write-Host "✓ Test script created: $testScriptPath" -ForegroundColor Green
    Write-Host ""
    
    # Run the test script
    Write-Host "6. Testing script execution..." -ForegroundColor Yellow
    & $testScriptPath
    Write-Host ""
}
catch {
    Write-Host "✗ Failed to create or run test script: $_" -ForegroundColor Red
}

# Final summary
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "✓ PowerShell is now configured to run scripts" -ForegroundColor Green
Write-Host ""
Write-Host "To run scripts:" -ForegroundColor White
Write-Host "  • From same directory: .\script.ps1" -ForegroundColor Gray
Write-Host "  • From any directory: C:\path\to\script.ps1" -ForegroundColor Gray
if ($AddToPath) {
    Write-Host "  • If in PATH: script.ps1 (after restarting terminal)" -ForegroundColor Gray
}
Write-Host ""
Write-Host "If you download a script and get blocked:" -ForegroundColor White
Write-Host "  Unblock-File -Path .\downloaded-script.ps1" -ForegroundColor Gray
Write-Host ""

# Check for Group Policy conflicts
$machinePolicy = (Get-ExecutionPolicy -List | Where-Object { $_.Scope -eq "MachinePolicy" }).ExecutionPolicy
$userPolicy = (Get-ExecutionPolicy -List | Where-Object { $_.Scope -eq "UserPolicy" }).ExecutionPolicy

if ($machinePolicy -ne "Undefined" -or $userPolicy -ne "Undefined") {
    Write-Host "⚠ WARNING: Group Policy is setting execution policy" -ForegroundColor Yellow
    Write-Host "  MachinePolicy: $machinePolicy" -ForegroundColor Gray
    Write-Host "  UserPolicy: $userPolicy" -ForegroundColor Gray
    Write-Host "  Your setting may be overridden. Contact your system administrator." -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Configuration complete! 🎉" -ForegroundColor Green