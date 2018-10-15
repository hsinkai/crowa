#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dateutil.parser

import db
import log_module
import stwarning

__all__ = ['log_module', 'db', 'stwarning']


def parsing(input):
    return dateutil.parser.parse(input).replace(tzinfo=None)
