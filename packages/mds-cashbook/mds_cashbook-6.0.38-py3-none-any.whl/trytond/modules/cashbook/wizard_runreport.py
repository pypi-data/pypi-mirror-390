# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateReport, Button
from trytond.pool import Pool
from trytond.pyson import Eval, Bool
from trytond.transaction import Transaction


class RunCbReportStart(ModelView):
    'Cashbook Report'
    __name__ = 'cashbook.runrepbook.start'

    cashbook = fields.Many2One(
        string='Cashbook', required=True,
        model_name='cashbook.book', depends=['cashbooks'],
        domain=[('id', 'in', Eval('cashbooks', []))])
    cashbooks = fields.One2Many(
        string='Cashbooks', model_name='cashbook.book',
        field=None, readonly=True, states={'invisible': True})
    reconciliation = fields.Many2One(
        string='Reconciliation', required=True,
        model_name='cashbook.recon', depends=['reconciliations'],
        states={
            'readonly': ~Bool(Eval('reconciliations')),
        }, domain=[('id', 'in', Eval('reconciliations', []))])
    reconciliations = fields.Function(fields.One2Many(
        string='Reconciliations',
        model_name='cashbook.recon', field=None, readonly=True,
        states={'invisible': True}),
        'on_change_with_reconciliations')

    @fields.depends('cashbook', 'reconciliations', 'reconciliation')
    def on_change_cashbook(self):
        """ update reconciliations
        """
        if self.cashbook:
            self.reconciliations = self.on_change_with_reconciliations()
            if len(self.reconciliations or []) > 0:
                self.reconciliation = self.reconciliations[0]
            else:
                self.reconciliation = None
        else:
            self.reconciliations = []
            self.reconciliation = None

    @fields.depends('cashbook')
    def on_change_with_reconciliations(self, name=None):
        """ get reconciliations of current cashbook
        """
        Recon2 = Pool().get('cashbook.recon')

        if self.cashbook:
            recons = Recon2.search([
                ('cashbook', '=', self.cashbook.id),
                ], order=[('date_from', 'DESC')])
            return [x.id for x in recons]

# end RunCbReportStart


class RunCbReport(Wizard):
    'Cashbook Report'
    __name__ = 'cashbook.runrepbook'

    start_state = 'selrecon'
    selrecon = StateView(
        'cashbook.runrepbook.start',
        'cashbook.runrepbook_view_form', [
            Button(string='Cancel', state='end', icon='tryton-cancel'),
            Button(
                string='Report', state='report_', icon='tryton-ok',
                default=True,
                states={'readonly': ~Bool(Eval('reconciliation'))})])
    report_ = StateReport('cashbook.reprecon')

    def default_selrecon(self, fields):
        """ setup form
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Recon2 = pool.get('cashbook.recon')
        context = Transaction().context

        result = {}
        if context.get('active_model', '') == 'cashbook.book':
            result['cashbook'] = context.get('active_id', None)
        elif context.get('active_model', '') == 'cashbook.line':
            result['cashbook'] = context.get('cashbook', None)
        else:
            raise ValueError('invalid model')

        with Transaction().set_context({
                '_check_access': True}):
            books = Book.search([])
            result['cashbooks'] = [x.id for x in books]

            if len(result['cashbooks']) > 0:
                if result['cashbook'] is None:
                    result['cashbook'] = result['cashbooks'][0]

            recons = Recon2.search([
                ('cashbook', '=', result['cashbook']),
                ], order=[('date_from', 'DESC')])
            if len(recons) > 0:
                result['reconciliations'] = [x.id for x in recons]
                result['reconciliation'] = recons[0].id
        return result

    def do_report_(self, action):
        """ run report
        """
        # values for 'data' in report
        if self.selrecon.reconciliation:
            r1 = {
                'model': self.selrecon.reconciliation.__name__,
                'id': self.selrecon.reconciliation.id,
                'ids': [self.selrecon.reconciliation.id],
                }
        else:
            r1 = {'model': '', 'id': None, 'ids': []}
        return action, r1

    def transition_report_(self):
        return 'end'

# end RunCbReport
