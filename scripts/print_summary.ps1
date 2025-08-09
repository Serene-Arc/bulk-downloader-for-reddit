if (($args[0] -eq $null) -or -Not (Test-Path -Path $args[0] -PathType Leaf)) {
    Write-Host "CANNOT FIND LOG FILE"
    Exit 1
}
elseif (Test-Path -Path $args[0] -PathType Leaf) {
    $file=$args[0]
}

Write-Host -NoNewline "Downloaded submissions: "
Write-Host (Select-String -Path $file -Pattern "Downloaded submission" -AllMatches).Matches.Count
Write-Host -NoNewline "Failed downloads: "
Write-Host (Select-String -Path $file -Pattern "failed to download submission" -AllMatches).Matches.Count
Write-Host -NoNewline "Files already downloaded: "
Write-Host (Select-String -Path $file -Pattern "already exists, continuing" -AllMatches).Matches.Count
Write-Host -NoNewline "Hard linked submissions: "
Write-Host (Select-String -Path $file -Pattern "Hard link made" -AllMatches).Matches.Count
Write-Host -NoNewline "Excluded submissions: "
Write-Host (Select-String -Path $file -Pattern "in exclusion list" -AllMatches).Matches.Count
Write-Host -NoNewline "Files with existing hash skipped: "
Write-Host (Select-String -Path $file -Pattern "downloaded elsewhere" -AllMatches).Matches.Count
Write-Host -NoNewline "Submissions from excluded subreddits: "
Write-Host (Select-String -Path $file -Pattern "in skip list" -AllMatches).Matches.Count
