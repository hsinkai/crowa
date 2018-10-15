#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Filename: xml2csv
Auchor: CJ Lin
"""

import argparse
from string import Template

import petl
import yaml

parser = argparse.ArgumentParser(description='Parse an xml file to csv via an yaml config.')
parser.add_argument('-f', metavar='xml', help='path of input xml file')
parser.add_argument('-t', metavar='csv', help='path of output csv file')
parser.add_argument('-e', action='store_true', help='add quotes to header to fit SQL pattern')
parser.add_argument('config', help='path of config yaml file')
args = parser.parse_args()

info = yaml.load(open(args.config))
xml_file = args.f or info['xml']
csv_file = args.t or info['csv']
table = petl.empty()

# substitute namespace to keys
for key in eval(Template(str(info['keys'])).substitute(**info['namespace'])) if 'namespace' in info else info['keys']:
    # collect data from each key
    table = table.cat(petl.fromxml(xml_file, key['anchor'], key['select']))

if 'pks' in info:
    table = table.mergeduplicates(info['pks'] if len(info['pks']) > 1 else info['pks'][0])

if 'orderBy' in info:
    table = table.sort(info['orderBy'])

if 'skip' in info:
    table = table.tail(len(table) - info['skip'])

if 'first' in info:
    table = table.head(info['first'])

if 'replace' in info:
    for a, b in info['replace'].iteritems():
        table = table.replaceall(a, b)

if args.e:
    table = table.rename({i: '`' + i + '`' for i in table[0]})

table.convertall(lambda x: '\N' if x is None or x.strip() == '' else x.strip()
    ).tocsv(csv_file)
