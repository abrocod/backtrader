#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2020 Jinchao Lin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import collections
from datetime import date, datetime
import io
import itertools

from ..utils.py3 import (urlopen, urlquote, ProxyHandler, build_opener,
                         install_opener)

import backtrader as bt
from . import *
from ..utils import date2num


class FirstRateCSVData(GenericCSVData):
    ''' Datafeed for FirstRate data source 
        File Format : {DateTime, Open, High, Low, Close, Volume} - OHLC
        Time zone is US Eastern Time   
        Times with zero volume are omitted (thus gaps in the data sequence are when there have been no trades)
    '''
    params = (
        ('fromdate', datetime(2017, 1, 1)), 
        ('todate', datetime(2019, 1, 1)), 
        ('nullvalue', 0.0),  # good?
        ('dtformat', ('%Y-%m-%d %H:%M:%S')),
        ('dataname', '/Users/jinchaolin/FirstRateReady/futures-active_adjusted_1min_8sjor/ES_continuous_adjusted_1min.txt'),
        ('openinterest', -1),
    )

    # def start(self):
    #     firstrate_path = '/Users/jinchaolin/FirstRateReady/futures-active_adjusted_1min_8sjor/'
    #     firstrate_file = self.p.product + '_continuous_adjusted_1min.txt'
    #     self.p.dataname = firstrate_path + firstrate_file
    #     print(f'dataname is {self.p.dataname}')
