# Description: Script to prep CSEC 471 Win 10 Instances
# Author(s): Andrew Afonso


# Strings for Prompts 
$title = "Confirmation Prompt"
$choices = "&Yes", "&No" # 0=Yes, 1=No
$default = 1

# List Installed Packages
$pickZero = $Host.UI.PromptForChoice($title, "List installed Applications?", $choices, $default)
if ($pickZero -eq 0){
    Get-AppxPackage | Select Name, Version, NonRemovable, InstallLocation
}

# Remove 3rd Party Bloatware Standalone Win 10 (Duolingo, Pandora, Eclipse Manager, Photoshop Express, Code Writer)
$pickOne = $Host.UI.PromptForChoice($title, "Remove Bloatware (If Found):`nDuolingo, Pandora, Eclipse Manager, Photoshop Express, Code Writer?", $choices, $default)
if ($pickOne -eq 0){
    Get-AppxPackage *Duolingo* | Remove-AppxPackage
    Get-AppxPackage *PandoraMedia* | Remove-AppxPackage
    Get-AppxPackage *EclipseManager* | Remove-AppxPackage
    Get-AppxPackage *PhotoshopExpress* | Remove-AppxPackage
    Get-AppxPackage *ActiproSoftware* | Remove-AppxPackage
}

# Remove unneeded Windows Apps (Xbox companion, Xbox live, Your Phone, Skype, PowerBI)
$pickTwo = $Host.UI.PromptForChoice($title, "Remove Unneeded Microsoft Apps (If Found):`nXbox companion, Xbox live, Your Phone, Skype, PowerBI?", $choices, $default)
if ($pickTwo -eq 0){
    Get-AppxPackage *XboxApp* | Remove-AppxPackage
    Get-AppxPackage *Xbox.TCUI* | Remove-AppxPackage
    Get-AppxPackage *YourPhone* | Remove-AppxPackage
    Get-AppxPackage *SkypeApp* | Remove-AppxPackage
    Get-AppxPackage *PowerBI* | Remove-AppxPackage
}

# Create Registry Key to Disable OneDrive
$doesOuterExist = Test-Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\OneDrive' # Check if OneDrive key already exists. If not, make it. 
if($doesOuterExist -eq $false){ # If OneDrive Key doesnt exist
    $pickThree = $Host.UI.PromptForChoice($title, "Disable OneDrive?", $choices, $default)
    if ($pickThree -eq 0){
        Set-Location HKLM:
        New-Item -Path .\SOFTWARE\Policies\Microsoft\Windows -Name OneDrive
        New-ItemProperty -Path .\SOFTWARE\Policies\Microsoft\Windows\OneDrive -Name DisableFileSyncNGSC -Value 1 -PropertyType DWord # Create the entry to disable OneDrive
    }
}
if($doesOuterExist -eq $true){ # If entry does exist, prompt to override. 
    $pickThree = $Host.UI.PromptForChoice($title, "It seems a registry key already exists to disable OneDrive.`nOverwrite existing value to disable OneDrive?", $choices, $default)
    if ($pickThree -eq 0){
        Set-Location HKLM:\SOFTWARE\Policies\Microsoft\Windows\OneDrive
        Set-ItemProperty -Path . -Name DisableFileSyncNGSC -Value 1
    }
}

# Disable SmartScreen for Microsoft Edge
$doesOuterExist = Test-Path 'HKLM:\SOFTWARE\Policies\Microsoft\MicrosoftEdge\PhishingFilter' # Check if relevant MS Edge key already exists.
if($doesOuterExist -eq $false){ # If Edge Key doesnt exist
    $pickFour = $Host.UI.PromptForChoice($title, "Disable SmartScreen for Microsoft Edge?", $choices, $default)
    if ($pickFour -eq 0){
        Set-Location HKLM:
        New-Item -Path .\SOFTWARE\Policies\Microsoft -Name MicrosoftEdge
        New-Item -Path .\SOFTWARE\Policies\Microsoft\MicrosoftEdge -Name PhishingFilter
        New-ItemProperty -Path .\SOFTWARE\Policies\Microsoft\MicrosoftEdge\PhishingFilter -Name EnabledV9 -Value 0 -PropertyType DWord
    }
}
if($doesOuterExist -eq $true){ # If entry does exist, prompt to override. 
    $pickFour = $Host.UI.PromptForChoice($title, "It seems a registry key already exists to disable Microsoft Edge SmartScreen.`nOverwrite existing value to disable MS Edge SmartScreen?", $choices, $default)
    if ($pickFour -eq 0){
        Set-ItemProperty -Path HKLM:\SOFTWARE\Policies\Microsoft\MicrosoftEdge\PhishingFilter -Name EnabledV9 -Value 0 
    }
}

# Disable SmartScreen for Microsoft Store Apps
$doesOuterExist = Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppHost' # Check if relevant AppHost key already exists.
if($doesOuterExist -eq $false){ # If AppHost Key doesnt exist
    $pickFive = $Host.UI.PromptForChoice($title, "Disable SmartScreen for Microsoft Store Apps?", $choices, $default)
    if ($pickFive -eq 0){
        Set-Location HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\
        New-Item -Path . -Name AppHost
        New-ItemProperty -Path .\AppHost -Name EnableWebContentEvaluation -Value 0 -PropertyType DWord
    }
}
if($doesOuterExist -eq $true){ # If entry does exist, prompt to override. 
    $pickFive = $Host.UI.PromptForChoice($title, "It seems a registry key already exists to configure Microsoft Store SmartScreen.`nOverwrite existing value to disable Microsoft Store SmartScreen?", $choices, $default)
    if ($pickFive -eq 0){
        Set-ItemProperty -Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppHost -Name EnableWebContentEvaluation -Value 0 
    }
}
