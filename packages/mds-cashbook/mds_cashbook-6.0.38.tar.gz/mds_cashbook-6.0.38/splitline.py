# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.


from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool
from trytond.pyson import Eval, If
from trytond.report import Report
from trytond.i18n import gettext
from .line import sel_bookingtype, sel_linestate, STATES, DEPENDS
from .book import sel_state_book
from .mixin import SecondCurrencyMixin


sel_linetype = [
    ('cat', 'Category'),
    ('tr', 'Transfer'),
    ]

sel_target = [
    ('cashbook.book', 'Cashbook'),
    ('cashbook.category', 'Category'),
    ]


class SplitLine(SecondCurrencyMixin, ModelSQL, ModelView):
    'Split booking line'
    __name__ = 'cashbook.split'

    line = fields.Many2One(
        string='Line', required=True,
        select=True, ondelete='CASCADE', model_name='cashbook.line',
        readonly=True)
    description = fields.Text(
        string='Description', states=STATES, depends=DEPENDS)
    splittype = fields.Selection(
        string='Type', required=True,
        help='Type of split booking line', selection=sel_linetype,
        states=STATES, depends=DEPENDS, select=True)
    category = fields.Many2One(
        string='Category', select=True,
        model_name='cashbook.category', ondelete='RESTRICT',
        states={
            'readonly': STATES['readonly'],
            'required': Eval('splittype', '') == 'cat',
            'invisible': Eval('splittype', '') != 'cat',
        }, depends=DEPENDS+['bookingtype', 'splittype'],
        domain=[
            If(
                Eval('bookingtype', '') == 'spin',
                ('cattype', '=', 'in'),
                ('cattype', '=', 'out'),
            )])
    category_view = fields.Function(fields.Char(
        string='Category', readonly=True),
        'on_change_with_category_view')
    booktransf = fields.Many2One(
        string='Source/Dest',
        ondelete='RESTRICT', model_name='cashbook.book',
        domain=[
            ('owner.id', '=', Eval('owner_cashbook', -1)),
            ('id', '!=', Eval('cashbook', -1)),
            ('btype', '!=', None),
            ], select=True,
        states={
            'readonly': STATES['readonly'],
            'invisible': Eval('splittype', '') != 'tr',
            'required': Eval('splittype', '') == 'tr',
        }, depends=DEPENDS+['bookingtype', 'owner_cashbook', 'cashbook'])

    amount = fields.Numeric(
        string='Amount', digits=(16, Eval('currency_digits', 2)),
        required=True, states=STATES, depends=DEPENDS+['currency_digits'])

    date = fields.Function(fields.Date(
        string='Date', readonly=True), 'on_change_with_date')
    target = fields.Function(fields.Reference(
        string='Target', readonly=True,
        selection=sel_target), 'on_change_with_target')
    currency = fields.Function(fields.Many2One(
        model_name='currency.currency',
        string="Currency", readonly=True), 'on_change_with_currency')
    currency_digits = fields.Function(fields.Integer(
        string='Currency Digits',
        readonly=True), 'on_change_with_currency_digits')
    bookingtype = fields.Function(fields.Selection(
        string='Type', readonly=True,
        selection=sel_bookingtype), 'on_change_with_bookingtype')
    state = fields.Function(fields.Selection(
        string='State', readonly=True,
        selection=sel_linestate), 'on_change_with_state')
    cashbook = fields.Function(fields.Many2One(
        string='Cashbook',
        readonly=True, states={'invisible': True}, model_name='cashbook.book'),
        'on_change_with_cashbook')
    feature = fields.Function(fields.Char(
        string='Feature', readonly=True,
        states={'invisible': True}), 'on_change_with_feature')
    booktransf_feature = fields.Function(fields.Char(
        string='Feature', readonly=True,
        states={'invisible': True}), 'on_change_with_booktransf_feature')
    state_cashbook = fields.Function(fields.Selection(
        string='State of Cashbook',
        readonly=True, states={'invisible': True}, selection=sel_state_book),
        'on_change_with_state_cashbook')
    owner_cashbook = fields.Function(fields.Many2One(
        string='Owner', readonly=True,
        states={'invisible': True}, model_name='res.user'),
        'on_change_with_owner_cashbook')

    @classmethod
    def default_splittype(cls):
        """ default category
        """
        return 'cat'

    def get_rec_name(self, name):
        """ short + name
        """
        return '%(type)s|%(amount)s %(symbol)s|%(desc)s [%(target)s]' % {
            'desc': (self.description or '-')[:40],
            'amount': Report.format_number(
                self.amount, None,
                digits=getattr(self.currency, 'digits', 2)),
            'symbol': getattr(self.currency, 'symbol', '-'),
            'target': self.category_view
            if self.splittype == 'cat' else self.booktransf.rec_name,
            'type': gettext(
                'cashbook.msg_line_bookingtype_%s' % self.line.bookingtype),
            }

    @fields.depends('splittype', 'category', 'booktransf')
    def on_change_splittype(self):
        """ clear category if not valid type
        """
        if self.splittype:
            if self.splittype == 'cat':
                self.booktransf = None
            if self.splittype == 'tr':
                self.category = None

    @fields.depends('line', '_parent_line.date')
    def on_change_with_date(self, name=None):
        """ get date of line
        """
        if self.line:
            if self.line.date is not None:
                return self.line.date

    @fields.depends('splittype', 'category', 'booktransf')
    def on_change_with_target(self, name=None):
        """ get category or cashbook
        """
        if self.splittype:
            if self.splittype == 'cat':
                if self.category:
                    return 'cashbook.category,%d' % self.category.id
            elif self.splittype == 'tr':
                if self.booktransf:
                    return 'cashbook.book,%d' % self.booktransf.id

    @fields.depends('category')
    def on_change_with_category_view(self, name=None):
        """ show optimizef form of category for list-view
        """
        Configuration = Pool().get('cashbook.configuration')

        if self.category:
            cfg1 = Configuration.get_singleton()

            if getattr(cfg1, 'catnamelong', True) is True:
                return self.category.rec_name
            else:
                return self.category.name

    @fields.depends('line', '_parent_line.state')
    def on_change_with_state(self, name=None):
        """ get state
        """
        if self.line:
            return self.line.state

    @fields.depends('line', '_parent_line.cashbook')
    def on_change_with_cashbook(self, name=None):
        """ get cashbook
        """
        if self.line:
            return self.line.cashbook.id

    @fields.depends('line', '_parent_line.cashbook')
    def on_change_with_state_cashbook(self, name=None):
        """ get state of cashbook
        """
        if self.line:
            return self.line.cashbook.state

    @fields.depends('line', '_parent_line.cashbook')
    def on_change_with_owner_cashbook(self, name=None):
        """ get current owner
        """
        if self.line:
            return self.line.cashbook.owner.id

    @fields.depends('line', '_parent_line.bookingtype')
    def on_change_with_bookingtype(self, name=None):
        """ get type
        """
        if self.line:
            return self.line.bookingtype

    @fields.depends('line', '_parent_line.cashbook')
    def on_change_with_feature(self, name=None):
        """ get feature-set
        """
        if self.line:
            return self.line.cashbook.btype.feature

    @fields.depends('booktransf', '_parent_booktransf.feature')
    def on_change_with_booktransf_feature(self, name=None):
        """ get 'feature' of counterpart
        """
        if self.booktransf:
            if self.booktransf.btype:
                return self.booktransf.btype.feature

    @fields.depends('line', '_parent_line.cashbook')
    def on_change_with_currency(self, name=None):
        """ currency of cashbook
        """
        if self.line:
            return self.line.cashbook.currency.id

    @fields.depends('line', '_parent_line.cashbook')
    def on_change_with_currency_digits(self, name=None):
        """ currency-digits of cashbook
        """
        if self.line:
            return self.line.cashbook.currency.digits
        else:
            return 2

    @classmethod
    def add_2nd_unit_values(cls, values):
        """ extend create-values
        """
        Line2 = Pool().get('cashbook.line')
        line = Line2(values.get('line', None))

        if line:
            values.update(cls.add_2nd_currency(values, line.cashbook.currency))
        return values

    @classmethod
    def create(cls, vlist):
        """ add debit/credit
        """
        Line2 = Pool().get('cashbook.line')

        vlist = [x.copy() for x in vlist]
        for values in vlist:
            values.update(cls.add_2nd_unit_values(values))
        records = super(SplitLine, cls).create(vlist)

        to_update_line = []
        for record in records:
            if record.line not in to_update_line:
                to_update_line.append(record.line)

        to_write = Line2.update_values_by_splitlines(to_update_line)
        if len(to_write) > 0:
            Line2.write(*to_write)
        return records

    @classmethod
    def write(cls, *args):
        """ deny update if cashbook.line!='open',
            add or update debit/credit
        """
        Line2 = Pool().get('cashbook.line')

        actions = iter(args)
        to_update_line = []
        for records, values in zip(actions, actions):
            Line2.check_permission_write([x.line for x in records])

            if 'amount' in values.keys():
                for record in records:
                    if record.line not in to_update_line:
                        to_update_line.append(record.line)
        super(SplitLine, cls).write(*args)

        to_write = Line2.update_values_by_splitlines(to_update_line)
        if len(to_write) > 0:
            Line2.write(*to_write)

    @classmethod
    def delete(cls, splitlines):
        """ deny delete if book is not 'open' or wf is not 'edit'
        """
        Line2 = Pool().get('cashbook.line')

        Line2.check_permission_delete([x.line for x in splitlines])
        super(SplitLine, cls).delete(splitlines)

# end SplitLine
