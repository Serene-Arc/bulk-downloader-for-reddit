Describe "extract_failed_ids" {
    It "fail run no args" {
        (..\extract_failed_ids.ps1) | Should -Be "CANNOT FIND LOG FILE"
    }

    It "fail run no logfile" {
        (..\extract_failed_ids.ps1 missing.txt) | Should -Be "CANNOT FIND LOG FILE"
    }

    It "fail no downloader module" {
        $down_error = (..\extract_failed_ids.ps1 example_logfiles\failed_no_downloader.txt)
        $down_error | Should -HaveCount 3
        $down_error | Should -Contain "nxv3ea"
    }

    It "fail resource error" {
        $res_error = (..\extract_failed_ids.ps1 example_logfiles\failed_resource_error.txt)
        $res_error | Should -HaveCount 1
        $res_error | Should -Contain "nxv3dt"
    }

    It "fail site downloader error" {
        $site_error = (..\extract_failed_ids.ps1 example_logfiles\failed_sitedownloader_error.txt)
        $site_error | Should -HaveCount 2
        $site_error | Should -Contain "nxpn0h"
    }

    It "fail failed file write" {
        $write_error = (..\extract_failed_ids.ps1 example_logfiles\failed_write_error.txt)
        $write_error | Should -HaveCount 1
        $write_error | Should -Contain "nnboza"
    }

    It "fail disabled module" {
        $disabled = (..\extract_failed_ids.ps1 example_logfiles\failed_disabled_module.txt)
        $disabled | Should -HaveCount 1
        $disabled | Should -Contain "m2601g"
    }
}
