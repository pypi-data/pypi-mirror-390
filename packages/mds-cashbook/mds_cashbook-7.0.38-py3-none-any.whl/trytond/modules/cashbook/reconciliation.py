# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import Workflow, ModelView, ModelSQL, fields, Index
from trytond.pyson import Eval, If, Or
from trytond.pool import Pool
from trytond.report import Report
from trytond.exceptions import UserError
from trytond.i18n import gettext
from decimal import Decimal
from datetime import timedelta
from .book import sel_state_book


sel_reconstate = [
    ('edit', 'Edit'),
    ('check', 'Check'),
    ('done', 'Done'),
    ]

STATES = {
    'readonly': Or(
            Eval('state', '') != 'edit',
            Eval('state_cashbook', '') != 'open',
        ),
    }
DEPENDS = ['state', 'state_cashbook']


class Reconciliation(Workflow, ModelSQL, ModelView):
    'Cashbook Reconciliation'
    __name__ = 'cashbook.recon'

    cashbook = fields.Many2One(
        string='Cashbook', required=True,
        model_name='cashbook.book', ondelete='CASCADE', readonly=True)
    date = fields.Date(
        string='Date', required=True,
        states=STATES, depends=DEPENDS)
    feature = fields.Function(fields.Char(
        string='Feature', readonly=True,
        states={'invisible': True}), 'on_change_with_feature')

    date_from = fields.Date(
        string='Start Date',
        required=True,
        domain=[
            If(Eval('date_to') & Eval('date_from'),
                ('date_from', '<=', Eval('date_to')),
                ()),
            ],
        states=STATES, depends=DEPENDS+['date_to'])
    date_to = fields.Date(
        string='End Date',
        required=True,
        domain=[
            If(Eval('date_to') & Eval('date_from'),
                ('date_from', '<=', Eval('date_to')),
                ()),
            ],
        states=STATES, depends=DEPENDS+['date_from'])
    start_amount = fields.Numeric(
        string='Start Amount', required=True,
        readonly=True, digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'])
    end_amount = fields.Numeric(
        string='End Amount', required=True,
        readonly=True, digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits'])

    lines = fields.One2Many(
        string='Lines', field='reconciliation',
        model_name='cashbook.line', states=STATES,
        depends=DEPENDS+['date_from', 'date_to', 'cashbook'],
        add_remove=[
            ('cashbook', '=', Eval('cashbook')),
            ('state', 'in', ['check', 'recon', 'done']),
            ('date', '>=', Eval('date_from')),
            ('date', '<=', Eval('date_to')),
        ],
        domain=[
            ('date', '>=', Eval('date_from', None)),
            ('date', '<=', Eval('date_to', None)),
        ])

    currency = fields.Function(fields.Many2One(
        model_name='currency.currency',
        string="Currency"), 'on_change_with_currency')
    currency_digits = fields.Function(fields.Integer(
        string='Currency Digits'),
        'on_change_with_currency_digits')
    predecessor = fields.Function(fields.Many2One(
        string='Predecessor', readonly=True,
        model_name='cashbook.recon'),
        'on_change_with_predecessor')

    state = fields.Selection(
        string='State', required=True, readonly=True,
        selection=sel_reconstate)
    state_string = state.translated('state')
    state_cashbook = fields.Function(fields.Selection(
        string='State of Cashbook',
        readonly=True, states={'invisible': True}, selection=sel_state_book),
        'on_change_with_state_cashbook')

    @classmethod
    def __setup__(cls):
        super(Reconciliation, cls).__setup__()
        cls._order.insert(0, ('date_from', 'DESC'))
        t = cls.__table__()
        cls._transitions |= set((
                ('edit', 'check'),
                ('check', 'done'),
                ('check', 'edit'),
            ))
        cls._buttons.update({
            'wfedit': {
                'invisible': Eval('state', '') != 'check',
                'depends': ['state'],
                },
            'wfcheck': {
                'invisible': Eval('state') != 'edit',
                'depends': ['state'],
                },
            'wfdone': {
                'invisible': Eval('state') != 'check',
                'depends': ['state'],
                },
            })
        cls._sql_indexes.update({
            Index(
                t,
                (t.cashbook, Index.Equality())),
            Index(
                t,
                (t.date, Index.Range())),
            Index(
                t,
                (t.date_to, Index.Range())),
            Index(
                t,
                (t.date_from, Index.Range(order='DESC'))),
            Index(
                t,
                (t.state, Index.Equality())),
            })

    def check_overlap_dates(self):
        """ deny overlap of date_from/date_to between records of same cashbook
            allow: date_to=date_from
        """
        Recon = Pool().get('cashbook.recon')

        query = [
                ('cashbook.id', '=', self.cashbook.id),
                ('id', '!=', self.id),
                ['OR',
                    [   # 'start' is inside of other record
                        ('date_from', '<=', self.date_from),
                        ('date_to', '>', self.date_from),
                    ],
                    [   # 'end' is inside of other record
                        ('date_from', '<', self.date_to),
                        ('date_to', '>=', self.date_to),
                    ],
                    [   # enclose other record
                        ('date_from', '>=', self.date_from),
                        ('date_to', '<=', self.date_to),
                    ]]]

        if Recon.search_count(query) > 0:
            raise UserError(gettext('cashbook.msg_recon_err_overlap'))

    @classmethod
    def check_lines_not_checked(cls, reconciliations):
        """ deny lines in date-range not 'checked', w/o records at date-limit
        """
        Line = Pool().get('cashbook.line')

        for reconciliation in reconciliations:
            if Line.search_count([
                    ('date', '>', reconciliation.date_from),
                    ('date', '<', reconciliation.date_to),
                    ('cashbook', '=', reconciliation.cashbook.id),
                    ('state', 'not in', ['check', 'recon']),
                    ]) > 0:
                raise UserError(gettext(
                    'cashbook.mds_recon_deny_line_not_check',
                    bookname=reconciliation.cashbook.rec_name,
                    reconame=reconciliation.rec_name,
                    datefrom=Report.format_date(reconciliation.date_from),
                    dateto=Report.format_date(reconciliation.date_to)))

    @classmethod
    def get_values_wfedit(cls, reconciliation):
        """ get values for 'to_write' in wf-edit
        """
        values = {
            'start_amount': Decimal('0.0'),
            'end_amount': Decimal('0.0'),
            }

        # unlink lines from reconciliation
        if len(reconciliation.lines) > 0:
            values['lines'] = [
                ('remove', [x.id for x in reconciliation.lines])]
        return values

    @classmethod
    def get_values_wfcheck(cls, reconciliation):
        """ get values for 'to_write' in wf-check
        """
        Line = Pool().get('cashbook.line')

        values = {}
        if reconciliation.predecessor:
            values['start_amount'] = reconciliation.predecessor.end_amount
        else:
            values['start_amount'] = Decimal('0.0')
        values['end_amount'] = values['start_amount']

        # add 'checked'-lines to reconciliation
        lines = Line.search([
            ('date', '>=', reconciliation.date_from),
            ('date', '<=', reconciliation.date_to),
            ('cashbook', '=', reconciliation.cashbook.id),
            ('reconciliation', '=', None),
            ('state', 'in', ['check', 'recon']),
            ])
        if len(lines) > 0:
            values['lines'] = [('add', [x.id for x in lines])]

        # add amounts of new lines
        values['end_amount'] += sum([x.credit - x.debit for x in lines])
        # add amounts of already linked lines
        values['end_amount'] += sum([
            x.credit - x.debit for x in reconciliation.lines])
        return values

    @classmethod
    @ModelView.button
    @Workflow.transition('edit')
    def wfedit(cls, reconciliations):
        """ edit
        """
        Recon = Pool().get('cashbook.recon')

        to_write = []
        for reconciliation in reconciliations:
            to_write.extend([
                [reconciliation],
                cls.get_values_wfedit(reconciliation),
                ])

        if len(to_write) > 0:
            Recon.write(*to_write)

    @classmethod
    @ModelView.button
    @Workflow.transition('check')
    def wfcheck(cls, reconciliations):
        """ checked: add lines of book in date-range to reconciliation,
            state of lines must be 'checked'
        """
        Recon = Pool().get('cashbook.recon')

        cls.check_lines_not_checked(reconciliations)

        to_write = []
        for reconciliation in reconciliations:
            if reconciliation.predecessor:
                # predecessor must be 'done'
                if reconciliation.predecessor.state != 'done':
                    raise UserError(gettext(
                        'cashbook.msg_recon_predecessor_not_done',
                        recname_p=reconciliation.predecessor.rec_name,
                        recname_c=reconciliation.rec_name))

                # check if current.date_from == predecessor.date_to
                if reconciliation.predecessor.date_to != \
                        reconciliation.date_from:
                    raise UserError(gettext(
                        'cashbook.msg_recon_date_from_to_mismatch',
                        datefrom=Report.format_date(reconciliation.date_from),
                        dateto=Report.format_date(
                            reconciliation.predecessor.date_to),
                        recname=reconciliation.rec_name))

            to_write.extend([
                [reconciliation],
                cls.get_values_wfcheck(reconciliation),
                ])

        if len(to_write) > 0:
            Recon.write(*to_write)

    @classmethod
    @ModelView.button
    @Workflow.transition('done')
    def wfdone(cls, reconciliations):
        """ is done
        """
        Line = Pool().get('cashbook.line')

        to_wfdone_line = []
        to_wfrecon_line = []
        for reconciliation in reconciliations:
            to_wfrecon_line.extend([
                    x for x in reconciliation.lines
                    if x.state == 'check'])
            to_wfdone_line.extend([
                    x for x in reconciliation.lines
                    if x.state == 'recon'])

            # deny if there are lines not linked to reconciliation
            if Line.search_count([
                    ('cashbook', '=', reconciliation.cashbook.id),
                    ('reconciliation', '=', None),
                    ['OR',
                        [   # lines inside of date-range
                            ('date', '>', reconciliation.date_from),
                            ('date', '<', reconciliation.date_to),
                        ],
                        # lines at from-date must relate to a reconciliation
                        ('date', '=', reconciliation.date_from)],
                    ]) > 0:
                raise UserError(gettext(
                    'cashbook.msg_recon_lines_no_linked',
                    date_from=Report.format_date(reconciliation.date_from),
                    date_to=Report.format_date(reconciliation.date_to),))

        if len(to_wfrecon_line) > 0:
            Line.wfrecon(to_wfrecon_line)
            to_wfdone_line.extend(to_wfrecon_line)
        if len(to_wfdone_line) > 0:
            Line.wfdone(to_wfdone_line)

    def get_rec_name(self, name):
        """ short + name
        """
        return ' '.join([
            Report.format_date(self.date_from, None)
            if self.date_from is not None else '-',
            '-',
            Report.format_date(self.date_to, None)
                if self.date_to is not None else '-',
            '|',
            Report.format_number(
                self.start_amount or 0.0, None,
                digits=getattr(self.currency, 'digits', 2)),
            getattr(self.currency, 'symbol', '-'),
            '-',
            Report.format_number(
                self.end_amount or 0.0, None,
                digits=getattr(self.currency, 'digits', 2)),
            getattr(self.currency, 'symbol', '-'),
            '[%(num)s]' % {'num': len(self.lines)},
            ])

    @classmethod
    def default_date_from(cls):
        """ 1st day of current month
        """
        return Pool().get('ir.date').today().replace(day=1)

    @classmethod
    def default_date_to(cls):
        """ last day of current month
        """
        IrDate = Pool().get('ir.date')

        dt1 = IrDate.today().replace(day=28) + timedelta(days=5)
        dt1 = dt1.replace(day=1) - timedelta(days=1)
        return dt1

    @classmethod
    def default_start_amount(cls):
        return Decimal('0.0')

    @classmethod
    def default_end_amount(cls):
        return Decimal('0.0')

    @classmethod
    def default_state(cls):
        return 'edit'

    @classmethod
    def default_date(cls):
        """ today
        """
        IrDate = Pool().get('ir.date')
        return IrDate.today()

    @fields.depends('cashbook', '_parent_cashbook.btype')
    def on_change_with_feature(self, name=None):
        """ get feature-set
        """
        if self.cashbook:
            return self.cashbook.btype.feature

    @fields.depends('cashbook', '_parent_cashbook.id', 'date_from')
    def on_change_with_predecessor(self, name=None):
        """ get predecessor
        """
        Recon = Pool().get('cashbook.recon')

        if self.cashbook:
            if self.date_from is not None:
                reconciliations = Recon.search([
                        ('cashbook', '=', self.cashbook.id),
                        ('date_from', '<', self.date_from),
                    ], order=[('date_from', 'DESC')], limit=1)
                if len(reconciliations) > 0:
                    return reconciliations[0].id

    @fields.depends('cashbook', '_parent_cashbook.currency')
    def on_change_with_currency(self, name=None):
        """ currency of cashbook
        """
        if self.cashbook:
            return self.cashbook.currency.id

    @fields.depends('cashbook', '_parent_cashbook.currency')
    def on_change_with_currency_digits(self, name=None):
        """ currency-digits of cashbook
        """
        if self.cashbook:
            return self.cashbook.currency.digits
        else:
            return 2

    @fields.depends('cashbook', '_parent_cashbook.state')
    def on_change_with_state_cashbook(self, name=None):
        """ get state of cashbook
        """
        if self.cashbook:
            return self.cashbook.state

    @classmethod
    def validate(cls, reconciliations):
        """ deny overlap of dates
        """
        super(Reconciliation, cls).validate(reconciliations)

        for reconciliation in reconciliations:
            reconciliation.check_overlap_dates()

    @classmethod
    def create(cls, vlist):
        """ add debit/credit
        """
        pool = Pool()
        Recon = pool.get('cashbook.recon')
        Line = pool.get('cashbook.line')
        Cashbook = pool.get('cashbook.book')

        for values in vlist:
            id_cashbook = values.get('cashbook', -1)

            # set date_from to date_to of predecessor
            recons = Recon.search([
                ('cashbook', '=', id_cashbook),
                ], order=[('date_to', 'DESC')], limit=1)
            if len(recons) > 0:
                values['date_from'] = recons[0].date_to
            elif id_cashbook != -1:
                values['date_from'] = Cashbook(id_cashbook).start_date

            # set date_to to day of last 'checked'-booking in selected cashbook
            lines = Line.search([
                ('cashbook', '=', id_cashbook),
                ('state', '=', 'check'),
                ('reconciliation', '=', None),
                ], order=[('date', 'DESC')], limit=1)
            if len(lines) > 0:
                values['date_to'] = lines[0].date

        return super(Reconciliation, cls).create(vlist)

    @classmethod
    def write(cls, *args):
        """ deny update if cashbook.line!='open',
            add or update debit/credit
        """
        actions = iter(args)
        for reconciliations, values in zip(actions, actions):
            # deny write if chashbook is not open
            for reconciliation in reconciliations:
                if reconciliation.cashbook.state != 'open':
                    raise UserError(gettext(
                        'cashbook.msg_book_deny_write',
                        bookname=reconciliation.cashbook.rec_name,
                        state_txt=reconciliation.cashbook.state_string))
        super(Reconciliation, cls).write(*args)

    @classmethod
    def delete(cls, reconciliations):
        """ deny delete if book is not 'open' or wf is not 'edit'
        """
        for reconciliation in reconciliations:
            if reconciliation.cashbook.state == 'closed':
                raise UserError(gettext(
                    'cashbook.msg_line_deny_delete1',
                    linetxt=reconciliation.rec_name,
                    bookname=reconciliation.cashbook.rec_name,
                    bookstate=reconciliation.cashbook.state_string))
            if reconciliation.state != 'edit':
                raise UserError(gettext(
                    'cashbook.msg_recon_deny_delete2',
                    recontxt=reconciliation.rec_name,
                    reconstate=reconciliation.state_string))

        super(Reconciliation, cls).delete(reconciliations)

# end Type
