#!/usr/bin/env pwsh
<#
.SYNOPSIS
    動態生成 Release Notes
    
.DESCRIPTION
    從 version_config.json 和 CHANGELOG.md 讀取資訊，生成 Release Notes
    
.PARAMETER Version
    版本號，預設使用 version_config.json 中的版本
    
.PARAMETER OutputPath
    輸出文件路徑，預設為 RELEASE_NOTES_v{VERSION}.md
    
.EXAMPLE
    .\scripts\generate_release_notes.ps1
    # 生成當前版本的 Release Notes
    
.EXAMPLE
    .\scripts\generate_release_notes.ps1 -Version 1.8.5
    # 生成指定版本的 Release Notes
#>

param(
    [Parameter()]
    [string]$Version,
    
    [Parameter()]
    [string]$OutputPath,
    
    [Parameter()]
    [string]$ConfigPath = "scripts/version_config.json"
)

$ErrorActionPreference = "Stop"

# 讀取配置
if (-not (Test-Path $ConfigPath)) {
    Write-Host "找不到配置文件: $ConfigPath" -ForegroundColor Red
    exit 1
}

$config = Get-Content $ConfigPath -Raw | ConvertFrom-Json

if (-not $Version) {
    $Version = $config.version.current
}

if (-not $OutputPath) {
    $OutputPath = "RELEASE_NOTES_v$Version.md"
}

Write-Host "生成 Release Notes: $Version" -ForegroundColor Cyan

# 生成 Release Notes 內容
$releaseNotes = @"
## 🚀 Release $Version

### 📦 Installation

**PyPI (Python Package):**
``````bash
pip install --upgrade fubon-api-mcp-server==$Version
``````

**VS Code Extension:**
- **Extension ID**: ``$($config.extension.id)``
- Search for "Fubon API MCP Server" in VS Code Extensions (Publisher: **$($config.publisher.name)**)
- Or visit: $($config.urls.marketplace)
- Or download the ``.vsix`` file below and install manually

### 📝 Changelog

> 請手動補充此版本的變更內容

### 🔗 Links
- **VS Code Extension**: $($config.urls.marketplace)
- **PyPI**: $($config.urls.pypi)$Version/
- **Documentation**: $($config.urls.documentation)
- **Issues**: $($config.urls.issues)
- **富邦 API**: $($config.urls.fubon_api)

---

**Full Changelog**: $($config.urls.repository)/compare/v$Version...HEAD
"@

# 寫入文件
Set-Content -Path $OutputPath -Value $releaseNotes

Write-Host "✓ Release Notes 已生成: $OutputPath" -ForegroundColor Green
Write-Host ""
Write-Host "請編輯文件並補充變更內容，然後用於 GitHub Release" -ForegroundColor Yellow
