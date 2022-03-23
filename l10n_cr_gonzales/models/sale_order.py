# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    state = fields.Selection([
        ('created','Borrador'),
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Estado', readonly=True, copy=False, index=True, tracking=3, default='created')

    # state = fields.Selection(selection_add=[
    #     ('created', 'Borrador')
    # ], ondelete={'created': 'cascade'}, default='created')

    is_revised = fields.Boolean('Revisado') #state "CREATED"

    #Todo: SE AÑADE EL CAMPO CREATED A ATRIBUTO STATES.
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)],
                                         'created': [('readonly', False)]},
                                 copy=False, default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")

    def _default_validity_date(self):
        if self.env['ir.config_parameter'].sudo().get_param('sale.use_quotation_validity_days'):
            days = self.env.company.quotation_validity_days
            if days > 0:
                return fields.Date.to_string(datetime.now() + timedelta(days))
        return False

    validity_date = fields.Date(string='Expiration', readonly=True, copy=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)],
                                                                                        'created': [('readonly', False)]},default=_default_validity_date)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)],
                'created': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)],
                'created': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)],
                'created': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)],
                                              'created': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        readonly=True, copy=False, check_company=True,  # Unrequired company
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)],
                'created': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="The analytic account related to a sales order.")


    #Pasar estado a Revisado
    def action_revised(self):
        if self.state == 'created':
            self.state = 'draft'
            self.is_revised = True

    def unlink(self):
        for order in self:
            if order.state == 'created': #Añadimos created
                return models.Model.unlink(order)
            elif order.state not in ('draft', 'cancel'):
                raise UserError(_('You can not delete a sent quotation or a confirmed sales order. You must first cancel it.'))
        return super().unlink()

    def _validation_partner(self,partner_id):
        if not partner_id.code:
            raise ValidationError(_('El cliente no tiene un código definido.'))

        if not partner_id.abbreviation:
            raise ValidationError(_('El cliente no tiene una abreviatura definida.'))

        if not partner_id.location:
            raise ValidationError(_('El cliente no tiene una locación definida.'))


    @api.model
    def create(self, vals):
        #validaciones
        if vals['partner_id']:
            partner_id = self.env['res.partner'].sudo().browse(vals['partner_id'])
        else:
            raise ValidationError(_('Defina un cliente por favor.'))

        self._validation_partner(partner_id)

        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            #Todo: Campo a reemplazar 23-12-21
            #vals['name'] = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('New')
            sequence = self.env.ref('l10n_cr_gonzales.seq_sale_order_gonzales').next_by_id() or _('New')
            #mes = datetime.today().month
            #anio = datetime.today().year
            #day = datetime.today().day
            #mes_anio_dia = str(mes)+''+str(anio)+''+str(day)
            #mes_anio_dia = str(mes)+''+str(anio)+''+str(day)
            mes_anio_dia = datetime.today().strftime('%m%y%d')
            name = partner_id.location + '-' + partner_id.code + '-' + mes_anio_dia + '-'+partner_id.abbreviation + '-' + sequence
            vals['name'] = name

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist.id)
        result = super(SaleOrder, self).create(vals)
        return result