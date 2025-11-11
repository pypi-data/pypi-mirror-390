# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import fields
from trytond.pyson import Eval, Bool, Or
from trytond.pool import Pool
from trytond.modules.currency.ir import rate_decimal
from trytond.transaction import Transaction
from decimal import Decimal


STATES = {
    'readonly': Or(
            Eval('state', '') != 'edit',
            Eval('state_cashbook', '') != 'open',
        ),
    }
DEPENDS = ['state', 'state_cashbook']


class SecondCurrencyMixin:
    """ two fields for 2nd currency: amount + rate
    """
    __slots__ = ()

    amount_2nd_currency = fields.Numeric(
        string='Amount Second Currency',
        digits=(16, Eval('currency2nd_digits', 2)),
        states={
            'readonly': Or(
                    STATES['readonly'],
                    ~Bool(Eval('currency2nd'))),
            'required': Bool(Eval('currency2nd')),
            'invisible': ~Bool(Eval('currency2nd')),
        }, depends=DEPENDS+['currency2nd_digits', 'currency2nd'])
    rate_2nd_currency = fields.Function(fields.Numeric(
        string='Rate',
        help='Exchange rate between the currencies of the ' +
        'participating cashbooks.',
        digits=(rate_decimal * 2, rate_decimal),
        states={
            'readonly': Or(
                    STATES['readonly'],
                    ~Bool(Eval('currency2nd'))),
            'required': Bool(Eval('currency2nd')),
            'invisible': ~Bool(Eval('currency2nd')),
        }, depends=DEPENDS+['currency2nd_digits', 'currency2nd']),
        'on_change_with_rate_2nd_currency', setter='set_rate_2nd_currency')

    currency2nd = fields.Function(fields.Many2One(
        model_name='currency.currency',
        string="2nd Currency", readonly=True), 'on_change_with_currency2nd')
    currency2nd_digits = fields.Function(fields.Integer(
        string='2nd Currency Digits',
        readonly=True), 'on_change_with_currency2nd_digits')

    @classmethod
    def add_2nd_currency(cls, values, from_currency):
        """ add second currency amount if missing
        """
        pool = Pool()
        Currency = pool.get('currency.currency')
        Cashbook = pool.get('cashbook.book')
        IrDate = pool.get('ir.date')

        booktransf = values.get('booktransf', None)
        amount = values.get('amount', None)
        amount_2nd_currency = values.get('amount_2nd_currency', None)

        if (amount is not None) and (booktransf is not None):
            if amount_2nd_currency is None:
                booktransf = Cashbook(booktransf)
                if from_currency.id != booktransf.currency.id:
                    with Transaction().set_context({
                            'date': values.get('date', IrDate.today())}):
                        values['amount_2nd_currency'] = Currency.compute(
                            from_currency,
                            amount,
                            booktransf.currency,
                            )
        return values

    @fields.depends(
        'booktransf', '_parent_booktransf.currency',
        'currency', 'amount', 'date', 'amount_2nd_currency',
        'rate_2nd_currency')
    def on_change_booktransf(self):
        """ update amount_2nd_currency
        """
        self.on_change_rate_2nd_currency()

    @fields.depends(
        'booktransf', '_parent_booktransf.currency',
        'currency', 'amount', 'date', 'amount_2nd_currency',
        'rate_2nd_currency')
    def on_change_amount(self):
        """ update amount_2nd_currency
        """
        self.on_change_rate_2nd_currency()

    @fields.depends(
        'booktransf', '_parent_booktransf.currency',
        'currency', 'amount', 'date', 'amount_2nd_currency',
        'rate_2nd_currency')
    def on_change_rate_2nd_currency(self):
        """ update amount_2nd_currency + rate_2nd_currency
        """
        pool = Pool()
        IrDate = pool.get('ir.date')
        Currency = pool.get('currency.currency')

        if (self.amount is None) or (self.booktransf is None):
            self.amount_2nd_currency = None
            self.rate_2nd_currency = None
            return

        if self.rate_2nd_currency is None:
            # no rate set, use current rate of target-currency
            with Transaction().set_context({
                    'date': self.date or IrDate.today()}):
                self.amount_2nd_currency = Currency.compute(
                    self.currency,
                    self.amount,
                    self.booktransf.currency)
                if self.amount != Decimal('0.0'):
                    self.rate_2nd_currency = \
                        self.amount_2nd_currency / self.amount
        else:
            self.amount_2nd_currency = self.booktransf.currency.round(
                    self.amount * self.rate_2nd_currency)

    @classmethod
    def set_rate_2nd_currency(cls, lines, name, value):
        """ compute amount_2nd_currency, write to db
        """
        Line2 = Pool().get(cls.__name__)

        to_write = []

        if not name == 'rate_2nd_currency':
            return

        for line in lines:
            if line.booktransf is None:
                continue

            if line.cashbook.currency.id == line.booktransf.currency.id:
                continue

            to_write.extend([
                [line],
                {
                    'amount_2nd_currency': line.booktransf.currency.round(
                        line.amount * value),
                }])

        if len(to_write) > 0:
            Line2.write(*to_write)

    @fields.depends('amount', 'amount_2nd_currency', 'rate_2nd_currency')
    def on_change_amount_2nd_currency(self):
        """ update rate_2nd_currency by rate
        """
        self.rate_2nd_currency = self.on_change_with_rate_2nd_currency()

    @fields.depends('amount', 'amount_2nd_currency')
    def on_change_with_rate_2nd_currency(self, name=None):
        """ get current rate from amount
        """
        Rate = Pool().get('currency.currency.rate')

        if (self.amount is not None) and \
                (self.amount_2nd_currency is not None):
            if self.amount != Decimal('0.0'):
                exp = Decimal(Decimal(1) / 10 ** Rate.rate.digits[1])
                return (self.amount_2nd_currency / self.amount).quantize(exp)

    @fields.depends('currency', 'booktransf', '_parent_booktransf.currency')
    def on_change_with_currency2nd(self, name=None):
        """ currency of transfer-target
        """
        if self.booktransf:
            if self.currency:
                if self.currency.id != self.booktransf.currency.id:
                    return self.booktransf.currency.id

    @fields.depends('booktransf', '_parent_booktransf.currency')
    def on_change_with_currency2nd_digits(self, name=None):
        """ currency of transfer-target
        """
        if self.booktransf:
            return self.booktransf.currency.digits
        else:
            return 2

# end SecondCurrencyMixin
