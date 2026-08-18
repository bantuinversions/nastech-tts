$ErrorActionPreference = "Stop"
$SourceRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$GuiModule = "installer.gui"
$LauncherModule = "installer.launcher"
$PythonWindowless = Get-Command pyw -ErrorAction SilentlyContinue
if ($PythonWindowless) {
    & pyw -m $GuiModule --source-root $SourceRoot -- $args
} else {
    & py -m $GuiModule --source-root $SourceRoot -- $args
}
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
