# pyRofex-To-Excel Project PowerShell Setup Script
# Provides convenient commands for common development tasks on Windows

param(
    [Parameter(Position=0)]
    [ValidateSet("help", "install", "install-dev", "check", "upgrade", "clean", "lint", "format", "type-check", "run", "config", "validate", "quality", "dev-setup")]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "pyRofex-To-Excel Project Commands" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Setup Commands:" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1 install     - Install package (editable) via pip"
    Write-Host "  .\setup.ps1 install-dev - Install package + dev extras from pyproject.toml"
    Write-Host "  .\setup.ps1 check       - Validate environment"
    Write-Host "  .\setup.ps1 upgrade     - Upgrade pip tooling + reinstall package"
    Write-Host "  .\setup.ps1 clean       - Remove .venv virtual environment"
    Write-Host ""
    Write-Host "Development Commands:" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1 lint        - Run linting (ruff)"
    Write-Host "  .\setup.ps1 format      - Format code (ruff)"
    Write-Host "  .\setup.ps1 type-check  - Run type checking (mypy)"
    Write-Host "  .\setup.ps1 run         - Run the main application"
    Write-Host ""
    Write-Host "Utility Commands:" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1 config      - Run quickstart validation"
    Write-Host "  .\setup.ps1 validate    - Validate system setup"
    Write-Host ""
    Write-Host "Example usage:" -ForegroundColor Green
    Write-Host "  .\setup.ps1 install-dev" -ForegroundColor Green
    Write-Host "  .\setup.ps1 run" -ForegroundColor Green
}

function Invoke-Command-Safe {
    param([string]$CommandToRun, [string]$Description)
    
    Write-Host "🔄 $Description" -ForegroundColor Blue
    Write-Host "   Running: $CommandToRun" -ForegroundColor Gray
    
    try {
        Invoke-Expression $CommandToRun
        if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null) {
            Write-Host "✅ $Description completed successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $Description failed with exit code $LASTEXITCODE" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ $Description failed: $_" -ForegroundColor Red
        return $false
    }
}

# Command implementations
switch ($Command) {
    "help" { Show-Help }
    
    "install" { 
        Invoke-Command-Safe "python -m pip install -e . --force-reinstall" "Installing package (editable)"
    }
    
    "install-dev" { 
        Invoke-Command-Safe "python -m pip install -e \".[dev]\" --force-reinstall" "Installing package + dev extras"
    }
    
    "check" { 
        Invoke-Command-Safe "python tools/validate_system.py" "Checking environment"
    }
    
    "upgrade" { 
        $pipUpgrade = Invoke-Command-Safe "python -m pip install --upgrade pip setuptools wheel" "Upgrading packaging toolchain"
        if ($pipUpgrade) {
            Invoke-Command-Safe "python -m pip install -e \".[dev]\" --upgrade --force-reinstall" "Upgrading project dependencies via pyproject"
        }
    }
    
    "clean" { 
        Write-Host "🧹 Removing .venv virtual environment (if present)..." -ForegroundColor Blue
        if (Test-Path ".venv") {
            try {
                Remove-Item -Recurse -Force ".venv"
                Write-Host "✅ .venv removed" -ForegroundColor Green
            } catch {
                Write-Host "❌ Failed to remove .venv: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "ℹ️ No .venv directory found" -ForegroundColor Yellow
        }
    }
    
    "lint" {
        Write-Host "🔍 Running linter..." -ForegroundColor Blue
        Invoke-Command-Safe "ruff check ." "Linting code"
    }
    
    "format" {
        Write-Host "🎨 Formatting code..." -ForegroundColor Blue
        Invoke-Command-Safe "ruff format ." "Formatting code"
    }
    
    "type-check" {
        Write-Host "🔍 Running type checker..." -ForegroundColor Blue
        Invoke-Command-Safe "mypy ." "Type checking"
    }
    
    "run" {
        Write-Host "🚀 Running pyRofex-To-Excel..." -ForegroundColor Blue
        Invoke-Command-Safe "python -m epgb_options" "Running application"
    }
    
    "config" {
        Write-Host "⚙️ Running quickstart validation..." -ForegroundColor Blue
        Invoke-Command-Safe "python tools/validate_quickstart.py" "Quickstart validation"
    }
    
    "validate" {
        Write-Host "✅ Validating system setup..." -ForegroundColor Blue
        Invoke-Command-Safe "python tools/validate_system.py" "System validation"
    }
    
    "quality" {
        Write-Host "🔍 Running quality checks..." -ForegroundColor Blue
        $lintResult = Invoke-Command-Safe "ruff check ." "Linting code"
        $typeResult = Invoke-Command-Safe "mypy ." "Type checking"
        
        if ($lintResult -and $typeResult) {
            Write-Host "✅ All quality checks passed" -ForegroundColor Green
        } else {
            Write-Host "❌ Some quality checks failed" -ForegroundColor Red
        }
    }
    
    "dev-setup" {
        Write-Host "🔧 Setting up development environment..." -ForegroundColor Blue
        $installResult = Invoke-Command-Safe "python -m pip install -e \".[dev]\" --force-reinstall" "Installing package + dev extras"
        $devDeps = $installResult
        
        if ($installResult -and $devDeps) {
            Write-Host "🔧 Setting up pre-commit hooks..." -ForegroundColor Blue
            try {
                pre-commit install
                Write-Host "✅ Pre-commit hooks installed" -ForegroundColor Green
            } catch {
                Write-Host "⚠️ pre-commit not available - install with: pip install pre-commit" -ForegroundColor Yellow
            }
            
            Write-Host "✅ Development setup complete" -ForegroundColor Green
        }
    }
    
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Show-Help
        exit 1
    }
}