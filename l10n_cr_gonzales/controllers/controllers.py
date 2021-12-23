# -*- coding: utf-8 -*-
# from odoo import http


# class L10nCrGonzales(http.Controller):
#     @http.route('/l10n_cr_gonzales/l10n_cr_gonzales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_cr_gonzales/l10n_cr_gonzales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_cr_gonzales.listing', {
#             'root': '/l10n_cr_gonzales/l10n_cr_gonzales',
#             'objects': http.request.env['l10n_cr_gonzales.l10n_cr_gonzales'].search([]),
#         })

#     @http.route('/l10n_cr_gonzales/l10n_cr_gonzales/objects/<model("l10n_cr_gonzales.l10n_cr_gonzales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_cr_gonzales.object', {
#             'object': obj
#         })
