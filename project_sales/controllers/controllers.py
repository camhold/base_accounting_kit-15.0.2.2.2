# -*- coding: utf-8 -*-
# from odoo import http


# class ProjectSales(http.Controller):
#     @http.route('/project_sales/project_sales', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_sales/project_sales/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_sales.listing', {
#             'root': '/project_sales/project_sales',
#             'objects': http.request.env['project_sales.project_sales'].search([]),
#         })

#     @http.route('/project_sales/project_sales/objects/<model("project_sales.project_sales"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_sales.object', {
#             'object': obj
#         })
