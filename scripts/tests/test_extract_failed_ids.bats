setup() {
    load ./test_helper/bats-support/load
    load ./test_helper/bats-assert/load
}

teardown() {
    rm -f failed.txt
}

@test "fail run no logfile" {
    run ../extract_failed_ids.sh
    assert_failure
}

@test "fail no downloader module" {
    run ../extract_failed_ids.sh ./example_logfiles/failed_no_downloader.txt
    assert [ "$( wc -l 'failed.txt' | awk '{ print $1 }' )" -eq "3" ];
    assert [ "$( grep -Ecv '\w{6,7}' 'failed.txt' )" -eq "0" ];
}

@test "fail resource error" {
    run ../extract_failed_ids.sh ./example_logfiles/failed_resource_error.txt
    assert [ "$( wc -l 'failed.txt' | awk '{ print $1 }' )" -eq "1" ];
    assert [ "$( grep -Ecv '\w{6,7}' 'failed.txt' )" -eq "0" ];
}

@test "fail site downloader error" {
    run ../extract_failed_ids.sh ./example_logfiles/failed_sitedownloader_error.txt
    assert [ "$( wc -l 'failed.txt' | awk '{ print $1 }' )" -eq "2" ];
    assert [ "$( grep -Ecv '\w{6,7}' 'failed.txt' )" -eq "0" ];
}

@test "fail failed file write" {
    run ../extract_failed_ids.sh ./example_logfiles/failed_write_error.txt
    assert [ "$( wc -l 'failed.txt' | awk '{ print $1 }' )" -eq "1" ];
    assert [ "$( grep -Ecv '\w{6,7}' 'failed.txt' )" -eq "0" ];
}

@test "fail disabled module" {
    run ../extract_failed_ids.sh ./example_logfiles/failed_disabled_module.txt
    assert [ "$( wc -l 'failed.txt' | awk '{ print $1 }' )" -eq "1" ];
    assert [ "$( grep -Ecv '\w{6,7}' 'failed.txt' )" -eq "0" ];
}
