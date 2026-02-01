if (-not ([string]::IsNullOrEmpty($env:REDDIT_TOKEN)))
{
    Copy-Item .\\bdfr\\default_config.cfg .\\tests\\test_config.cfg
    Write-Output "`nuser_token = $env:REDDIT_TOKEN" >> ./tests/test_config.cfg
}
