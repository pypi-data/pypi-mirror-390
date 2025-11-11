# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.pyson import Eval, Bool, If, And
from decimal import Decimal
from .line import sel_bookingtype

sel_booktypewiz = [x for x in sel_bookingtype if not x[0] in ['spin', 'spout']]


class EnterBookingStart(ModelView):
    'Enter Booking'
    __name__ = 'cashbook.enterbooking.start'

    cashbook = fields.Many2One(
        string='Cashbook', model_name='cashbook.book',
        domain=[('id', 'in', Eval('cashbooks', [])), ('btype', '!=', None)],
        depends=['cashbooks'], required=True)
    cashbooks = fields.One2Many(
        string='Cashbooks', field=None,
        model_name='cashbook.book', readonly=True,
        states={'invisible': True})
    owner_cashbook = fields.Function(fields.Many2One(
        string='Owner', readonly=True,
        states={'invisible': True}, model_name='res.user'),
        'on_change_with_owner_cashbook')
    currency = fields.Function(fields.Many2One(
        string='Currency',
        model_name='currency.currency', states={'invisible': True}),
        'on_change_with_currency')
    currency_digits = fields.Function(fields.Integer(
        string='Currency Digits',
        readonly=True, states={'invisible': True}),
        'on_change_with_currency_digits')
    bookingtype = fields.Selection(
        string='Type', required=True, selection=sel_booktypewiz)
    amount = fields.Numeric(
        string='Amount',
        depends=['currency_digits', 'bookingtype'],
        digits=(16, Eval('currency_digits', 2)), required=True,
        domain=[('amount', '>=', Decimal('0.0'))])
    description = fields.Text(
        string='Description', states={'required': Bool(Eval('fixate'))},
        depends=['fixate'])
    category = fields.Many2One(
        string='Category',
        model_name='cashbook.category', depends=['bookingtype'],
        states={
            'readonly': ~Bool(Eval('bookingtype')),
            'required': Eval('bookingtype', '').in_(['in', 'out']),
            'invisible': ~Eval('bookingtype', '').in_(['in', 'out']),
        },
        domain=[
            If(
                Eval('bookingtype', '').in_(['in', 'mvin']),
                ('cattype', '=', 'in'),
                ('cattype', '=', 'out'),
            )])
    fixate = fields.Boolean(
        string='Check booking', help='The booking is checked immediately.')
    date = fields.Date(string='Date', help='Date of booking')

    # party or cashbook as counterpart
    booktransf = fields.Many2One(
        string='Source/Dest',
        model_name='cashbook.book',
        domain=[
            ('owner.id', '=', Eval('owner_cashbook', -1)),
            ('id', '!=', Eval('cashbook', -1)),
            ],
        states={
            'invisible': ~Eval('bookingtype', '').in_(['mvin', 'mvout']),
            'required': Eval('bookingtype', '').in_(['mvin', 'mvout']),
        }, depends=['bookingtype', 'owner_cashbook', 'cashbook'])
    party = fields.Many2One(
        string='Party', model_name='party.party',
        states={
            'invisible': ~Eval('bookingtype', '').in_(['in', 'out']),
            'required': And(
                Bool(Eval('fixate')),
                Eval('bookingtype', '').in_(['in', 'out']))},
        depends=['bookingtype', 'fixate'])

    @fields.depends('bookingtype', 'category')
    def on_change_bookingtype(self):
        """ clear category if not valid type
        """
        types = {
            'in': ['in', 'mvin'],
            'out': ['out', 'mvout'],
            }

        if self.bookingtype:
            if self.category:
                if self.bookingtype not in types.get(
                        self.category.cattype, ''):
                    self.category = None

    @fields.depends('cashbook', '_parent_cashbook.owner')
    def on_change_with_owner_cashbook(self, name=None):
        """ get current owner
        """
        if self.cashbook:
            return self.cashbook.owner.id

    @fields.depends('cashbook', '_parent_cashbook.currency')
    def on_change_with_currency(self, name=None):
        """ digits
        """
        if self.cashbook:
            return self.cashbook.currency.id

    @fields.depends('cashbook', '_parent_cashbook.currency')
    def on_change_with_currency_digits(self, name=None):
        """ digits
        """
        if self.cashbook:
            return self.cashbook.currency.digits
        else:
            return 2

# end EnterBookingStart


class EnterBookingWizard(Wizard):
    'Enter Booking'
    __name__ = 'cashbook.enterbooking'

    start_state = 'start'
    start = StateView(
        'cashbook.enterbooking.start',
        'cashbook.enterbooking_start_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Save', 'save_', 'tryton-save', default=True),
            Button('Save & Next', 'savenext_', 'tryton-forward'),
            ])
    save_ = StateTransition()
    savenext_ = StateTransition()

    def default_start(self, fields):
        """ setup form
        """
        pool = Pool()
        Cashbook = pool.get('cashbook.book')
        Configuration = pool.get('cashbook.configuration')
        IrDate = pool.get('ir.date')

        cfg1 = Configuration.get_singleton()

        book_ids = []
        for x in ['defbook', 'book1', 'book2', 'book3', 'book4', 'book5']:
            if getattr(cfg1, x, None) is not None:
                book_ids.append(getattr(cfg1, x, None).id)

        result = {
            'fixate': cfg1.fixate
            if cfg1 and cfg1.fixate is not None else False,
            'cashbooks': [x.id for x in Cashbook.search([
                    ('state', '=', 'open'),
                    ('btype', '!=', None),
                    ('owner', '=', Transaction().user),
                    ('id', 'in', book_ids),
                ])],
            'bookingtype': getattr(self.start, 'bookingtype', 'out'),
            'cashbook': getattr(getattr(cfg1, 'defbook', None), 'id', None),
            'amount': None,
            'party': None,
            'booktransf': None,
            'description': None,
            'category': None,
            'date': IrDate.today()}
        return result

    def transition_save_(self):
        """ store booking
        """
        pool = Pool()
        Line = pool.get('cashbook.line')

        query = {
            'cashbook': self.start.cashbook.id,
            'description': self.start.description,
            'date': self.start.date,
            'bookingtype': self.start.bookingtype,
            'amount': self.start.amount}

        if self.start.bookingtype in ['in', 'out']:
            query['category'] = self.start.category.id
            query['party'] = getattr(self.start.party, 'id', None)
        elif self.start.bookingtype in ['mvin', 'mvout']:
            query['booktransf'] = self.start.booktransf.id

        lines = Line.create([query])
        if self.start.fixate:
            Line.wfcheck(lines)
        return 'end'

    def transition_savenext_(self):
        """ store booking & restart
        """
        self.transition_save_()
        return 'start'

# end EnterBookingWizard
