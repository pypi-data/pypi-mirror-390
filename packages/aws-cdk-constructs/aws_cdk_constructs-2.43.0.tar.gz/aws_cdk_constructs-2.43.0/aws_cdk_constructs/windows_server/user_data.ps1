Set-PSDebug -Trace 2;

# Temp Folder          
mkdir C:\temp

$S3Bucket = "fao-aws-configuration-files"

# Hardening
$S3KeyHarden = "windows/hardening.reg"
$LocalFileHarden = "C:\temp\hardening.reg"
Copy-S3Object -BucketName $S3Bucket -Key "$S3KeyHarden" -LocalFile "$LocalFileHarden"
regedit /s $LocalFileHarden


# SentinelOne Installation
$S3KeySO = "windows/SentinelOneInstaller_windows_64bit_v23_1_1_140.exe"
$LocalFileSO = "C:\temp\SentinelOneInstaller_windows_64bit_v23_1_1_140.exe"
Copy-S3Object -BucketName $S3Bucket -Key "$S3KeySO" -LocalFile "$LocalFileSO"

$token = (Get-SSMParameter -Name '/windows/SO' -WithDecryption $true).Value
$parm1 = '/q'

$process = Start-Process $LocalFileSO -ArgumentList "/t=$token $parm1" 

# This is to wait till SentinelOne has been installed and in case it fails, after 5 minutes the Installation aborts 

$i = 20

While (((get-process "SentinelCtl" -ea SilentlyContinue) -eq $Null) -and ($i -ge 0)){ 
    Start-Sleep -s 15
    $i--
}

# Cloud watch agent Installation

$S3KeyCWAg = "windows/AmazonCloudWatchAgent.zip"
$LocalFileCWAg = "C:\temp\AmazonCloudWatchAgent.zip"
Copy-S3Object -BucketName $S3Bucket -Key "$S3KeyCWAg" -LocalFile "$LocalFileCWAg"
Expand-Archive -Path $LocalFileCWAg -DestinationPath "C:\temp\AmazonCloudWatchAgent"
Set-Location -Path "C:\temp\AmazonCloudWatchAgent"
.\install.ps1

$S3KeyCWAgFile = "windows/config.json"
$LocalFileCWAgFile = "C:\Program Files\Amazon\AmazonCloudWatchAgent\config.json"
Copy-S3Object -BucketName $S3Bucket -Key "$S3KeyCWAgFile" -LocalFile "$LocalFileCWAgFile"
(Get-Content $LocalFileCWAgFile).replace('SERVER_NAME', '_EC2Name_') | Set-Content  $LocalFileCWAgFile

# Configuring CloudWatch Agent to start at Server startup

mkdir C:\script
$S3KeyCWAgStrt = "windows/cwagent.ps1"
$LocalFileCWAgStrt = "C:\script\cwagent.ps1"
Copy-S3Object -BucketName $S3Bucket -Key "$S3KeyCWAgStrt" -LocalFile "$LocalFileCWAgStrt"
schtasks /create /tn "CloudWatchAgent" /sc onstart /delay 0000:30 /rl highest /ru system /tr "powershell.exe -file C:\script\cwagent.ps1"


# Changing DNS

# Identifying the Subnet
$Subnet = "_EC2SubnetId_"


# Identifying the chosen DNS 
$DNSType = "_DNSType_"
if($DNSType -eq 'DNSHQ') {
    if (($Subnet -eq 'subnet-1bc5357d') -or ($Subnet -eq 'subnet-4231c124') -or ($Subnet -eq 'subnet-9ed9e4c5') -or ($Subnet -eq 'subnet-25dfe27e')) { $DnsIp = "10.97.8.10,10.97.16.10"}

    if (($Subnet -eq 'subnet-db37f093') -or ($Subnet -eq 'subnet-3d2aed75') -or ($Subnet -eq 'subnet-7fc33319') -or ($Subnet -eq 'subnet-7aca3a1c')) { $DnsIp = "10.97.16.10,10.97.8.10"}
}


if($DNSType -eq 'DNSFIELD1'){$DnsIp = "10.97.9.10,10.97.17.10"}

# DNS Change
Get-NetAdapter | Set-DnsClientServerAddress -ServerAddresses $DnsIp;

Start-Sleep -s 30

# Change timezone
Set-TimeZone -Name "W. Europe Standard Time"

# Install Rapid7
$S3KeyRapid7 = "windows/R7agent.zip"
$LocalRapid7 = "C:\temp\R7agent.zip"
Copy-S3Object -BucketName $S3Bucket -Key "$S3KeyRapid7" -LocalFile "$LocalRapid7"
Expand-Archive $LocalRapid7 C:\temp\
msiexec /i C:\temp\R7agent\agentInstaller-x86_64.msi /quiet

Start-Sleep -s 60


# Delete the temp Folder
rmdir -Force -Recurse C:\temp


# Changing EC2 Name and Restarting
$EC2Name = "_EC2Name_"
Rename-Computer -NewName $EC2Name -force -restart