setup() {
    load ./test_helper/bats-support/load
    load ./test_helper/bats-assert/load
}

teardown() {
    rm -f successful.txt
}

@test "fail run no args" {
    run ../extract_successful_ids.sh
    assert_failure
}

@test "fail run no logfile" {
    run ../extract_successful_ids.sh ./missing.txt
    assert_failure
}

@test "success downloaded submission" {
    run ../extract_successful_ids.sh ./example_logfiles/succeed_downloaded_submission.txt
    echo "$output" > successful.txt
    assert [ "$( wc -l 'successful.txt' | awk '{ print $1 }' )" -eq "7" ];
    assert [ "$( grep -Ecv '\w{6,7}' 'successful.txt' )" -eq "0" ];
}

@test "success resource hash" {
    run ../extract_successful_ids.sh ./example_logfiles/succeed_resource_hash.txt
    echo "$output" > successful.txt
    assert [ "$( wc -l 'successful.txt' | awk '{ print $1 }' )" -eq "1" ];
    assert [ "$( grep -Ecv '\w{6,7}' 'successful.txt' )" -eq "0" ];
}

@test "success download filter" {
    run ../extract_successful_ids.sh ./example_logfiles/succeed_download_filter.txt
    echo "$output" > successful.txt
    assert [ "$( wc -l 'successful.txt' | awk '{ print $1 }' )" -eq "3" ];
    assert [ "$( grep -Ecv '\w{6,7}' 'successful.txt' )" -eq "0" ];
}

@test "success already exists" {
    run ../extract_successful_ids.sh ./example_logfiles/succeed_already_exists.txt
    echo "$output" > successful.txt
    assert [ "$( wc -l 'successful.txt' | awk '{ print $1 }' )" -eq "3" ];
    assert [ "$( grep -Ecv '\w{6,7}' 'successful.txt' )" -eq "0" ];
}

@test "success hard link" {
    run ../extract_successful_ids.sh ./example_logfiles/succeed_hard_link.txt
    echo "$output" > successful.txt
    assert [ "$( wc -l 'successful.txt' | awk '{ print $1 }' )" -eq "1" ];
    assert [ "$( grep -Ecv '\w{6,7}' 'successful.txt' )" -eq "0" ];
}

@test "success score filter" {
    run ../extract_successful_ids.sh ./example_logfiles/succeed_score_filter.txt
    echo "$output" > successful.txt
    assert [ "$( wc -l 'successful.txt' | awk '{ print $1 }' )" -eq "2" ];
    assert [ "$( grep -Ecv '\w{6,7}' 'successful.txt' )" -eq "0" ];
}
