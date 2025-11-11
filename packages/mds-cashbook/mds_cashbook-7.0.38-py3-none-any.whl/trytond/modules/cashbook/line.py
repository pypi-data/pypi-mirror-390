# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, Workflow, fields, Check, Index
from trytond.pool import Pool
from trytond.pyson import Eval, If, Or, Bool, Date
from trytond.transaction import Transaction
from trytond.report import Report
from trytond.exceptions import UserError
from trytond.i18n import gettext
from decimal import Decimal
from sql import Literal
from sql.functions import DatePart
from sql.conditionals import Case
from .book import sel_state_book
from .mixin import SecondCurrencyMixin
from .const import DEF_NONE


sel_payee = [
    ('cashbook.book', 'Cashbook'),
    ('party.party', 'Party')
    ]

sel_linestate = [
    ('edit', 'Edit'),
    ('check', 'Checked'),
    ('recon', 'Reconciled'),
    ('done', 'Done'),
    ]

sel_bookingtype = [
    ('in', 'Revenue'),
    ('out', 'Expense'),
    ('spin', 'Revenue Splitbooking'),
    ('spout', 'Expense Splitbooking'),
    ('mvin', 'Transfer from'),
    ('mvout', 'Transfer to'),
    ]

STATES = {
    'readonly': Or(
            Eval('state', '') != 'edit',
            Eval('state_cashbook', '') != 'open',
        ),
    }
DEPENDS = ['state', 'state_cashbook']


