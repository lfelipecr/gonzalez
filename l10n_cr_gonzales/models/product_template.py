# -*- coding: utf-8 -*-
from odoo import fields, osv, models, api
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)
import pdb
#from .warning import warning
import requests


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_min = fields.Float(string='Cantidad mínima')

class ProductProduct(models.Model):

    _inherit = "product.product"

    qty_min = fields.Float(string='Cantidad mínima', related='product_tmpl_id.qty_min', readonly=False)