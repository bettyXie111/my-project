$ErrorActionPreference = "Stop"

$checkpoint = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspace = Split-Path -Parent (Split-Path -Parent $checkpoint)

Copy-Item -Path (Join-Path $checkpoint "shared") -Destination (Join-Path $workspace "shared") -Recurse -Force
Copy-Item -Path (Join-Path $checkpoint "run_autodate_batch.py") -Destination (Join-Path $workspace "run_autodate_batch.py") -Force
Copy-Item -Path (Join-Path $checkpoint "pipeline_guard.py") -Destination (Join-Path $workspace "pipeline_guard.py") -Force

Write-Host "Restored checkpoint from $checkpoint"
