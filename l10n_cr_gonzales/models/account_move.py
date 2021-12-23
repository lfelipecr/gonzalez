# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

class AccountMove(models.Model):
    _inherit = "account.move"

    is_name_manual = fields.Boolean('Nombre manual')

    @api.depends('posted_before', 'state', 'journal_id', 'date')
    def _compute_name(self):
        if self.is_name_manual:
            pass
        else:
            super(AccountMove, self)._compute_name()