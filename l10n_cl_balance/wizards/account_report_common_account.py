# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountCommonAccountReport(models.TransientModel):
    _name = 'account.common.account.report'
    _description = 'Account Common Account Report'
    _inherit = "account.common.report"



    def pre_print_report(self, data):
        data['form'].update(self.read(['display_account'])[0])
        return data
