[CmdletBinding()]
param(
    [string]$Workspace = (Join-Path $env:USERPROFILE ".nanobot\workspace")
)

$sourcePackage = Join-Path $PSScriptRoot "ecommerce_multi_agent"
$sourceKnowledgeBase = Join-Path $sourcePackage "knowledge_base"
$sourceSkill = Join-Path $PSScriptRoot "skills\ecommerce-operations\SKILL.md"
$targetPackage = Join-Path $Workspace "ecommerce_multi_agent"
$targetSkillDirectory = Join-Path $Workspace "skills\ecommerce-operations"

if (-not (Test-Path -LiteralPath $sourcePackage)) {
    throw "Missing workflow package: $sourcePackage"
}

if (-not (Test-Path -LiteralPath $sourceSkill)) {
    throw "Missing Skill file: $sourceSkill"
}

New-Item -ItemType Directory -Path $targetPackage -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $targetPackage "knowledge_base") -Force | Out-Null
New-Item -ItemType Directory -Path $targetSkillDirectory -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $sourcePackage "__init__.py") -Destination $targetPackage -Force
Copy-Item -LiteralPath (Join-Path $sourcePackage "run_demo.py") -Destination $targetPackage -Force
Copy-Item -LiteralPath (Join-Path $sourcePackage "seed_data.py") -Destination $targetPackage -Force
Copy-Item -LiteralPath (Join-Path $sourcePackage "workflow.py") -Destination $targetPackage -Force
Copy-Item -Path (Join-Path $sourceKnowledgeBase "*") -Destination (Join-Path $targetPackage "knowledge_base") -Force
Copy-Item -LiteralPath $sourceSkill -Destination (Join-Path $targetSkillDirectory "SKILL.md") -Force

Write-Host "Installed e-commerce workflow to: $targetPackage"
Write-Host "Installed Nanobot Skill to: $targetSkillDirectory"
Write-Host 'Next: open Nanobot WebUI and invoke the ecommerce-operations skill.'
