# -*- coding: utf-8 -*-

from . import controllers
from . import models

from odoo import api, fields, tools
def add_philippines_location(cr, registry):
    tools.convert_file(cr, 'l10n_ph', 'data/res.country.state.csv', None, mode='init', noupdate=True, kind='init', report=None)
    tools.convert_file(cr, 'l10n_ph', 'data/res.state.city.csv', None, mode='init', noupdate=True, kind='init', report=None)
    tools.convert_file(cr, 'l10n_ph', 'data/res.city.barangay.csv', None, mode='init', noupdate=True, kind='init', report=None)