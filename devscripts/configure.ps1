if (-not ([string]::IsNullOrEmpty($env:REDDIT_TOKEN)))
{
    copy .\\bdfr\\default_config.cfg .\\test_config.cfg
    echo "`nuser_token = $env:REDDIT_TOKEN" >> ./test_config.cfg
}