# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.tools.misc import get_lang

class AccountBalanceReport(models.TransientModel):
    _inherit = "account.common.report"
    _name = 'account.balance.cl.report'
    _description = 'Trial Balance CL Report'

    display_account = fields.Selection([('all', 'All'), ('movement', 'With movements'),
                                        ('not_zero', 'With balance is not equal to 0'), ],
                                       string='Display Accounts', required=True, default='movement')

    journal_ids = fields.Many2many('account.journal', 'account_balance_cl_report_journal_rel', 'account_id', 'journal_id', string='Journals', required=True, default=[])

    def _print_report(self, data):
        data = self.pre_print_report(data)
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('l10n_cl_balance.action_report_cl_trial_balance').report_action(
            records, data=data)

    def pre_print_report(self, data):
        data['form'].update(self.read(['display_account'])[0])
        return data
    
    def get_account_move_lines(self):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        data['form'].update(self.read(['display_account'])[0])
        display_account = data['form'].get('display_account')
        accounts =self.env['account.account'].search([])
        account_accounts = self.with_context(data['form'].get('used_context'))._get_account_accounts(accounts, display_account)
        return account_accounts
        
    def _get_account_accounts(self, accounts, display_account):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_accounts = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            res['user_type_id'] = account.user_type_id.name
            res['ident'] = account.user_type_id.id
            if account.id in account_result.keys():
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            if display_account == 'all':
                account_accounts.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_accounts.append(res)
            if display_account == 'movement' and (not currency.is_zero(res['debit']) or not currency.is_zero(res['credit'])):
                account_accounts.append(res)
        codes = list(map(lambda x:x['code'], account_accounts))
        account_accounts  = self.env['account.account'].search([('code', 'in', codes)])
        account_move_lines = self._get_account_move_lines(accounts)
        action = self.env.ref('account.action_account_moves_all_tree').read()[0]
        action['domain'] = [('id', 'in', account_move_lines.ids)]
        action['context'] = {'group_by': ['account_id']}
        return action
        
    
    def _get_account_move_lines(self, accounts):
        account_move_line_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT id" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters )
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_move_line_result[row.pop('id')] = row
        ids = list(account_move_line_result.keys())
        account_move_lines = self.env['account.move.line'].browse( ids)
        return account_move_lines
        
