# Setup step: download and start the official Nmap installer (Setup.bat runs this).
#
# Travel Guardian needs Nmap, but can't include it: the free Npcap licence that
# comes with Nmap doesn't allow it to be bundled. So this script fetches the
# installer from nmap.org, the official site, and the user installs it.
#
# What it does:
#   1. Stops if Nmap is already installed.
#   2. Reads nmap.org's download page to find the current installer's name.
#   3. Downloads it to the Temp folder.
#   4. Checks its digital signature, so only a genuine Nmap installer is run.
#   5. Starts it. Windows asks for Administrator rights; the user clicks Yes,
#      then clicks through Nmap's setup (keep Npcap ticked).

$ErrorActionPreference = "Stop"   # stop at the first error instead of carrying on

# 1. Already installed? (the same places scanner.py looks)
$places = @("${env:ProgramFiles(x86)}\Nmap\nmap.exe", "$env:ProgramFiles\Nmap\nmap.exe")
if ((Get-Command nmap -ErrorAction SilentlyContinue) -or ($places | Where-Object { Test-Path $_ })) {
    Write-Host "Nmap is already installed. You can start Travel Guardian."
    exit 0
}

try {
    # 2. Find the installer's name, e.g. nmap-7.993-setup.exe
    Write-Host "Finding the latest Nmap installer on nmap.org..."
    $page = Invoke-WebRequest "https://nmap.org/download.html" -UseBasicParsing
    $name = [regex]::Match($page.Content, "nmap-[0-9.]+-setup\.exe").Value
    if (-not $name) { throw "couldn't find the installer on nmap.org" }

    # 3. Download it
    $file = Join-Path $env:TEMP $name
    Write-Host "Downloading $name (about 40 MB)..."
    Invoke-WebRequest "https://nmap.org/dist/$name" -OutFile $file -UseBasicParsing

    # 4. Check it is signed by Nmap's makers and the signature is valid
    $signature = Get-AuthenticodeSignature $file
    if ($signature.Status -ne "Valid" -or $signature.SignerCertificate.Subject -notlike "*O=Nmap Software LLC*") {
        Remove-Item $file
        throw "the downloaded file isn't signed by Nmap Software LLC, so it was deleted"
    }

    # 5. Run it and wait until the user finishes the setup
    Write-Host "Starting the Nmap installer. Click Yes, then keep the default options."
    Start-Process $file -Verb RunAs -Wait
    Remove-Item $file
    Write-Host "Done. You can now start Travel Guardian."
}
catch {
    Write-Host "Nmap couldn't be installed automatically: $($_.Exception.Message)"
    Write-Host "Please install it from https://nmap.org/download.html (see INSTALL.txt, step 2)."
    exit 1
}
