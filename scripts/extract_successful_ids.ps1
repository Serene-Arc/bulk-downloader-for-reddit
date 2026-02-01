if (($args[0] -eq $null) -or -Not (Test-Path -Path $args[0] -PathType Leaf)) {
    Write-Output "CANNOT FIND LOG FILE"
    Exit 1
}
elseif (Test-Path -Path $args[0] -PathType Leaf) {
    $file=$args[0]
}

Select-String -Path $file -Pattern "Downloaded submission" | ForEach-Object { -split $_.Line | Select-Object -Last 3 | Select-Object -SkipLast 2 }
Select-String -Path $file -Pattern "Resource hash" | ForEach-Object { -split $_.Line | Select-Object -Last 3 | Select-Object -SkipLast 2 }
Select-String -Path $file -Pattern "Download filter" | ForEach-Object { -split $_.Line | Select-Object -Last 4 | Select-Object -SkipLast 3 }
Select-String -Path $file -Pattern "already exists, continuing" | ForEach-Object { -split $_.Line | Select-Object -Last 4 | Select-Object -SkipLast 3 }
Select-String -Path $file -Pattern "Hard link made" | ForEach-Object { -split $_.Line | Select-Object -Last 1 }
Select-String -Path $file -Pattern "filtered due to score" | ForEach-Object { -split $_.Line | Select-Object -Index 8 }
