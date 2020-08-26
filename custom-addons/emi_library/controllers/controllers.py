# -*- coding: utf-8 -*-
# from odoo import http


# class EmiLibrary(http.Controller):
#     @http.route('/emi_library/emi_library/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/emi_library/emi_library/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('emi_library.listing', {
#             'root': '/emi_library/emi_library',
#             'objects': http.request.env['emi_library.emi_library'].search([]),
#         })

#     @http.route('/emi_library/emi_library/objects/<model("emi_library.emi_library"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('emi_library.object', {
#             'object': obj
#         })
