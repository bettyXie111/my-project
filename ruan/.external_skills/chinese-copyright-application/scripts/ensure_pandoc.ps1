param(
  [string]$ProjectRoot = ".",
  [string]$Version = "3.9.0.2",
  [string]$ZipPath = ""
)

$ErrorActionPreference = "Stop"

function Get-PandocVersion {
  param(
    [string]$Name
  )

  $match = [regex]::Match($Name, "pandoc-(?<version>\d+(?:\.\d+){1,3})")
  if ($match.Success) {
    try {
      return [version]$match.Groups["version"].Value
    }
    catch {
    }
  }

  return [version]"0.0"
}

function Get-InstalledPandocExe {
  param(
    [string]$ToolsDir,
    [string]$RequestedExe
  )

  $cmd = Get-Command pandoc -ErrorAction SilentlyContinue
  if ($null -ne $cmd) {
    return $cmd.Source
  }

  if (Test-Path -LiteralPath $RequestedExe) {
    return (Resolve-Path -LiteralPath $RequestedExe).Path
  }

  if (-not (Test-Path -LiteralPath $ToolsDir)) {
    return $null
  }

  $candidate = Get-ChildItem -LiteralPath $ToolsDir -Directory -ErrorAction SilentlyContinue |
    Where-Object {
      $_.Name -like "pandoc-*" -and (Test-Path -LiteralPath (Join-Path $_.FullName "pandoc.exe"))
    } |
    Sort-Object `
      @{ Expression = { Get-PandocVersion $_.Name }; Descending = $true }, `
      @{ Expression = { $_.LastWriteTime }; Descending = $true } |
    Select-Object -First 1

  if ($null -ne $candidate) {
    return (Resolve-Path -LiteralPath (Join-Path $candidate.FullName "pandoc.exe")).Path
  }

  return $null
}

function Get-LocalPandocZip {
  param(
    [string]$ProjectPath,
    [string]$ToolsDir,
    [string]$RequestedVersion,
    [string]$ExplicitZipPath
  )

  if ($ExplicitZipPath) {
    if (-not (Test-Path -LiteralPath $ExplicitZipPath)) {
      throw "Pandoc zip not found: $ExplicitZipPath"
    }

    return (Resolve-Path -LiteralPath $ExplicitZipPath).Path
  }

  $searchRoots = @(
    $ToolsDir,
    $ProjectPath,
    "D:\"
  )

  if ($env:USERPROFILE) {
    $searchRoots += (Join-Path $env:USERPROFILE "Downloads")
  }

  foreach ($candidatePath in @(
    (Join-Path $ToolsDir ("pandoc-" + $RequestedVersion + "-windows-x86_64.zip")),
    (Join-Path $ProjectPath ("pandoc-" + $RequestedVersion + "-windows-x86_64.zip")),
    ("D:\pandoc-" + $RequestedVersion + "-windows-x86_64.zip")
  )) {
    if ($candidatePath -and (Test-Path -LiteralPath $candidatePath)) {
      return (Resolve-Path -LiteralPath $candidatePath).Path
    }
  }

  $candidates = foreach ($root in $searchRoots | Select-Object -Unique) {
    if (-not $root -or -not (Test-Path -LiteralPath $root)) {
      continue
    }

    Get-ChildItem -LiteralPath $root -Filter "pandoc-*-windows-x86_64.zip" -File -ErrorAction SilentlyContinue
  }

  $candidate = $candidates |
    Sort-Object `
      @{ Expression = { Get-PandocVersion $_.BaseName }; Descending = $true }, `
      @{ Expression = { $_.LastWriteTime }; Descending = $true } |
    Select-Object -First 1

  if ($null -ne $candidate) {
    return $candidate.FullName
  }

  return $null
}

$project = (Resolve-Path $ProjectRoot).Path
$toolsDir = Join-Path $project ".tools/pandoc"
$pandocDir = Join-Path $toolsDir ("pandoc-" + $Version)
$pandocExe = Join-Path $pandocDir "pandoc.exe"

New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null

$installedPandoc = Get-InstalledPandocExe -ToolsDir $toolsDir -RequestedExe $pandocExe
if ($installedPandoc) {
  Write-Output $installedPandoc
  exit 0
}

$localZip = Get-LocalPandocZip -ProjectPath $project -ToolsDir $toolsDir -RequestedVersion $Version -ExplicitZipPath $ZipPath
if ($localZip) {
  Expand-Archive -LiteralPath $localZip -DestinationPath $toolsDir -Force

  $installedPandoc = Get-InstalledPandocExe -ToolsDir $toolsDir -RequestedExe $pandocExe
  if ($installedPandoc) {
    Write-Output $installedPandoc
    exit 0
  }
}

$zipPath = Join-Path $toolsDir ("pandoc-" + $Version + "-windows-x86_64.zip")
$url = "https://github.com/jgm/pandoc/releases/download/$Version/pandoc-$Version-windows-x86_64.zip"

Invoke-WebRequest -Uri $url -OutFile $zipPath
Expand-Archive -LiteralPath $zipPath -DestinationPath $toolsDir -Force

$installedPandoc = Get-InstalledPandocExe -ToolsDir $toolsDir -RequestedExe $pandocExe
if (-not $installedPandoc) {
  throw "Pandoc is unavailable after local extraction/download. Expected under: $toolsDir"
}

Write-Output $installedPandoc
