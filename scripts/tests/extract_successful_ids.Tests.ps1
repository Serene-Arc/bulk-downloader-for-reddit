Describe "extract_successful_ids" {
    It "fail run no args" {
        (..\extract_successful_ids.ps1) | Should -Be "CANNOT FIND LOG FILE"
    }

    It "fail run no logfile" {
        (..\extract_successful_ids.ps1 missing.txt) | Should -Be "CANNOT FIND LOG FILE"
    }

    It "success downloaded submission" {
        $down_success = (..\extract_successful_ids.ps1 example_logfiles\succeed_downloaded_submission.txt)
        $down_success | Should -HaveCount 7
        $down_success | Should -Contain "nn9cor"
    }

    It "success resource hash" {
        $hash_success = (..\extract_successful_ids.ps1 example_logfiles\succeed_resource_hash.txt)
        $hash_success | Should -HaveCount 1
        $hash_success | Should -Contain "n86jk8"
    }

    It "success download filter" {
        $filt_success = (..\extract_successful_ids.ps1 example_logfiles\succeed_download_filter.txt)
        $filt_success | Should -HaveCount 3
        $filt_success | Should -Contain "nxuxjy"
    }

    It "success already exists" {
        $exist_success = (..\extract_successful_ids.ps1 example_logfiles\succeed_already_exists.txt)
        $exist_success | Should -HaveCount 3
        $exist_success | Should -Contain "nxrq9g"
    }

    It "success hard link" {
        $link_success = (..\extract_successful_ids.ps1 example_logfiles\succeed_hard_link.txt)
        $link_success | Should -HaveCount 1
        $link_success | Should -Contain "nwnp2n"
    }

    It "success score filter" {
        $score_success = (..\extract_successful_ids.ps1 example_logfiles\succeed_score_filter.txt)
        $score_success | Should -HaveCount 2
        $score_success | Should -Contain "ljyz27"
    }
}
