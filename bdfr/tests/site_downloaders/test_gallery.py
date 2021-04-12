#!/usr/bin/env python3
# coding=utf-8

import praw
import pytest

from bdfr.site_downloaders.gallery import Gallery


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected'), (
    ('https://www.reddit.com/gallery/m6lvrh', {
        'https://preview.redd.it/18nzv9ch0hn61.jpg?width=4160&'
        'format=pjpg&auto=webp&s=470a825b9c364e0eace0036882dcff926f821de8',
        'https://preview.redd.it/jqkizcch0hn61.jpg?width=4160&'
        'format=pjpg&auto=webp&s=ae4f552a18066bb6727676b14f2451c5feecf805',
        'https://preview.redd.it/k0fnqzbh0hn61.jpg?width=4160&'
        'format=pjpg&auto=webp&s=c6a10fececdc33983487c16ad02219fd3fc6cd76',
        'https://preview.redd.it/m3gamzbh0hn61.jpg?width=4160&'
        'format=pjpg&auto=webp&s=0dd90f324711851953e24873290b7f29ec73c444'
    }),
    ('https://www.reddit.com/gallery/ljyy27', {
        'https://preview.redd.it/04vxj25uqih61.png?width=92&'
        'format=png&auto=webp&s=6513f3a5c5128ee7680d402cab5ea4fb2bbeead4',
        'https://preview.redd.it/0fnx83kpqih61.png?width=241&'
        'format=png&auto=webp&s=655e9deb6f499c9ba1476eaff56787a697e6255a',
        'https://preview.redd.it/7zkmr1wqqih61.png?width=237&'
        'format=png&auto=webp&s=19de214e634cbcad9959f19570c616e29be0c0b0',
        'https://preview.redd.it/u37k5gxrqih61.png?width=443&'
        'format=png&auto=webp&s=e74dae31841fe4a2545ffd794d3b25b9ff0eb862'
    }),
))
def test_gallery_get_links(test_url: str, expected: set[str]):
    results = Gallery._get_links(test_url)
    assert set(results) == expected


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id', 'expected_hashes'), (
    ('m6lvrh', {
        '6c8a892ae8066cbe119218bcaac731e1',
        '93ce177f8cb7994906795f4615114d13',
        '9a293adf19354f14582608cf22124574',
        'b73e2c3daee02f99404644ea02f1ae65'
    }),
    ('ljyy27', {
        '1bc38bed88f9c4770e22a37122d5c941',
        '2539a92b78f3968a069df2dffe2279f9',
        '37dea50281c219b905e46edeefc1a18d',
        'ec4924cf40549728dcf53dd40bc7a73c'
    }),
))
def test_gallery_download(test_submission_id: str, expected_hashes: set[str], reddit_instance: praw.Reddit):
    test_submission = reddit_instance.submission(id=test_submission_id)
    gallery = Gallery(test_submission)
    results = gallery.find_resources()
    [res.download(120) for res in results]
    hashes = [res.hash.hexdigest() for res in results]
    assert set(hashes) == expected_hashes
