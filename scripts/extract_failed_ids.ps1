if (($args[0] -eq $null) -or -Not (Test-Path -Path $args[0] -PathType Leaf)) {
    Write-Output "CANNOT FIND LOG FILE"
    Exit 1
}
elseif (Test-Path -Path $args[0] -PathType Leaf) {
    $file=$args[0]
}

Select-String -Path $file -Pattern "Could not download submission" | ForEach-Object { -split $_.Line | Select-Object -Skip 11 | Select-Object -First 1 } | ForEach-Object { $_.substring(0,$_.Length-1) }
Select-String -Path $file -Pattern "Failed to download resource" | ForEach-Object { -split $_.Line | Select-Object -Skip 14 | Select-Object -First 1 }
Select-String -Path $file -Pattern "failed to download submission" | ForEach-Object { -split $_.Line | Select-Object -Skip 13 | Select-Object -First 1 } | ForEach-Object { $_.substring(0,$_.Length-1) }
Select-String -Path $file -Pattern "Failed to write file" | ForEach-Object { -split $_.Line | Select-Object -Skip 13 | Select-Object -First 1 }
Select-String -Path $file -Pattern "skipped due to disabled module" | ForEach-Object { -split $_.Line | Select-Object -Skip 8 | Select-Object -First 1 }
