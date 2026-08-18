$ErrorActionPreference = "Stop"
$SourceRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Launcher = Join-Path $SourceRoot "installer\launcher.py"
& py $Launcher --source-root $SourceRoot -- $args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
