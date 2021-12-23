# -*- coding: utf-8 -*-

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    code = fields.Char(string=u'Código')
    abbreviation = fields.Char(string='Abreviatura')
    location = fields.Char(string='Ubicación')

