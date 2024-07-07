# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    def action_project(self):
        action = self.env.ref("sale.action_quotations_with_onboarding").read()[0]
        action['context'] = {'default_project_id': self.id,}
        action["domain"] = [("proyecto", "=", self.id)]
        return action
