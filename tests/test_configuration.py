#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import MagicMock

import pytest

from bdfr.configuration import Configuration


@pytest.mark.parametrize('arg_dict', (
    {'directory': 'test_dir'},
    {
        'directory': 'test_dir',
        'no_dupes': True,
    },
))
def test_process_click_context(arg_dict: dict):
    test_config = Configuration()
    test_context = MagicMock()
    test_context.params = arg_dict
    test_config.process_click_arguments(test_context)
    test_config = vars(test_config)
    assert all([test_config[arg] == arg_dict[arg] for arg in arg_dict.keys()])
