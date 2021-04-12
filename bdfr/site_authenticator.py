#!/usr/bin/env python3
# coding=utf-8

import configparser


class SiteAuthenticator:
    def __init__(self, cfg: configparser.ConfigParser):
        self.imgur_authentication = None
