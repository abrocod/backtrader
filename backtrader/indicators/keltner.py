#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2021 Jinchao Lin
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

import backtrader as bt

# https://analyzingalpha.com/keltner-channels


class keltnerChannel(bt.Indicator):
    lines = ('upper', 'basis', 'lower',)
    params = (
        ('ema', 20), 
        ('period', 10),
        ('width', 2.25),
        )

    plotinfo = dict(subplot=False)  # plot along with data
    plotlines = dict(
        basis=dict(ls='--'),  # dashed line
        upper=dict(_samecolor=True),  # use same color as prev line (mid)
        lower=dict(_samecolor=True),  # use same color as prev line (upper)
    )
    
    def __init__(self):
        self.lines.basis = bt.ind.EMA(self.data, period=self.p.ema)
        atr = bt.ind.ATR(self.data, period=self.p.period)
        self.lines.upper = self.lines.basis + self.p.width * atr
        self.lines.lower = self.lines.basis - self.p.width * atr