class Line(SecondCurrencyMixin, Workflow, ModelSQL, ModelView):
    'Cashbook Line'
    __name__ = 'cashbook.line'

    cashbook = fields.Many2One(
        string='Cashbook', required=True,
        model_name='cashbook.book', ondelete='CASCADE', readonly=True,
        domain=[('btype', '!=', None)])
    date = fields.Date(
        string='Date', required=True,
        states=STATES, depends=DEPENDS)
    month = fields.Function(fields.Integer(
        string='Month', readonly=True),
        'on_change_with_month', searcher='search_month')
    number = fields.Char(string='Number', readonly=True)
    description = fields.Text(
        string='Description',
        states=STATES, depends=DEPENDS)
    descr_short = fields.Function(fields.Char(
        string='Description', readonly=True),
        'on_change_with_descr_short', searcher='search_descr_short')
    category = fields.Many2One(
        string='Category',
        model_name='cashbook.category', ondelete='RESTRICT',
        states={
            'readonly': Or(
                STATES['readonly'],
                ~Bool(Eval('bookingtype'))),
            'required': Eval('bookingtype', '').in_(['in', 'out']),
            'invisible': ~Eval('bookingtype', '').in_(['in', 'out']),
        }, depends=DEPENDS+['bookingtype'],
        domain=[
            If(
                Eval('bookingtype', '').in_(['in', 'mvin']),
                ('cattype', '=', 'in'),
                ('cattype', '=', 'out'),
            )])
    category_view = fields.Function(fields.Char(
        string='Category', readonly=True),
        'on_change_with_category_view', searcher='search_category_view')
    feature = fields.Function(fields.Char(
        string='Feature', readonly=True,
        states={'invisible': True}), 'on_change_with_feature')
    booktransf_feature = fields.Function(fields.Char(
        string='Feature', readonly=True,
        states={'invisible': True}), 'on_change_with_booktransf_feature')

    bookingtype = fields.Selection(
        string='Type', required=True,
        help='Type of Booking', selection=sel_bookingtype,
        states=STATES, depends=DEPENDS)
    bookingtype_string = bookingtype.translated('bookingtype')
    amount = fields.Numeric(
        string='Amount', digits=(16, Eval('currency_digits', 2)),
        required=True,
        states={
            'readonly': Or(
                STATES['readonly'],
                Eval('bookingtype', '').in_(['spin', 'spout']),
                ),
        }, depends=DEPENDS+['currency_digits', 'bookingtype'])
    debit = fields.Numeric(
        string='Debit', digits=(16, Eval('currency_digits', 2)),
        required=True, readonly=True, depends=['currency_digits'])
    credit = fields.Numeric(
        string='Credit', digits=(16, Eval('currency_digits', 2)),
        required=True, readonly=True, depends=['currency_digits'])

    # party or cashbook as counterpart
    booktransf = fields.Many2One(
        string='Source/Dest',
        ondelete='RESTRICT', model_name='cashbook.book',
        domain=[
            ('owner.id', '=', Eval('owner_cashbook', -1)),
            ('id', '!=', Eval('cashbook', -1)),
            ('btype', '!=', None),
            ],
        states={
            'readonly': STATES['readonly'],
            'invisible': ~Eval('bookingtype', '').in_(['mvin', 'mvout']),
            'required': Eval('bookingtype', '').in_(['mvin', 'mvout']),
        }, depends=DEPENDS+['bookingtype', 'owner_cashbook', 'cashbook'])
    party = fields.Many2One(
        string='Party', model_name='party.party',
        ondelete='RESTRICT',
        states={
            'readonly': STATES['readonly'],
            'invisible': ~Eval('bookingtype', '').in_(
                ['in', 'out', 'spin', 'spout']),
        }, depends=DEPENDS+['bookingtype'])
    payee = fields.Function(fields.Reference(
        string='Payee', readonly=True,
        selection=sel_payee), 'on_change_with_payee', searcher='search_payee')

    # link to lines created by this record
    reference = fields.Many2One(
        string='Reference', readonly=True,
        states={
            'invisible': ~Bool(Eval('reference')),
        }, model_name='cashbook.line', ondelete='CASCADE',
        help='The current row was created by and is controlled ' +
        'by the reference row.')
    references = fields.One2Many(
        string='References',
        model_name='cashbook.line',
        help='The rows are created and managed by the current record.',
        states={
            'invisible': ~Bool(Eval('references')),
        }, field='reference', readonly=True)
    splitlines = fields.One2Many(
        string='Split booking lines',
        model_name='cashbook.split',
        help='Rows with different categories form the total ' +
        'sum of the booking',
        states={
            'invisible': ~Eval('bookingtype' '').in_(['spin', 'spout']),
            'readonly': Or(
                ~Eval('bookingtype' '').in_(['spin', 'spout']),
                STATES['readonly'],
                ),
            'required': Eval('bookingtype' '').in_(['spin', 'spout']),
        }, field='line', depends=DEPENDS+['bookingtype'])

    reconciliation = fields.Many2One(
        string='Reconciliation', readonly=True,
        model_name='cashbook.recon', ondelete='SET NULL',
        domain=[('cashbook.id', '=', Eval('cashbook', -1))],
        depends=['cashbook'],
        states={
            'invisible': ~Bool(Eval('reconciliation')),
        })

    balance = fields.Function(fields.Numeric(
        string='Balance',
        digits=(16, Eval('currency_digits', 2)),
        help='Balance of the cash book up to the current line, ' +
        'if the default sorting applies.',
        readonly=True, depends=['currency_digits']),
        'on_change_with_balance')

    currency = fields.Function(fields.Many2One(
        model_name='currency.currency',
        string="Currency", readonly=True), 'on_change_with_currency')
    currency_digits = fields.Function(fields.Integer(
        string='Currency Digits',
        readonly=True), 'on_change_with_currency_digits')

    state = fields.Selection(
        string='State', required=True, readonly=True,
        selection=sel_linestate)
    state_string = state.translated('state')
    state_cashbook = fields.Function(fields.Selection(
        string='State of Cashbook',
        readonly=True, states={'invisible': True}, selection=sel_state_book),
        'on_change_with_state_cashbook', searcher='search_state_cashbook')
    owner_cashbook = fields.Function(fields.Many2One(
        string='Owner', readonly=True,
        states={'invisible': True}, model_name='res.user'),
        'on_change_with_owner_cashbook')

    @classmethod
    def __register__(cls, module_name):
        super(Line, cls).__register__(module_name)

        table = cls.__table_handler__(module_name)
        table.drop_constraint('amount_val')
        table.drop_constraint('state_val')
        cls.migrate_amount_2nd_currency()

    @classmethod
    def __setup__(cls):
        super(Line, cls).__setup__()
        cls._order.insert(0, ('date', 'ASC'))
        cls._order.insert(0, ('state', 'ASC'))
        t = cls.__table__()

        cls._sql_indexes.update({
            Index(
                t,
                (t.date, Index.Range(order='ASC'))),
            Index(
                t,
                (t.description, Index.Similarity())),
            Index(
                t,
                (t.category, Index.Equality())),
            Index(
                t,
                (t.bookingtype, Index.Equality())),
            Index(
                t,
                (t.state, Index.Equality())),
            Index(
                t,
                (t.reference, Index.Equality())),
            })
        cls._sql_constraints.extend([
            ('state_val2',
                Check(t, t.state.in_(['edit', 'check', 'done', 'recon'])),
                'cashbook.msg_line_wrong_state_value'),
            ])
        cls._transitions |= set((
                ('edit', 'check'),
                ('check', 'recon'),
                ('recon', 'done'),
                ('check', 'edit'),
            ))
        cls._buttons.update({
            'wfedit': {
                'invisible': Eval('state', '') != 'check',
                'readonly': Bool(Eval('reference')),
                'depends': ['state', 'reference'],
                },
            'wfcheck': {
                'invisible': Eval('state') != 'edit',
                'depends': ['state'],
                },
            'wfrecon': {
                'invisible': Eval('state') != 'check',
                'depends': ['state'],
                },
            'wfdone': {
                'invisible': Eval('state') != 'recon',
                'depends': ['state'],
                },
            })

    @classmethod
    def view_attributes(cls):
        return super().view_attributes() + [
            ('/tree', 'visual',
                If(Eval('balance', 0) < 0, 'warning',
                    If(Eval('date', Date()) > Date(), 'muted', ''))),
            ]

    @classmethod
    def migrate_amount_2nd_currency(cls):
        """ add amount-2nd-currency
        """
        pool = Pool()
        Line2 = pool.get('cashbook.line')
        Book = pool.get('cashbook.book')
        Book2 = pool.get('cashbook.book')
        tab_line = Line2.__table__()
        tab_book = Book.__table__()         # cashbook of line
        tab_book2 = Book2.__table__()       # transfer-target
        cursor = Transaction().connection.cursor()

        query = tab_line.join(
                tab_book,
                condition=tab_line.cashbook == tab_book.id,
            ).join(
                tab_book2,
                condition=tab_line.booktransf == tab_book2.id,
            ).select(
                tab_line.id,
                where=tab_line.bookingtype.in_(['mvin', 'mvout']) &
                    (tab_line.amount_2nd_currency == DEF_NONE) &
                    (tab_book.currency != tab_book2.currency)
            )
        lines = Line2.search([('id', 'in', query)])
        to_write = []
        for line in lines:
            values = Line2.add_2nd_currency({
                'date': line.date,
                'booktransf': line.booktransf.id,
                'amount': line.amount,
                }, line.currency)
            if 'amount_2nd_currency' in values.keys():
                values['id'] = line.id
                to_write.append(values)

        for line in to_write:
            qu1 = tab_line.update(
                    columns=[tab_line.amount_2nd_currency],
                    values=[line['amount_2nd_currency']],
                    where=tab_line.id == line['id'],
                )
            cursor.execute(*qu1)

    @classmethod
    @ModelView.button
    @Workflow.transition('edit')
    def wfedit(cls, lines):
        """ edit line
        """
        pool = Pool()
        Line2 = pool.get('cashbook.line')

        to_delete_line = []
        for line in lines:
            if line.reference:
                if Transaction().context.get(
                        'line.allow.wfedit', False) is False:
                    raise UserError(gettext(
                        'cashbook.msg_line_denywf_by_reference',
                        recname=line.reference.rec_name,
                        cbook=line.reference.cashbook.rec_name))
            # delete references
            to_delete_line.extend(list(line.references))

        if len(to_delete_line) > 0:
            with Transaction().set_context({
                    'line.allow.wfedit': True}):
                Line2.wfedit(to_delete_line)
            Line2.delete(to_delete_line)

    @classmethod
    @ModelView.button
    @Workflow.transition('check')
    def wfcheck(cls, lines):
        """ line is checked
        """
        pool = Pool()
        Recon = pool.get('cashbook.recon')
        Line2 = pool.get('cashbook.line')

        to_create_line = []
        to_write_line = []
        for line in lines:
            # deny if date is in range of existing reconciliation
            # allow cashbook-line at range-limits
            if Recon.search_count([
                    ('state', 'in', ['check', 'done']),
                    ('cashbook', '=', line.cashbook.id),
                    ('date_from', '<', line.date),
                    ('date_to', '>', line.date)]) > 0:
                raise UserError(gettext(
                    'cashbook.msg_line_err_write_to_reconciled',
                    datetxt=Report.format_date(line.date),
                    ))
            # deny if date is at reconciliation limits and two
            # reconciliations exist
            if Recon.search_count([
                    ('state', 'in', ['check', 'done']),
                    ('cashbook', '=', line.cashbook.id),
                    ['OR',
                        ('date_from', '=', line.date),
                        ('date_to', '=', line.date)]]) > 1:
                raise UserError(gettext(
                    'cashbook.msg_line_err_write_to_reconciled',
                    datetxt=Report.format_date(line.date),
                    ))

            if line.reference is None:
                if line.bookingtype in ['mvout', 'mvin']:
                    # in case of 'mvin' or 'mvout' - add counterpart
                    values = cls.get_counterpart_values(line)
                    values.update(cls.get_debit_credit(values))
                    to_create_line.append(values)
                elif line.bookingtype in ['spout', 'spin']:
                    # splitbooking can have a transfer - add counterpart
                    for sp_line in line.splitlines:
                        if sp_line.splittype != 'tr':
                            continue

                        values = cls.get_counterpart_values(
                            line, splitline=sp_line,
                            values={
                                'cashbook': sp_line.booktransf.id,
                                'description': sp_line.description,
                                'amount': sp_line.amount
                                if sp_line.currency.id == sp_line.
                                booktransf.currency.id
                                else sp_line.amount_2nd_currency,
                                'amount_2nd_currency': sp_line.amount
                                if sp_line.currency.id != sp_line.
                                booktransf.currency.id
                                else None,
                                'bookingtype': 'mvin'
                                if line.bookingtype.endswith('out')
                                else 'mvout',
                            })
                        values.update(cls.get_debit_credit(values))
                        to_create_line.append(values)

            # add number to line
            if line.cashbook.number_atcheck is True:
                if len(line.number or '') == 0:
                    to_write_line.extend([
                        [line],
                        {
                            'number': line.cashbook.number_sequ.get()
                        }])

        if len(to_write_line) > 0:
            Line2.write(*to_write_line)

        if len(to_create_line) > 0:
            new_lines = Line2.create(to_create_line)
            Line2.wfcheck(new_lines)

    @classmethod
    @ModelView.button
    @Workflow.transition('recon')
    def wfrecon(cls, lines):
        """ line is reconciled
        """
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('done')
    def wfdone(cls, lines):
        """ line is done
        """
        Line2 = Pool().get('cashbook.line')

        to_write_line = []
        for line in lines:
            # add number to line
            if len(line.number or '') == 0:
                to_write_line.extend([
                    [line],
                    {
                        'number': line.cashbook.number_sequ.get()
                    }])

        if len(to_write_line) > 0:
            Line2.write(*to_write_line)

    @classmethod
    def default_state(cls):
        """ default: edit
        """
        return 'edit'

    @classmethod
    def default_date(cls):
        """ default: today
        """
        IrDate = Pool().get('ir.date')
        return IrDate.today()

    @classmethod
    def default_cashbook(cls):
        """ get default from context
        """
        context = Transaction().context
        return context.get('cashbook', None)

    @classmethod
    def search_rec_name(cls, name, clause):
        """ search in description +...
        """
        return cls.search_payee(name, clause) + [
            ('description',) + tuple(clause[1:]),
            ('category.rec_name',) + tuple(clause[1:]),
            ('splitlines.description',) + tuple(clause[1:]),
            ('splitlines.category.rec_name',) + tuple(clause[1:]),
            ]

    def get_rec_name(self, name):
        """ short + name
        """
        credit = self.credit if self.credit is not None else Decimal('0.0')
        debit = self.debit if self.debit is not None else Decimal('0.0')
        return '|'.join([
            Report.format_date(self.date),
            gettext('cashbook.msg_line_bookingtype_%s' % self.bookingtype),
            '%(amount)s %(symbol)s' % {
                'amount': Report.format_number(
                    credit - debit, None,
                    digits=getattr(self.currency, 'digits', 2)),
                'symbol': getattr(self.currency, 'symbol', '-')},
            '%(desc)s [%(category)s]' % {
                'desc': (self.description or '-')[:40],
                'category': self.category_view
                if self.bookingtype in ['in', 'out']
                else getattr(self.booktransf, 'rec_name', '-')},
            ])

    @staticmethod
    def order_state(tables):
        """ edit = 0, check/done = 1
        """
        Line = Pool().get('cashbook.line')
        tab_line = Line.__table__()
        table, _ = tables[None]

        query = tab_line.select(
                Case(
                    (tab_line.state == 'edit', 1),
                    (tab_line.state.in_(['check', 'recon', 'done']), 0),
                    else_=2),
                where=tab_line.id == table.id)
        return [query]

    @staticmethod
    def order_category_view(tables):
        """ order: name
        """
        table, _ = tables[None]
        Category = Pool().get('cashbook.category')
        tab_cat = Category.__table__()

        tab2 = tab_cat.select(
            tab_cat.name,
            where=tab_cat.id == table.category)
        return [tab2]

    @staticmethod
    def order_descr_short(tables):
        """ order by 'description'
        """
        table, _ = tables[None]
        return [table.description]

    @classmethod
    def search_payee(cls, names, clause):
        """ search in payee for party or cashbook
        """
        return ['OR',
                ('party.rec_name',) + tuple(clause[1:]),
                ('booktransf.rec_name',) + tuple(clause[1:])]

    @classmethod
    def search_category_view(cls, name, clause):
        """ search in category
        """
        return [('category.rec_name',) + tuple(clause[1:])]

    @classmethod
    def search_month(cls, names, clause):
        """ search in month
        """
        pool = Pool()
        Line = pool.get('cashbook.line')
        IrDate = pool.get('ir.date')
        tab_line = Line.__table__()
        Operator = fields.SQL_OPERATORS[clause[1]]

        dt1 = IrDate.today()
        query = tab_line.select(
            tab_line.id,
            where=Operator(
                Literal(12 * dt1.year + dt1.month) -
                (Literal(12) * DatePart('year', tab_line.date) +
                    DatePart('month', tab_line.date)),
                clause[2]),
            )
        return [('id', 'in', query)]

    @classmethod
    def search_state_cashbook(cls, names, clause):
        """ search in state of cashbook
        """
        return [('cashbook.state',) + tuple(clause[1:])]

    @classmethod
    def search_descr_short(cls, names, clause):
        """ search in description
        """
        return [('description',) + tuple(clause[1:])]

    @fields.depends('amount', 'splitlines')
    def on_change_splitlines(self):
        """ update amount if splitlines change
        """
        self.amount = sum([
            x.amount for x in self.splitlines if x.amount is not None])

    @fields.depends(
        'bookingtype', 'category', 'splitlines', 'booktransf',
        'currency2nd')
    def on_change_bookingtype(self):
        """ clear category if not valid type
        """
        types = {
            'in': ['in', 'mvin', 'spin'],
            'out': ['out', 'mvout', 'spout'],
            }

        if self.bookingtype:
            if self.category:
                if self.bookingtype not in types.get(
                        self.category.cattype, ''):
                    self.category = None

            if self.bookingtype.startswith('sp'):   # split booking
                self.category = None
                self.booktransf = None
                for spline in self.splitlines:
                    if self.bookingtype not in types.get(
                            getattr(spline.category, 'cattype', '-'), ''):
                        spline.category = None
            elif self.bookingtype.startswith('mv'):     # transfer
                self.splitlines = []
                self.category = None
            else:                                       # category
                self.splitlines = []
                self.booktransf = None
            self.currency2nd = self.on_change_with_currency2nd()

    @fields.depends('cashbook', '_parent_cashbook.btype')
    def on_change_with_feature(self, name=None):
        """ get feature-set
        """
        if self.cashbook:
            return self.cashbook.btype.feature

    @fields.depends('booktransf', '_parent_booktransf.feature')
    def on_change_with_booktransf_feature(self, name=None):
        """ get 'feature' of counterpart
        """
        if self.booktransf:
            if self.booktransf.btype:
                return self.booktransf.btype.feature

    @fields.depends('description')
    def on_change_with_descr_short(self, name=None):
        """ to speed up list-view
        """
        if self.description:
            return self.description[:50].replace('\n', '; ')

    @fields.depends('party', 'booktransf', 'bookingtype')
    def on_change_with_payee(self, name=None):
        """ get party or cashbook
        """
        if self.bookingtype:
            if self.bookingtype in ['in', 'out', 'spin', 'spout']:
                if self.party:
                    return 'party.party,%d' % self.party.id
            elif self.bookingtype in ['mvin', 'mvout']:
                if self.booktransf:
                    return 'cashbook.book,%d' % self.booktransf.id

    @fields.depends('category')
    def on_change_with_category_view(self, name=None):
        """ show optimized form of category for list-view
        """
        Configuration = Pool().get('cashbook.configuration')

        if self.category:
            cfg1 = Configuration.get_singleton()

            if getattr(cfg1, 'catnamelong', True) is True:
                return self.category.rec_name
            else:
                return self.category.name

    @fields.depends('date')
    def on_change_with_month(self, name=None):
        """ get difference of month to current date
        """
        IrDate = Pool().get('ir.date')
        if self.date is not None:
            dt1 = IrDate.today()
            return (12 * dt1.year + dt1.month) - \
                (12 * self.date.year + self.date.month)

    @fields.depends('cashbook', '_parent_cashbook.owner')
    def on_change_with_owner_cashbook(self, name=None):
        """ get current owner
        """
        if self.cashbook:
            return self.cashbook.owner.id

    @fields.depends('cashbook', '_parent_cashbook.state')
    def on_change_with_state_cashbook(self, name=None):
        """ get state of cashbook
        """
        if self.cashbook:
            return self.cashbook.state

    @fields.depends('cashbook', '_parent_cashbook.currency')
    def on_change_with_currency(self, name=None):
        """ currency of cashbook
        """
        if self.cashbook:
            return self.cashbook.currency.id

    @fields.depends('cashbook', '_parent_cashbook.currency')
    def on_change_with_currency_digits(self, name=None):
        """ currency of cashbook
        """
        if self.cashbook:
            return self.cashbook.currency.digits
        else:
            return 2

    @classmethod
    def get_balance_of_line(
            cls, line, field_name='amount', credit_name='credit',
            debit_name='debit'):
        """ get balance of current line,
            try to speed up by usage of last reconcilitaion
        """
        pool = Pool()
        Reconciliation = pool.get('cashbook.recon')
        Line2 = pool.get('cashbook.line')

        def get_from_last_recon(line2):
            """ search last reconciliation in state 'done',
                generate query
            """
            query2 = []
            end_value = None

            recons = Reconciliation.search([
                ('cashbook', '=', line.cashbook.id),
                ('date_to', '<=', line2.date),
                ('state', '=', 'done'),
                ], order=[('date_from', 'DESC')], limit=1)
            if len(recons) > 0:
                query2.append([
                        ('date', '>=', recons[0].date_to),
                        ('date', '<=', line2.date),
                        ['OR',
                            ('reconciliation', '=', None),
                            ('reconciliation', '!=', recons[0])],
                    ])
                end_value = getattr(recons[0], 'end_%s' % field_name)
            return (query2, end_value)

        if line.cashbook:
            query = [
                ('cashbook', '=', line.cashbook.id),
                ]
            balance = Decimal('0.0')

            # get existing reconciliation, starting before current line
            # this will speed up calculation of by-line-balance
            if line.date is not None:
                if line.reconciliation:
                    if line.reconciliation.state == 'done':
                        query.append(
                            ('reconciliation', '=', line.reconciliation.id),
                            )
                        balance = getattr(
                            line.reconciliation, 'start_%s' % field_name)
                    else:
                        (query2, balance2) = get_from_last_recon(line)
                        query.extend(query2)
                        if balance2 is not None:
                            balance = balance2
                else:
                    (query2, balance2) = get_from_last_recon(line)
                    query.extend(query2)
                    if balance2 is not None:
                        balance = balance2

            lines = Line2.search(query)
            for line3 in lines:
                line_credit = getattr(line3, credit_name)
                line_debit = getattr(line3, debit_name)

                if (line_credit is not None) or (line_debit is not None):
                    balance += line_credit - line_debit

                if line3.id == line.id:
                    break
            return balance

    @fields.depends(
        'id', 'date', 'cashbook', '_parent_cashbook.id', 'reconciliation',
        '_parent_reconciliation.start_amount', '_parent_reconciliation.state')
    def on_change_with_balance(self, name=None):
        """ compute balance until current line, with current sort order,
            try to use a reconciliation as start to speed up calculation
        """
        Line2 = Pool().get('cashbook.line')
        return Line2.get_balance_of_line(
            self, field_name='amount', credit_name='credit',
            debit_name='debit')

    @classmethod
    def clear_by_bookingtype(cls, values, line=None):
        """ clear some fields by value of bookingtype
        """
        values2 = {}
        values2.update(values)

        bookingtype = values2.get(
            'bookingtype', getattr(line, 'bookingtype', None))
        if (bookingtype in ['in', 'out', 'mvin', 'mvout']) and \
                ('splitlines' not in values2.keys()):
            if line:
                if len(line.splitlines) > 0:
                    values2['splitlines'] = [
                        ('delete', [x.id for x in line.splitlines])]

        if bookingtype in ['in', 'out']:
            values2['booktransf'] = None

        if bookingtype in ['spin', 'spout']:
            values2['category'] = None
            values2['booktransf'] = None

        if bookingtype in ['mvin', 'mvout']:
            values2['category'] = None
        return values2

    @classmethod
    def get_counterpart_values(cls, line, splitline=None, values={}):
        """ get values to create counter-part of
            transfer booking
        """
        line_currency = getattr(line.currency, 'id', None)
        booktransf_currency = getattr(getattr(
            line.booktransf, 'currency', {}), 'id', None)

        result = {
            'cashbook': getattr(line.booktransf, 'id', None),
            'bookingtype': 'mvin' if line.bookingtype == 'mvout' else 'mvout',
            'date': line.date,
            'description': line.description,
            'booktransf': line.cashbook.id,
            'reference': line.id,
            'amount': line.amount
            if line_currency == booktransf_currency
            else line.amount_2nd_currency,
            'amount_2nd_currency': line.amount
            if line_currency != booktransf_currency else None}
        # update values from 'values'
        result.update(values)
        return result

    @classmethod
    def get_debit_credit(cls, values, line=None):
        """ compute debit/credit from amount
        """
        if isinstance(values, dict):
            type_ = values.get(
                'bookingtype', getattr(line, 'bookingtype', None))
            amount = values.get('amount', None)
        else:
            type_ = getattr(
                values, 'bookingtype', getattr(line, 'bookingtype', None))
            amount = getattr(values, 'amount', None)

        result = {}
        if type_:
            if amount is not None:
                if type_ in ['in', 'mvin', 'spin']:
                    result.update({
                        'debit': Decimal('0.0'), 'credit': amount})
                elif type_ in ['out', 'mvout', 'spout']:
                    result.update({
                        'debit': amount, 'credit': Decimal('0.0')})
                else:
                    raise ValueError('invalid "bookingtype"')
        return result

    @classmethod
    def validate(cls, lines):
        """ deny date before 'start_date' of cashbook
        """
        super(Line, cls).validate(lines)

        types = {
            'in': ['in', 'mvin', 'spin'],
            'out': ['out', 'mvout', 'spout'],
            }

        for line in lines:
            if line.date < line.cashbook.start_date:
                raise UserError(gettext(
                    'cashbook.msg_line_date_before_book',
                    datebook=Report.format_date(line.cashbook.start_date),
                    recname=line.rec_name))

            # line: category <--> bookingtype?
            if line.category:
                if line.bookingtype not in types[line.category.cattype]:
                    raise UserError(gettext(
                        'cashbook.msg_line_invalid_category',
                        recname=line.rec_name,
                        booktype=line.bookingtype_string))

            # splitline: category <--> bookingtype?
            for spline in line.splitlines:
                if spline.splittype != 'cat':
                    continue
                if line.bookingtype not in types[spline.category.cattype]:
                    raise UserError(gettext(
                        'cashbook.msg_line_split_invalid_category',
                        recname=line.rec_name,
                        splitrecname=spline.rec_name,
                        booktype=line.bookingtype_string))

    @classmethod
    def check_permission_write(cls, lines, values={}):
        """ deny update if cashbook.line!='open',
        """
        for line in lines:
            # deny write if cashbook is not open
            if line.cashbook.state != 'open':
                raise UserError(gettext(
                    'cashbook.msg_book_deny_write',
                    bookname=line.cashbook.rec_name,
                    state_txt=line.cashbook.state_string))

            # deny write if reconciliation is 'check' or 'done'
            if line.reconciliation:
                if line.reconciliation.state == 'done':
                    raise UserError(gettext(
                        'cashbook.msg_line_deny_write_by_reconciliation',
                        recname=line.rec_name,
                        reconame=line.reconciliation.rec_name))

            # deny write if line is not 'Edit'
            if line.state != 'edit':
                # allow state-update, if its the only action
                if not ((len(set({
                            'state', 'reconciliation', 'number'
                        }).intersection(values.keys())) > 0)
                        and (len(values.keys()) == 1)):
                    raise UserError(gettext(
                        'cashbook.msg_line_deny_write',
                        recname=line.rec_name,
                        state_txt=line.state_string))

    @classmethod
    def check_permission_delete(cls, lines):
        """ deny delete if book is not 'open' or wf is not 'edit'
        """
        for line in lines:
            if line.cashbook.state == 'closed':
                raise UserError(gettext(
                    'cashbook.msg_line_deny_delete1',
                    linetxt=line.rec_name,
                    bookname=line.cashbook.rec_name,
                    bookstate=line.cashbook.state_string))
            if line.state != 'edit':
                raise UserError(gettext(
                    'cashbook.msg_line_deny_delete2',
                    linetxt=line.rec_name,
                    linestate=line.state_string))

    @classmethod
    def update_values_by_splitlines(cls, lines):
        """ update amounts from split-lines
        """
        to_write = []
        for line in lines:
            amount = sum([x.amount for x in line.splitlines])
            if amount != line.amount:
                to_write.extend([[line], {'amount': amount}])
        return to_write

    @classmethod
    def add_values_from_splitlines(cls, values):
        """ add values for create to line by settings on splitlines
        """
        if ('splitlines' in values.keys()) and ('amount' not in values.keys()):
            for action in values['splitlines']:
                if action[0] == 'create':
                    values['amount'] = sum([
                        x.get('amount', None) for x in action[1]])
        return values

    @classmethod
    def add_2nd_unit_values(cls, values):
        """ extend create-values
        """
        Cashbook = Pool().get('cashbook.book')
        cashbook = values.get('cashbook', None)
        if cashbook:
            values.update(cls.add_2nd_currency(
                values, Cashbook(cashbook).currency))
        return values

    @classmethod
    def get_fields_write_update(cls):
        """ get fields to update on write
        """
        return ['amount', 'bookingtype']

    @classmethod
    def copy(cls, lines, default=None):
        """ reset values
        """
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('number', None)
        default.setdefault('state', cls.default_state())
        return super(Line, cls).copy(lines, default=default)

    @classmethod
    def create(cls, vlist):
        """ add debit/credit
        """
        ValueStore = Pool().get('cashbook.values')

        vlist = [x.copy() for x in vlist]
        for values in vlist:
            values.update(cls.add_values_from_splitlines(values))
            values.update(cls.get_debit_credit(values))
            values.update(cls.clear_by_bookingtype(values))
            values.update(cls.add_2nd_unit_values(values))

            # deny add to reconciliation if state is
            # not 'check', 'recon' or 'done'
            if values.get('reconciliation', None):
                if not values.get('state', '-') in ['check', 'done', 'recon']:
                    date_txt = '-'
                    if values.get('date', None):
                        date_txt = Report.format_date(values.get('date', None))
                    raise UserError(gettext(
                        'cashbook.msg_line_deny_recon_by_state',
                        recname='%(date)s|%(descr)s' % {
                            'date': date_txt,
                            'descr': values.get('description', '-')}))
        records = super(Line, cls).create(vlist)

        if records:
            ValueStore.update_books(ValueStore.get_book_by_line(records))
        return records

    @classmethod
    def write(cls, *args):
        """ deny update if cashbook.line!='open',
            add or update debit/credit
        """
        ValueStore = Pool().get('cashbook.values')

        actions = iter(args)
        to_write = []
        to_update = []
        for lines, values in zip(actions, actions):
            cls.check_permission_write(lines, values)

            to_update.extend(lines)
            for line in lines:
                if line.reconciliation:
                    # deny state-change to 'edit' if line is
                    # linked to reconciliation
                    if values.get('state', '-') == 'edit':
                        raise UserError(gettext(
                            'cashbook.msg_line_deny_stateedit_with_recon',
                            recname=line.rec_name))

            # deny add to reconciliation if state is
            # not 'check', 'recon' or 'done'
            if values.get('reconciliation', None):
                for line in lines:
                    if line.state not in ['check', 'done', 'recon']:
                        raise UserError(gettext(
                            'cashbook.msg_line_deny_recon_by_state',
                            recname=line.rec_name))

            # update debit / credit
            fields_update = cls.get_fields_write_update()
            if len(set(values.keys()).intersection(set(fields_update))) > 0:
                for line in lines:
                    values2 = {}
                    values2.update(values)
                    values2.update(cls.clear_by_bookingtype(values, line))

                    # select required fields in case on 'bookingtype'
                    updt_fields = []
                    updt_fields.extend(values.keys())
                    if 'bookingtype' in values.keys():
                        updt_fields.extend([
                            x for x in fields_update
                            if x not in values.keys()])

                    values2.update(cls.get_debit_credit({
                            x: values.get(x, getattr(line, x))
                            for x in updt_fields}, line=line))
                    to_write.extend([lines, values2])
            else:
                to_write.extend([lines, values])

        super(Line, cls).write(*to_write)

        if to_update:
            ValueStore.update_books(ValueStore.get_book_by_line(to_update))

    @classmethod
    def delete(cls, lines):
        """ deny delete if book is not 'open' or wf is not 'edit'
        """
        ValueStore = Pool().get('cashbook.values')

        cls.check_permission_delete(lines)
        to_update = ValueStore.get_book_by_line(lines)
        super(Line, cls).delete(lines)
        ValueStore.update_books(to_update)

