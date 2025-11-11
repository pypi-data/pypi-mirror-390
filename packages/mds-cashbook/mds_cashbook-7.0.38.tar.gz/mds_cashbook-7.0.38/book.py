# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import (
    Workflow, ModelView, ModelSQL, fields, Check, tree, Index)
from trytond.pyson import Eval, Or, Bool, Id
from trytond.exceptions import UserError
from trytond.i18n import gettext
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.report import Report
from decimal import Decimal
from datetime import date
from sql.aggregate import Sum
from sql.conditionals import Case
from .model import (
    order_name_hierarchical, sub_ids_hierarchical, AnyInArray)


STATES = {
    'readonly': Eval('state', '') != 'open',
    }
DEPENDS = ['state']

# states in case of 'btype'!=None
STATES2 = {
    'readonly': Or(
            Eval('state', '') != 'open',
            ~Bool(Eval('btype')),
        ),
    'invisible': ~Bool(Eval('btype')),
    }
STATES3 = {}
STATES3.update(STATES2)
STATES3['required'] = ~STATES2['invisible']
DEPENDS2 = ['state', 'btype']

sel_state_book = [
    ('open', 'Open'),
    ('closed', 'Closed'),
    ('archive', 'Archive'),
    ]


class Book(tree(separator='/'), Workflow, ModelSQL, ModelView):
    'Cashbook'
    __name__ = 'cashbook.book'

    company = fields.Many2One(
        string='Company', model_name='company.company',
        required=True, ondelete="RESTRICT")
    name = fields.Char(
        string='Name', required=True, states=STATES, depends=DEPENDS)
    description = fields.Text(
        string='Description', states=STATES, depends=DEPENDS)
    btype = fields.Many2One(
        string='Type',
        help='A cash book with type can contain postings. ' +
        'Without type is a view.',
        model_name='cashbook.type', ondelete='RESTRICT',
        states={
            'readonly': Or(
                STATES['readonly'],
                Eval('has_lines', False))},
        depends=DEPENDS+['has_lines'])
    feature = fields.Function(fields.Char(
        string='Feature', readonly=True,
        states={'invisible': True}), 'on_change_with_feature')
    owner = fields.Many2One(
        string='Owner', required=True,
        model_name='res.user', ondelete='SET NULL',
        states=STATES, depends=DEPENDS)
    reviewer = fields.Many2One(
        string='Reviewer',
        help='Group of users who have write access to the cashbook.',
        model_name='res.group', ondelete='SET NULL',
        states=STATES, depends=DEPENDS)
    observer = fields.Many2One(
        string='Observer',
        help='Group of users who have read-only access to the cashbook.',
        model_name='res.group', ondelete='SET NULL',
        states=STATES, depends=DEPENDS)
    lines = fields.One2Many(
        string='Lines', field='cashbook',
        model_name='cashbook.line',
        states=STATES, depends=DEPENDS)
    has_lines = fields.Function(fields.Boolean(
        string='Has Lines', readonly=True, states={'invisible': True}),
        'on_change_with_has_lines')
    reconciliations = fields.One2Many(
        string='Reconciliations',
        field='cashbook', model_name='cashbook.recon',
        states=STATES2, depends=DEPENDS2)
    number_sequ = fields.Many2One(
        string='Line numbering',
        help='Number sequence for numbering of the cash book lines.',
        model_name='ir.sequence',
        domain=[
            ('sequence_type', '=',
                Id('cashbook', 'sequence_type_cashbook_line')),
            ['OR',
                ('company', '=', None),
                ('company', '=', Eval('company', -1))],
            ],
        states=STATES3, depends=DEPENDS2+['company'])
    number_atcheck = fields.Boolean(
        string="number when 'Checking'",
        help="The numbering of the lines is done in the step Check. " +
        "If the check mark is inactive, this happens with Done.",
        states=STATES2, depends=DEPENDS2)
    start_date = fields.Date(
        string='Initial Date',
        states={
            'readonly': Or(
                STATES2['readonly'],
                Eval('has_lines', False)),
            'invisible': STATES2['invisible'],
            'required': ~STATES2['invisible'],
        }, depends=DEPENDS2+['has_lines'])

    value_store = fields.One2Many(
        string='Values', model_name='cashbook.values', field='cashbook',
        readonly=True)
    balance = fields.Function(fields.Numeric(
        string='Balance',
        readonly=True, depends=['currency_digits'],
        help='Balance of bookings to date',
        digits=(16, Eval('currency_digits', 2))),
        'get_balance_cashbook', searcher='search_balance')
    balance_all = fields.Function(fields.Numeric(
        string='Total balance',
        readonly=True, depends=['currency_digits'],
        help='Balance of all bookings',
        digits=(16, Eval('currency_digits', 2))),
        'get_balance_cashbook', searcher='search_balance')
    balance_ref = fields.Function(fields.Numeric(
        string='Balance (Ref.)',
        help='Balance in company currency',
        readonly=True, digits=(16, Eval('company_currency_digits', 2)),
        states={
            'invisible': ~Bool(Eval('company_currency')),
        }, depends=['company_currency_digits', 'company_currency']),
        'get_balance_cashbook', searcher='search_balance')
    company_currency = fields.Function(fields.Many2One(
        readonly=True,
        string='Company Currency', states={'invisible': True},
        model_name='currency.currency'),
        'on_change_with_company_currency')
    company_currency_digits = fields.Function(fields.Integer(
        string='Currency Digits (Ref.)', readonly=True),
        'on_change_with_currency_digits')

    currency = fields.Many2One(
        string='Currency',
        model_name='currency.currency',
        states={
            'readonly': Or(
                STATES2['readonly'],
                Eval('has_lines', False))},
        depends=DEPENDS2+['has_lines'])
    currency_digits = fields.Function(fields.Integer(
        string='Currency Digits',
        readonly=True), 'on_change_with_currency_digits')
    state = fields.Selection(
        string='State', required=True,
        readonly=True, selection=sel_state_book)
    state_string = state.translated('state')

    parent = fields.Many2One(
        string="Parent",
        model_name='cashbook.book', ondelete='RESTRICT')
    childs = fields.One2Many(
        string='Children', field='parent',
        model_name='cashbook.book')

    @classmethod
    def __register__(cls, module_name):
        super(Book, cls).__register__(module_name)

        table = cls.__table_handler__(module_name)
        table.drop_column('start_balance')
        table.drop_column('left')
        table.drop_column('right')

    @classmethod
    def __setup__(cls):
        super(Book, cls).__setup__()
        cls._order.insert(0, ('rec_name', 'ASC'))
        cls._order.insert(0, ('state', 'ASC'))
        t = cls.__table__()
        cls._sql_indexes.update({
            Index(
                t,
                (t.btype, Index.Equality())),
            Index(
                t,
                (t.company, Index.Equality())),
            Index(
                t,
                (t.currency, Index.Equality())),
            Index(
                t,
                (t.state, Index.Equality())),
            Index(
                t,
                (t.owner, Index.Equality())),
            Index(
                t,
                (t.reviewer, Index.Equality())),
            Index(
                t,
                (t.observer, Index.Equality())),
            })
        cls._sql_constraints.extend([
            ('state_val',
                Check(t, t.state.in_(['open', 'closed', 'archive'])),
                'cashbook.msg_book_wrong_state_value'),
            ])
        cls._transitions |= set((
                ('open', 'closed'),
                ('closed', 'open'),
                ('closed', 'archive'),
            ))
        cls._buttons.update({
            'wfopen': {
                'invisible': Eval('state', '') != 'closed',
                'depends': ['state'],
                },
            'wfclosed': {
                'invisible': Eval('state') != 'open',
                'depends': ['state'],
                },
            'wfarchive': {
                'invisible': Eval('state') != 'closed',
                'depends': ['state'],
                },
            })

    @classmethod
    def default_number_atcheck(cls):
        return True

    @classmethod
    def default_currency(cls):
        """ currency of company
        """
        Company = Pool().get('company.company')

        company = cls.default_company()
        if company:
            company = Company(company)
            if company.currency:
                return company.currency.id

    @staticmethod
    def default_company():
        return Transaction().context.get('company') or None

    @classmethod
    def default_start_date(cls):
        """ today
        """
        IrDate = Pool().get('ir.date')
        return IrDate.today()

    @classmethod
    def default_state(cls):
        return 'open'

    @classmethod
    def default_owner(cls):
        """ default: current user
        """
        return Transaction().user

    @staticmethod
    def order_state(tables):
        """ edit = 0, check/done = 1
        """
        Book2 = Pool().get('cashbook.book')
        tab_book = Book2.__table__()
        table, _ = tables[None]

        query = tab_book.select(
                Case(
                    (tab_book.state == 'open', 0),
                    else_=1),
                where=tab_book.id == table.id)
        return [query]

    @staticmethod
    def order_rec_name(tables):
        """ order by pos
            a recursive sorting
        """
        return order_name_hierarchical('cashbook.book', tables)

    def get_rec_name(self, name):
        """ name, balance, state
        """
        recname = super(Book, self).get_rec_name(name)
        if self.btype:
            return '%(name)s | %(balance)s %(symbol)s | %(state)s' % {
                'name': recname or '-',
                'balance': Report.format_number(
                    self.balance or 0.0, None,
                    digits=getattr(self.currency, 'digits', 2)),
                'symbol': getattr(self.currency, 'symbol', '-'),
                'state': self.state_string,
                }
        return recname

    @classmethod
    def get_balance_of_cashbook_sql(cls):
        """ sql for balance of a single cashbook
        """
        pool = Pool()
        Line = pool.get('cashbook.line')
        Book2 = pool.get('cashbook.book')
        IrDate = pool.get('ir.date')
        tab_line = Line.__table__()
        tab_book = Book2.__table__()
        context = Transaction().context

        query_date = context.get('date', IrDate.today())

        # deny invalid date in context
        if isinstance(query_date, str):
            try:
                date.fromisoformat(query_date)
            except Exception:
                query_date = IrDate.today()

        query = tab_book.join(
                tab_line,
                condition=tab_book.id == tab_line.cashbook,
            ).select(
                tab_line.cashbook,
                tab_book.currency,
                Sum(Case(
                    (tab_line.date <= query_date,
                        tab_line.credit - tab_line.debit),
                    else_=Decimal('0.0'),
                )).as_('balance'),
                Sum(tab_line.credit - tab_line.debit).as_('balance_all'),
                group_by=[tab_line.cashbook, tab_book.currency],
            )
        return (query, tab_line)

    @classmethod
    def work_order_balance(cls, tables, field_name):
        """ get order-query
        """
        pool = Pool()
        Book2 = pool.get('cashbook.book')
        ValueStore = pool.get('cashbook.values')
        context = Transaction().context

        query_date = context.get('date', None)
        table, _ = tables[None]
        if query_date is not None:
            if field_name == 'balance_ref':
                raise UserError(gettext(
                    'cashbook.msg_nosearch_with_date',
                    fname=field_name, model=Book2.__name__))

            (tab_book, tab2) = Book2.get_balance_of_cashbook_sql()
            query = tab_book.select(
                getattr(tab_book, field_name),
                where=tab_book.cashbook == table.id)
            return [query]
        else:
            tab_val = ValueStore.__table__()
            tab_book = Book2.__table__()

            query = tab_book.join(
                    tab_val,
                    condition=(
                        tab_book.id == tab_val.cashbook) & (
                        tab_val.field_name == field_name),
                ).select(
                    tab_val.numvalue,
                    where=tab_book.id == table.id)
            return [query]

    @staticmethod
    def order_balance(tables):
        """ order by balance
        """
        Book2 = Pool().get('cashbook.book')
        return Book2.work_order_balance(tables, 'balance')

    @staticmethod
    def order_balance_all(tables):
        """ order by balance-all
        """
        Book2 = Pool().get('cashbook.book')
        return Book2.work_order_balance(tables, 'balance_all')

    @staticmethod
    def order_balance_ref(tables):
        """ order by balance-all
        """
        Book2 = Pool().get('cashbook.book')
        return Book2.work_order_balance(tables, 'balance_ref')

    @classmethod
    def search_balance(cls, name, clause):
        """ search in 'balance'
        """
        ValueStore = Pool().get('cashbook.values')
        Operator = fields.SQL_OPERATORS[clause[1]]
        context = Transaction().context

        query_date = context.get('date', None)
        if query_date is not None:

            if name == 'balance_ref':
                raise UserError(gettext(
                    'cashbook.msg_nosearch_with_date',
                    fname=name, model=cls.__name__))

            (tab_line, tab2) = cls.get_balance_of_cashbook_sql()
            query = tab_line.select(
                    tab_line.cashbook,
                    where=Operator(
                        getattr(tab_line, name), clause[2]))
            return [('id', 'in', query)]
        else:
            value_query = ValueStore.search([
                ('field_name', '=', clause[0]),
                ('numvalue',) + tuple(clause[1:]),
                ],
                query=True)
            return [('value_store', 'in', value_query)]

    @classmethod
    def valuestore_delete_records(cls, records):
        """ delete value-records
        """
        ValStore = Pool().get('cashbook.values')
        if records:
            ValStore.delete_values(records)

    @classmethod
    def valuestore_fields(cls):
        """ field to update
        """
        return ['balance', 'balance_all', 'balance_ref']

    @classmethod
    def valuestore_update_records(cls, records):
        """ compute current values of records,
            store to global storage
        """
        ValStore = Pool().get('cashbook.values')

        if records:
            ValStore.update_values(
                cls.get_balance_values(
                    records,
                    ['balance', 'balance_all', 'balance_ref']))

    @classmethod
    def get_balance_cashbook(cls, cashbooks, names):
        """ get balance of cashbooks
        """
        context = Transaction().context

        result = {x: {y.id: Decimal('0.0') for y in cashbooks} for x in names}

        # return computed values if 'date' is in context
        query_date = context.get('date', None)
        if query_date is not None:
            return cls.get_balance_values(cashbooks, names)

        for cashbook in cashbooks:
            for value in cashbook.value_store:
                if value.field_name in names:
                    result[value.field_name][cashbook.id] = value.numvalue
        return result

    @classmethod
    def get_balance_values(cls, cashbooks, names):
        """ get balance of cashbook
        """
        pool = Pool()
        Book2 = pool.get('cashbook.book')
        Currency = pool.get('currency.currency')
        Company = pool.get('company.company')
        IrDate = pool.get('ir.date')
        tab_book = Book2.__table__()
        tab_comp = Company.__table__()
        cursor = Transaction().connection.cursor()
        context = Transaction().context

        result = {
            x: {y.id: Decimal('0.0') for y in cashbooks}
            for x in ['balance', 'balance_all', 'balance_ref']}

        # deny invalid date in context
        query_date = context.get('date', IrDate.today())
        if isinstance(query_date, str):
            try:
                date.fromisoformat(query_date)
            except Exception:
                query_date = IrDate.today()

        # query balances of cashbooks and sub-cashbooks
        with Transaction().set_context({
                'date': query_date}):
            (tab_line, tab2) = cls.get_balance_of_cashbook_sql()
            tab_subids = sub_ids_hierarchical('cashbook.book')
            query = tab_book.join(
                    tab_subids,
                    condition=tab_book.id == tab_subids.parent,
                ).join(
                    tab_comp,
                    condition=tab_book.company == tab_comp.id,
                ).join(
                    tab_line,
                    condition=tab_line.cashbook == AnyInArray(
                        tab_subids.subids),
                ).select(
                    tab_book.id,
                    tab_book.currency.as_('to_currency'),
                    tab_line.currency.as_('from_currency'),
                    tab_comp.currency.as_('company_currency'),
                    Sum(tab_line.balance).as_('balance'),
                    Sum(tab_line.balance_all).as_('balance_all'),
                    group_by=[
                        tab_book.id, tab_line.currency, tab_comp.currency],
                    where=tab_book.id.in_([x.id for x in cashbooks]),
                )
            cursor.execute(*query)
            records = cursor.fetchall()

            for record in records:
                result['balance'][record[0]] += Currency.compute(
                        record[2], record[4], record[1])
                result['balance_all'][record[0]] += Currency.compute(
                        record[2], record[5], record[1])
                result['balance_ref'][record[0]] += Currency.compute(
                        record[2], record[5], record[3])
        return result

    @fields.depends('id')
    def on_change_with_has_lines(self, name=None):
        """ return True if cashbook has lines
            (we dont use 'if self.lines:' this would slow down the client)
        """
        Line = Pool().get('cashbook.line')

        if Line.search_count([('cashbook', '=', self.id)]):
            return True
        return False

    @fields.depends('btype')
    def on_change_with_feature(self, name=None):
        """ get feature-set
        """
        if self.btype:
            return self.btype.feature

    @fields.depends('currency')
    def on_change_with_currency_digits(self, name=None):
        """ currency of cashbook
        """
        if self.currency:
            return self.currency.digits
        else:
            return 2

    @fields.depends('company', 'currency', 'btype')
    def on_change_with_company_currency(self, name=None):
        """ get company-currency if its different from current
            cashbook-currency, disable if book is a view
        """
        if self.company:
            if self.currency:
                if self.btype:
                    if self.company.currency.id != self.currency.id:
                        return self.company.currency.id

    @classmethod
    @ModelView.button
    @Workflow.transition('open')
    def wfopen(cls, books):
        """ open cashbook
        """
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('closed')
    def wfclosed(cls, books):
        """ cashbook is closed
        """
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('archive')
    def wfarchive(cls, books):
        """ cashbook is archived
        """
        pass

    @classmethod
    def create(cls, vlist):
        """ update values
        """
        records = super(Book, cls).create(vlist)
        cls.valuestore_update_records(records)
        return records

    @classmethod
    def write(cls, *args):
        """ deny update if book is not 'open'
        """
        ConfigUser = Pool().get('cashbook.configuration_user')

        actions = iter(args)
        to_write_config = []
        to_update = []
        for books, values in zip(actions, actions):
            to_update.extend(books)
            for book in books:
                # deny btype-->None if lines not empty
                if 'btype' in values.keys():
                    if (values['btype'] is None) and (len(book.lines) > 0):
                        raise UserError(gettext(
                            'cashbook.msg_book_btype_with_lines',
                            cbname=book.rec_name,
                            numlines=len(book.lines)))

                if book.state != 'open':
                    # allow state-update, if its the only action
                    if not (('state' in values.keys()) and
                            (len(values.keys()) == 1)):
                        raise UserError(gettext(
                            'cashbook.msg_book_deny_write',
                            bookname=book.rec_name,
                            state_txt=book.state_string))

                # if owner changes, remove book from user-config
                if 'owner' in values.keys():
                    if book.owner.id != values['owner']:
                        for x in [
                                'defbook', 'book1', 'book2', 'book3',
                                'book4', 'book5']:
                            cfg1 = ConfigUser.search([
                                    ('iduser', '=', book.owner.id),
                                    ('%s.id' % x, '=', book.id)])
                            if len(cfg1) > 0:
                                to_write_config.extend([cfg1, {x: None}])
        super(Book, cls).write(*args)

        if len(to_write_config) > 0:
            ConfigUser.write(*to_write_config)
        cls.valuestore_update_records(to_update)

    @classmethod
    def delete(cls, books):
        """ deny delete if book has lines
        """
        for book in books:
            if (len(book.lines) > 0) and (book.state != 'archive'):
                raise UserError(gettext(
                    'cashbook.msg_book_deny_delete',
                    bookname=book.rec_name,
                    booklines=len(book.lines)))
        super(Book, cls).delete(books)

# end Book