# end Line


class LineContext(ModelView):
    'Line Context'
    __name__ = 'cashbook.line.context'

    date_from = fields.Date(
        string='Start Date', depends=['date_to'],
        help='Limits the date range for the displayed entries.',
        domain=[
            If(Eval('date_to') & Eval('date_from'),
                ('date_from', '<=', Eval('date_to')),
                ()),
            ])
    date_to = fields.Date(
        string='End Date', depends=['date_from'],
        help='Limits the date range for the displayed entries.',
        domain=[
            If(Eval('date_to') & Eval('date_from'),
                ('date_from', '<=', Eval('date_to')),
                ()),
            ])
    checked = fields.Boolean(
        string='Checked',
        help='Show account lines in Checked-state.')
    done = fields.Boolean(
        string='Done',
        help='Show account lines in Done-state.')

    @classmethod
    def default_date_from(cls):
        """ get default from context
        """
        context = Transaction().context
        return context.get('date_from', None)

    @classmethod
    def default_date_to(cls):
        """ get default from context
        """
        context = Transaction().context
        return context.get('date_to', None)

    @classmethod
    def default_checked(cls):
        """ get default from context
        """
        context = Transaction().context
        return context.get('checked', False)

    @classmethod
    def default_done(cls):
        """ get default from context
        """
        context = Transaction().context
        return context.get('done', False)

# end LineContext
