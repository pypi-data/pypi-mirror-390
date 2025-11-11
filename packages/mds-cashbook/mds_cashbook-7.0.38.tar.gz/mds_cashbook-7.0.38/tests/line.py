# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from datetime import date
from unittest.mock import MagicMock
from decimal import Decimal


class LineTestCase(object):
    """ test lines
    """
    @with_transaction()
    def test_line_check_add_amount2nd_currency(self):
        """ create cashbook, lines, add transfer without
            amount_2nd_currency
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')
        Currency = pool.get('currency.currency')

        types = self.prep_type()
        company = self.prep_company()

        # add EURO, set company-currency to EURO
        (usd, euro) = self.prep_2nd_currency(company)
        self.assertEqual(len(usd.rates), 1)
        self.assertEqual(usd.rates[0].date, date(2022, 5, 2))
        self.assertEqual(usd.rates[0].rate, Decimal('1.05'))
        Currency.write(*[
            [usd],
            {
                'rates': [('create', [{
                    'rate': Decimal('1.02'),
                    'date': date(2022, 6, 1),
                    }])],
            }])
        self.assertEqual(len(usd.rates), 2)

        books = Book.create([{
            'name': 'Book USD',
            'btype': types.id,
            'company': company.id,
            'currency': usd.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }, {
            'name': 'Book EURO',
            'btype': types.id,
            'company': company.id,
            'currency': euro.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }])
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].rec_name, 'Book USD | 0.00 usd | Open')
        self.assertEqual(books[1].rec_name, 'Book EURO | 0.00 € | Open')

        # rate @ 2022-05-02: 1.05
        Book.write(*[
            [books[0]],
            {
                'lines': [('create', [{
                        'date': date(2022, 5, 5),
                        'description': 'Transfer USD --> EUR',
                        'bookingtype': 'mvout',
                        'amount': Decimal('10.0'),
                        'booktransf': books[1].id,
                    }])],
            }])
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/05/2022|to|-10.00 usd|Transfer USD --> EUR ' +
            '[Book EURO | 0.00 € | Open]')
        self.assertEqual(books[0].lines[0].amount, Decimal('10.0'))
        # auto-created
        self.assertEqual(books[0].lines[0].amount_2nd_currency, Decimal('9.52'))
        self.assertEqual(books[0].lines[0].rate_2nd_currency, Decimal('0.952'))
        Lines.delete(books[0].lines)

        # rate @ 2022-06-01: 1.02
        Book.write(*[
            [books[0]],
            {
                'lines': [('create', [{
                        'date': date(2022, 6, 1),
                        'description': 'Transfer USD --> EUR',
                        'bookingtype': 'mvout',
                        'amount': Decimal('10.0'),
                        'booktransf': books[1].id,
                    }])],
            }])
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(
            books[0].lines[0].rec_name,
            '06/01/2022|to|-10.00 usd|Transfer USD --> EUR ' +
            '[Book EURO | 0.00 € | Open]')
        self.assertEqual(books[0].lines[0].amount, Decimal('10.0'))
        # auto-created
        self.assertEqual(books[0].lines[0].amount_2nd_currency, Decimal('9.80'))
        self.assertEqual(books[0].lines[0].rate_2nd_currency, Decimal('0.98'))
        Lines.delete(books[0].lines)

        Book.write(*[
            [books[0]],
            {
                'lines': [('create', [{
                        'date': date(2022, 5, 5),
                        'description': 'Transfer USD --> EUR',
                        'bookingtype': 'mvout',
                        'amount': Decimal('10.0'),
                        'booktransf': books[1].id,
                        'amount_2nd_currency': Decimal('8.5'),
                    }])],
            }])
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/05/2022|to|-10.00 usd|Transfer USD --> ' +
            'EUR [Book EURO | 0.00 € | Open]')
        self.assertEqual(books[0].lines[0].amount, Decimal('10.0'))
        # manual set
        self.assertEqual(books[0].lines[0].amount_2nd_currency, Decimal('8.5'))
        self.assertEqual(books[0].lines[0].rate_2nd_currency, Decimal('0.85'))

        # update rate to get new amount_2nd_currency
        Lines.write(*[
            [books[0].lines[0]],
            {
                'rate_2nd_currency': Decimal('0.9'),
            }])
        self.assertEqual(books[0].lines[0].amount_2nd_currency, Decimal('9.0'))

        # update amount, rate, amount_2nd_currency
        self.assertEqual(books[0].lines[0].rate_2nd_currency, Decimal('0.9'))
        self.assertEqual(books[0].lines[0].amount_2nd_currency, Decimal('9.0'))
        self.assertEqual(books[0].lines[0].amount, Decimal('10.0'))

        books[0].lines[0].amount = Decimal('12.0')
        books[0].lines[0].on_change_amount()
        self.assertEqual(books[0].lines[0].rate_2nd_currency, Decimal('0.9'))
        self.assertEqual(books[0].lines[0].amount_2nd_currency, Decimal('10.8'))
        self.assertEqual(books[0].lines[0].amount, Decimal('12.0'))

        books[0].lines[0].rate_2nd_currency = Decimal('0.95')
        books[0].lines[0].on_change_rate_2nd_currency()
        self.assertEqual(books[0].lines[0].rate_2nd_currency, Decimal('0.95'))
        self.assertEqual(books[0].lines[0].amount_2nd_currency, Decimal('11.4'))
        self.assertEqual(books[0].lines[0].amount, Decimal('12.0'))

        books[0].lines[0].amount_2nd_currency = Decimal('10.5')
        books[0].lines[0].on_change_amount_2nd_currency()
        self.assertEqual(books[0].lines[0].rate_2nd_currency, Decimal('0.875'))
        self.assertEqual(books[0].lines[0].amount_2nd_currency, Decimal('10.5'))
        self.assertEqual(books[0].lines[0].amount, Decimal('12.0'))

    @with_transaction()
    def test_line_check_migrate_amount_2nd_currency(self):
        """ create cashbook, lines, transfer
            check migration
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')
        tab_line = Lines.__table__()
        cursor = Transaction().connection.cursor()

        types = self.prep_type()
        company = self.prep_company()

        # add EURO, set company-currency to EURO
        (usd, euro) = self.prep_2nd_currency(company)

        books = Book.create([{
            'name': 'Book USD',
            'btype': types.id,
            'company': company.id,
            'currency': usd.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }, {
            'name': 'Book EURO',
            'btype': types.id,
            'company': company.id,
            'currency': euro.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }])
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].rec_name, 'Book USD | 0.00 usd | Open')
        self.assertEqual(books[1].rec_name, 'Book EURO | 0.00 € | Open')

        Book.write(*[
            [books[0]],
            {
                'lines': [('create', [{
                        'date': date(2022, 5, 5),
                        'description': 'Transfer USD --> EUR',
                        'bookingtype': 'mvout',
                        'amount': Decimal('10.0'),
                        'booktransf': books[1].id,
                    }])],
            }])
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(len(books[1].lines), 0)
        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/05/2022|to|-10.00 usd|Transfer USD --> ' +
            'EUR [Book EURO | 0.00 € | Open]')
        self.assertEqual(books[0].lines[0].amount_2nd_currency, Decimal('9.52'))

        # clear field 'amount_2nd_currency' to prepare for migration
        clear_field = tab_line.update(
                columns=[tab_line.amount_2nd_currency],
                values=[None],
                where=(tab_line.id == books[0].lines[0].id),
            )
        cursor.execute(*clear_field)

        # migrate
        Lines.migrate_amount_2nd_currency()
        self.assertEqual(books[0].lines[0].amount_2nd_currency, Decimal('9.52'))

    @with_transaction()
    def test_line_check_transfer_2nd_currency_out(self):
        """ create cashbook, lines, transfer amount between
            accounts with different currencies
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')

        types = self.prep_type()
        company = self.prep_company()

        # add EURO, set company-currency to EURO
        (usd, euro) = self.prep_2nd_currency(company)

        books = Book.create([{
            'name': 'Book USD',
            'btype': types.id,
            'company': company.id,
            'currency': usd.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }, {
            'name': 'Book EURO',
            'btype': types.id,
            'company': company.id,
            'currency': euro.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }])
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].rec_name, 'Book USD | 0.00 usd | Open')
        self.assertEqual(books[1].rec_name, 'Book EURO | 0.00 € | Open')

        Book.write(*[
            [books[0]],
            {
                'lines': [('create', [{
                        'date': date(2022, 5, 5),
                        'description': 'Transfer USD --> EUR',
                        'bookingtype': 'mvout',
                        'amount': Decimal('10.0'),
                        'booktransf': books[1].id,
                    }])],
            }])
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(len(books[1].lines), 0)
        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/05/2022|to|-10.00 usd|Transfer USD --> ' +
            'EUR [Book EURO | 0.00 € | Open]')
        self.assertEqual(books[0].lines[0].amount_2nd_currency, Decimal('9.52'))
        self.assertEqual(books[0].lines[0].reference, None)
        self.assertEqual(len(books[0].lines[0].references), 0)
        self.assertEqual(books[0].lines[0].reconciliation, None)

        Lines.wfcheck([books[0].lines[0]])

        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(len(books[1].lines), 1)
        self.assertEqual(books[0].lines[0].reference, None)
        self.assertEqual(len(books[0].lines[0].references), 1)

        self.prep_valstore_run_worker()

        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/05/2022|to|-10.00 usd|Transfer USD --> ' +
            'EUR [Book EURO | 9.52 € | Open]')
        self.assertEqual(
            books[1].lines[0].rec_name,
            '05/05/2022|from|9.52 €|Transfer USD --> ' +
            'EUR [Book USD | -10.00 usd | Open]')
        self.assertEqual(books[0].balance, Decimal('-10.0'))
        self.assertEqual(books[0].currency.rec_name, 'usd')
        self.assertEqual(books[1].balance, Decimal('9.52'))
        self.assertEqual(books[1].currency.rec_name, 'Euro')

    @with_transaction()
    def test_line_check_transfer_2nd_currency_in(self):
        """ create cashbook, lines, transfer amount between
            accounts with different currencies
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')

        types = self.prep_type()
        company = self.prep_company()

        # add EURO, set company-currency to EURO
        (usd, euro) = self.prep_2nd_currency(company)

        books = Book.create([{
            'name': 'Book USD',
            'btype': types.id,
            'company': company.id,
            'currency': usd.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }, {
            'name': 'Book EURO',
            'btype': types.id,
            'company': company.id,
            'currency': euro.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }])
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].rec_name, 'Book USD | 0.00 usd | Open')
        self.assertEqual(books[1].rec_name, 'Book EURO | 0.00 € | Open')

        Book.write(*[
            [books[0]],
            {
                'lines': [('create', [{
                        'date': date(2022, 5, 5),
                        'description': 'Transfer USD <-- EUR',
                        'bookingtype': 'mvin',
                        'amount': Decimal('10.0'),
                        'booktransf': books[1].id,
                    }])],
            }])
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(len(books[1].lines), 0)
        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/05/2022|from|10.00 usd|Transfer USD <-- ' +
            'EUR [Book EURO | 0.00 € | Open]')
        self.assertEqual(books[0].lines[0].reference, None)
        self.assertEqual(len(books[0].lines[0].references), 0)
        self.assertEqual(books[0].lines[0].reconciliation, None)

        Lines.wfcheck([books[0].lines[0]])

        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(len(books[1].lines), 1)
        self.assertEqual(books[0].lines[0].reference, None)
        self.assertEqual(len(books[0].lines[0].references), 1)

        self.prep_valstore_run_worker()

        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/05/2022|from|10.00 usd|Transfer USD <-- ' +
            'EUR [Book EURO | -9.52 € | Open]')
        self.assertEqual(
            books[1].lines[0].rec_name,
            '05/05/2022|to|-9.52 €|Transfer USD <-- ' +
            'EUR [Book USD | 10.00 usd | Open]')
        self.assertEqual(books[0].balance, Decimal('10.0'))
        self.assertEqual(books[0].currency.rec_name, 'usd')
        self.assertEqual(books[1].balance, Decimal('-9.52'))
        self.assertEqual(books[1].currency.rec_name, 'Euro')

    @with_transaction()
    def test_line_check_transfer_2nd_currency_nocompany(self):
        """ create cashbook, lines, transfer amount between
            accounts with different currencies,
            both currencies are no company-currencies
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')
        Currency = pool.get('currency.currency')
        CurrencyRate = pool.get('currency.currency.rate')

        types = self.prep_type()
        company = self.prep_company()

        # add EURO, set company-currency to EURO
        (usd, euro) = self.prep_2nd_currency(company)
        # add CHF
        curr_chf, = Currency.create([{
            'name': 'Swiss Franc',
            'symbol': 'CHF',
            'code': 'CHF',
            'numeric_code': '756',
            'rounding': Decimal('0.01'),
            'digits': 2,
            }])
        CurrencyRate.create([{
            'date': date(2022, 5, 2),
            'currency': curr_chf.id,
            'rate': Decimal('1.04'),    # 1 € = 1.04 CHF @ 5/2/2022
            },])

        books = Book.create([{
            'name': 'Book CHF',
            'btype': types.id,
            'company': company.id,
            'currency': curr_chf.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }, {
            'name': 'Book USD',
            'btype': types.id,
            'company': company.id,
            'currency': usd.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }])
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].rec_name, 'Book CHF | 0.00 CHF | Open')
        self.assertEqual(books[1].rec_name, 'Book USD | 0.00 usd | Open')

        Book.write(*[
            [books[0]],
            {
                'lines': [('create', [{
                        'date': date(2022, 5, 5),
                        'description': 'Transfer CHF --> USD',
                        'bookingtype': 'mvout',
                        'amount': Decimal('10.0'),
                        'booktransf': books[1].id,
                    }])],
            }])
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(len(books[1].lines), 0)
        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/05/2022|to|-10.00 CHF|Transfer CHF --> ' +
            'USD [Book USD | 0.00 usd | Open]')
        self.assertEqual(books[0].lines[0].reference, None)
        self.assertEqual(len(books[0].lines[0].references), 0)
        self.assertEqual(books[0].lines[0].reconciliation, None)

        Lines.wfcheck([books[0].lines[0]])

        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(len(books[1].lines), 1)
        self.assertEqual(books[0].lines[0].reference, None)
        self.assertEqual(len(books[0].lines[0].references), 1)

        self.prep_valstore_run_worker()

        # 10 CHF --> USD: USD = CHF * 1.05 / 1.04
        # 10 CHF = 10.0961538 USD
        #  EUR | USD | CHF
        # -----+-----+-----  @ 05/02/2022
        #  1.00| 1.05| 1.04
        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/05/2022|to|-10.00 CHF|Transfer CHF --> ' +
            'USD [Book USD | 10.10 usd | Open]')
        self.assertEqual(
            books[1].lines[0].rec_name,
            '05/05/2022|from|10.10 usd|Transfer CHF --> ' +
            'USD [Book CHF | -10.00 CHF | Open]')
        self.assertEqual(books[0].balance, Decimal('-10.0'))
        self.assertEqual(books[0].currency.rec_name, 'Swiss Franc')
        self.assertEqual(books[1].balance, Decimal('10.10'))
        self.assertEqual(books[1].currency.rec_name, 'usd')

    @with_transaction()
    def test_line_check_balance_by_line(self):
        """ create cashbook, lines, reconciliations,
            check calculation of balance per line
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')
        Reconciliation = pool.get('cashbook.recon')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Text 1',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 2),
                    'description': 'Text 2',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 15),
                    'description': 'Text 3',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 17),
                    'description': 'Text 4',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            }])

        self.assertEqual(len(book.lines), 4)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(book.lines[0].balance, Decimal('1.0'))
        self.assertEqual(book.lines[0].reconciliation, None)
        self.assertEqual(book.lines[0].state, 'edit')
        self.assertEqual(book.lines[0].feature, 'gen')
        self.assertEqual(
            book.lines[1].rec_name,
            '05/02/2022|Rev|1.00 usd|Text 2 [Cat1]')
        self.assertEqual(book.lines[1].balance, Decimal('2.0'))
        self.assertEqual(book.lines[1].reconciliation, None)
        self.assertEqual(book.lines[1].state, 'edit')
        self.assertEqual(
            book.lines[2].rec_name,
            '05/15/2022|Rev|1.00 usd|Text 3 [Cat1]')
        self.assertEqual(book.lines[2].balance, Decimal('3.0'))
        self.assertEqual(book.lines[2].reconciliation, None)
        self.assertEqual(book.lines[2].state, 'edit')
        self.assertEqual(
            book.lines[3].rec_name,
            '05/17/2022|Rev|1.00 usd|Text 4 [Cat1]')
        self.assertEqual(book.lines[3].balance, Decimal('4.0'))
        self.assertEqual(book.lines[3].reconciliation, None)
        self.assertEqual(book.lines[3].state, 'edit')

        Lines.wfcheck([book.lines[0], book.lines[1]])
        recon, = Reconciliation.create([{
                'cashbook': book.id}])
        self.assertEqual(
            recon.rec_name,
            '05/01/2022 - 05/02/2022 | 0.00 usd - 0.00 usd [0]')

        Reconciliation.wfcheck([recon])
        self.assertEqual(
            recon.rec_name,
            '05/01/2022 - 05/02/2022 | 0.00 usd - 2.00 usd [2]')

        self.assertEqual(len(book.lines), 4)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(book.lines[0].balance, Decimal('1.0'))
        self.assertEqual(book.lines[0].reconciliation.id, recon.id)
        self.assertEqual(book.lines[0].state, 'check')
        self.assertEqual(
            book.lines[1].rec_name,
            '05/02/2022|Rev|1.00 usd|Text 2 [Cat1]')
        self.assertEqual(book.lines[1].balance, Decimal('2.0'))
        self.assertEqual(book.lines[1].reconciliation.id, recon.id)
        self.assertEqual(book.lines[1].state, 'check')
        self.assertEqual(
            book.lines[2].rec_name,
            '05/15/2022|Rev|1.00 usd|Text 3 [Cat1]')
        self.assertEqual(book.lines[2].balance, Decimal('3.0'))
        self.assertEqual(book.lines[2].reconciliation, None)
        self.assertEqual(book.lines[2].state, 'edit')
        self.assertEqual(
            book.lines[3].rec_name,
            '05/17/2022|Rev|1.00 usd|Text 4 [Cat1]')
        self.assertEqual(book.lines[3].balance, Decimal('4.0'))
        self.assertEqual(book.lines[3].reconciliation, None)
        self.assertEqual(book.lines[3].state, 'edit')

        Reconciliation.wfdone([recon])
        self.assertEqual(
            recon.rec_name,
            '05/01/2022 - 05/02/2022 | 0.00 usd - 2.00 usd [2]')

        self.assertEqual(len(book.lines), 4)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(book.lines[0].balance, Decimal('1.0'))
        self.assertEqual(book.lines[0].reconciliation.id, recon.id)
        self.assertEqual(book.lines[0].state, 'done')
        self.assertEqual(
            book.lines[1].rec_name,
            '05/02/2022|Rev|1.00 usd|Text 2 [Cat1]')
        self.assertEqual(book.lines[1].balance, Decimal('2.0'))
        self.assertEqual(book.lines[1].reconciliation.id, recon.id)
        self.assertEqual(book.lines[1].state, 'done')
        self.assertEqual(
            book.lines[2].rec_name,
            '05/15/2022|Rev|1.00 usd|Text 3 [Cat1]')
        self.assertEqual(book.lines[2].balance, Decimal('3.0'))
        self.assertEqual(book.lines[2].reconciliation, None)
        self.assertEqual(book.lines[2].state, 'edit')
        self.assertEqual(
            book.lines[3].rec_name,
            '05/17/2022|Rev|1.00 usd|Text 4 [Cat1]')
        self.assertEqual(book.lines[3].balance, Decimal('4.0'))
        self.assertEqual(book.lines[3].reconciliation, None)
        self.assertEqual(book.lines[3].state, 'edit')

    @with_transaction()
    def test_line_set_number_with_done(self):
        """ create cashbook + line, write number to line
            at state-change check->done
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')
        Reconciliation = pool.get('cashbook.recon')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        with Transaction().set_context({
                'company': company.id}):
            book, = Book.create([{
                'name': 'Book 1',
                'btype': types.id,
                'company': company.id,
                'currency': company.currency.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1),
                'number_atcheck': False,
                'lines': [('create', [{
                        'date': date(2022, 5, 1),
                        'description': 'Text 1',
                        'category': category.id,
                        'bookingtype': 'in',
                        'amount': Decimal('1.0'),
                        'party': party.id,
                    }, {
                        'date': date(2022, 5, 2),
                        'description': 'Text 2',
                        'category': category.id,
                        'bookingtype': 'in',
                        'amount': Decimal('1.0'),
                        'party': party.id,
                    }])],
                }])
            self.assertEqual(book.name, 'Book 1')
            self.assertEqual(book.btype.rec_name, 'CAS - Cash')
            self.assertEqual(book.state, 'open')
            self.assertEqual(book.number_atcheck, False)
            self.assertEqual(len(book.lines), 2)
            self.assertEqual(book.lines[0].date, date(2022, 5, 1))
            self.assertEqual(
                book.lines[0].rec_name,
                '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
            self.assertEqual(book.lines[0].state_cashbook, 'open')
            self.assertEqual(book.lines[1].date, date(2022, 5, 2))
            self.assertEqual(
                book.lines[1].rec_name,
                '05/02/2022|Rev|1.00 usd|Text 2 [Cat1]')

            # add reconciliation
            Book.write(*[
                [book],
                {
                    'reconciliations': [('create', [{
                        'date': date(2022, 5, 1),
                        'date_from': date(2022, 5, 1),
                        'date_to': date(2022, 5, 30),
                        }])],
                }])
            self.assertEqual(len(book.reconciliations), 1)
            self.assertEqual(len(book.reconciliations[0].lines), 0)
            self.assertEqual(
                book.reconciliations[0].date_from, date(2022, 5, 1))
            self.assertEqual(
                book.reconciliations[0].date_to, date(2022, 5, 30))
            self.assertEqual(book.reconciliations[0].state, 'edit')

            Lines.wfcheck(book.lines)
            self.assertEqual(book.lines[0].state, 'check')
            self.assertEqual(book.lines[0].number, None)
            self.assertEqual(book.lines[1].state, 'check')
            self.assertEqual(book.lines[1].number, None)

            Reconciliation.wfcheck(book.reconciliations)
            self.assertEqual(len(book.reconciliations[0].lines), 2)
            self.assertEqual(
                book.reconciliations[0].lines[0].rec_name,
                '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
            self.assertEqual(
                book.reconciliations[0].lines[1].rec_name,
                '05/02/2022|Rev|1.00 usd|Text 2 [Cat1]')
            self.assertEqual(book.reconciliations[0].lines[0].number, None)
            self.assertEqual(book.reconciliations[0].lines[1].number, None)

            Reconciliation.wfdone(book.reconciliations)
            self.assertEqual(book.reconciliations[0].lines[0].number, '1')
            self.assertEqual(book.reconciliations[0].lines[0].state, 'done')
            self.assertEqual(book.reconciliations[0].lines[1].number, '2')
            self.assertEqual(book.reconciliations[0].lines[1].state, 'done')

    @with_transaction()
    def test_line_create_check_names_search(self):
        """ create cashbook + line
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')
        Category = pool.get('cashbook.category')

        types = self.prep_type()
        company = self.prep_company()
        category = self.prep_category(cattype='in')
        category2, = Category.create([{
            'name': 'sp-cat1',
            'cattype': 'in',
            'company': company.id,
            }])
        self.assertEqual(category2.rec_name, 'sp-cat1')

        party = self.prep_party()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Text 1',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 2),
                    'description': 'Text 2',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 3),
                    'description': 'Text 3',
                    'bookingtype': 'spin',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                    'splitlines': [('create', [{
                        'amount': Decimal('1.0'),
                        'description': 'text3-spline1',
                        'category': category2.id,
                        }])],
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.btype.rec_name, 'CAS - Cash')
        self.assertEqual(book.state, 'open')
        self.assertEqual(len(book.lines), 3)
        self.assertEqual(book.lines[0].date, date(2022, 5, 1))
        self.assertEqual(
            book.lines[0].rec_name, '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(book.lines[0].state_cashbook, 'open')
        self.assertEqual(book.lines[1].date, date(2022, 5, 2))
        self.assertEqual(
            book.lines[1].rec_name, '05/02/2022|Rev|1.00 usd|Text 2 [Cat1]')
        self.assertEqual(book.lines[2].date, date(2022, 5, 3))
        self.assertEqual(
            book.lines[2].rec_name, '05/03/2022|Rev/Sp|1.00 usd|Text 3 [-]')

        self.assertEqual(
            Lines.search_count([('rec_name', '=', 'Text 1')]), 1)
        self.assertEqual(
            Lines.search_count([('rec_name', '=', 'Text 1a')]), 0)
        self.assertEqual(
            Lines.search_count([('rec_name', 'ilike', 'text%')]), 3)
        # search in category of split-line
        self.assertEqual(
            Lines.search_count([('rec_name', '=', 'sp-cat1')]), 1)
        # search in description of split-line
        self.assertEqual(
            Lines.search_count([('rec_name', '=', 'text3-spline1')]), 1)
        # ilike fails in fields.Text to find subtext...
        self.assertEqual(
            Lines.search_count([('rec_name', 'ilike', '%spline%')]), 0)
        # ...but it uses separator-chars
        self.assertEqual(
            Lines.search_count([('rec_name', 'ilike', 'text3%')]), 1)
        self.assertEqual(
            Lines.search_count([('rec_name', 'ilike', 'spline1')]), 1)
        self.assertEqual(
            Lines.search_count([('rec_name', 'ilike', '%spline1')]), 1)
        self.assertEqual(
            Lines.search_count([('rec_name', 'ilike', 'spline1%')]), 0)
        self.assertEqual(
            Lines.search_count([('rec_name', 'ilike', 'text3')]), 1)

        self.assertEqual(
            Lines.search_count([('state_cashbook', '=', 'open')]), 3)
        self.assertEqual(
            Lines.search_count([('state_cashbook', '=', 'closed')]), 0)
        self.assertEqual(
            Lines.search_count([('cashbook.state', '=', 'open')]), 3)
        self.assertEqual(
            Lines.search_count([('cashbook.state', '=', 'closed')]), 0)

        # sorting: date -> state -> id
        self.assertEqual(len(book.lines), 3)
        self.assertEqual(
            book.lines[0].rec_name, '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(book.lines[0].state, 'edit')
        self.assertEqual(
            book.lines[1].rec_name, '05/02/2022|Rev|1.00 usd|Text 2 [Cat1]')
        self.assertEqual(book.lines[1].state, 'edit')
        self.assertEqual(
            book.lines[2].rec_name, '05/03/2022|Rev/Sp|1.00 usd|Text 3 [-]')
        self.assertEqual(book.lines[2].state, 'edit')

        # set to same date
        Lines.write(*[
            list(book.lines),
            {
                'date': date(2022, 5, 1),
            }])
        # check again
        book, = Book.search([])
        self.assertEqual(
            book.lines[0].rec_name, '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(book.lines[0].state, 'edit')
        self.assertEqual(
            book.lines[1].rec_name, '05/01/2022|Rev|1.00 usd|Text 2 [Cat1]')
        self.assertEqual(book.lines[1].state, 'edit')
        self.assertEqual(
            book.lines[2].rec_name, '05/01/2022|Rev/Sp|1.00 usd|Text 3 [-]')
        self.assertEqual(book.lines[2].state, 'edit')

        # set to 'check', will sort first
        Lines.wfcheck([book.lines[1]])
        book, = Book.search([])
        self.assertEqual(
            book.lines[0].rec_name, '05/01/2022|Rev|1.00 usd|Text 2 [Cat1]')
        self.assertEqual(book.lines[0].state, 'check')
        self.assertEqual(
            book.lines[1].rec_name, '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(book.lines[1].state, 'edit')
        self.assertEqual(
            book.lines[2].rec_name, '05/01/2022|Rev/Sp|1.00 usd|Text 3 [-]')
        self.assertEqual(book.lines[2].state, 'edit')

    @with_transaction()
    def test_line_to_non_type_book(self):
        """ create cashbook w/o type
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        category = self.prep_category(cattype='in')
        company = self.prep_company()
        self.prep_party()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': None,
            'company': company.id,
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')

        self.assertRaisesRegex(
            UserError,
            r'The value "Book 1" for field "Cashbook" in "\d+" of ' +
            r'"Cashbook Line" is not valid according to its domain.',
            Line.create,
            [{
                'cashbook': book.id,
                'date': date(2022, 5, 1),
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('0.0'),
            }])

    @with_transaction()
    def test_line_check_deny_delete_of_party(self):
        """ create cashbook + line, delete party should fail
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Party = pool.get('party.party')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Text 1',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        self.assertEqual(len(book.lines), 1)
        self.assertEqual(book.lines[0].party.rec_name, 'Party')
        self.assertEqual(book.lines[0].party.id, party.id)

        self.assertEqual(Party.search_count([('name', '=', 'Party')]), 1)

        self.assertRaisesRegex(
            UserError,
            'The records could not be deleted because they are used by ' +
            'field "Party" of "Cashbook Line".',
            Party.delete,
            [party])

    @with_transaction()
    def test_line_create_check_deny_write(self):
        """ create cashbook + line, 'close' book, write to line
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Text 1',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 6, 1),
                    'description': 'Text 2',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        self.assertEqual(len(book.lines), 2)

        Line.write(*[
            [book.lines[0]],
            {
                'description': 'works',
            }])
        Line.wfcheck([book.lines[0]])
        self.assertEqual(book.lines[0].state, 'check')

        self.assertRaisesRegex(
            UserError,
            "The cashbook line '05/01/2022|1.00 usd|works [Cat1]' is " +
            "'Checked' and cannot be changed.",
            Line.write,
            *[
                [book.lines[0]],
                {
                    'description': 'denied by line.state',
                },
            ])

        Book.wfclosed([book])
        self.assertEqual(book.state, 'closed')

        self.assertRaisesRegex(
            UserError,
            "The cash book 'Book | 2.00 usd | Closed' is 'Closed' " +
            "and cannot be changed.",
            Line.write,
            *[
                [book.lines[0]],
                {
                    'description': 'should be denied',
                },
            ])

    @with_transaction()
    def test_line_create_check_month(self):
        """ create cashbook + line, check 'month' + search
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')
        IrDate = pool.get('ir.date')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        IrDate.today = MagicMock(return_value=date(2022, 6, 1))

        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Text 1',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 6, 1),
                    'description': 'Text 2',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        self.assertEqual(len(book.lines), 2)
        self.assertEqual(book.lines[0].date, date(2022, 5, 1))
        self.assertEqual(book.lines[0].month, 1)
        self.assertEqual(book.lines[1].date, date(2022, 6, 1))
        self.assertEqual(book.lines[1].month, 0)

        l1, = Line.search([('month', '=', 0)])
        self.assertEqual(l1.date, date(2022, 6, 1))
        l1, = Line.search([('month', '=', 1)])
        self.assertEqual(l1.date, date(2022, 5, 1))

        IrDate.today = MagicMock(return_value=date(2022, 6, 30))

        l1, = Line.search([('month', '=', 0)])
        self.assertEqual(l1.date, date(2022, 6, 1))
        l1, = Line.search([('month', '=', 1)])
        self.assertEqual(l1.date, date(2022, 5, 1))

        self.assertEqual(Line.search_count([('month', '=', 2)]), 0)

        IrDate.today = MagicMock(return_value=date(2022, 7, 1))

        self.assertEqual(Line.search_count([('month', '=', 0)]), 0)
        l1, = Line.search([('month', '=', 1)])
        self.assertEqual(l1.date, date(2022, 6, 1))

        IrDate.today = MagicMock(return_value=date.today())

    @with_transaction()
    def test_line_check_bookingtype_mvout(self):
        """ create cashbook + line, bookingtype 'mvout'
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        types = self.prep_type()
        self.prep_category(cattype='in')
        category_out = self.prep_category(name='Out Category', cattype='out')
        company = self.prep_company()
        self.prep_party()

        book2, = Book.create([{
            'name': 'Book 2',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }])

        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Transfer Out',
                    'category': category_out.id,
                    'bookingtype': 'mvout',
                    'amount': Decimal('1.0'),
                    'booktransf': book2.id,
                }])],
            }])
        self.assertEqual(book.rec_name, 'Book 1 | -1.00 usd | Open')
        self.assertEqual(len(book.lines), 1)
        self.assertEqual(len(book2.lines), 0)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|to|-1.00 usd|Transfer Out [Book 2 | 0.00 usd | Open]')
        self.assertEqual(len(book.lines[0].references), 0)

        # check counterpart
        self.assertEqual(
            book.lines[0].booktransf.rec_name,
            'Book 2 | 0.00 usd | Open')
        self.assertEqual(book.lines[0].booktransf.btype.feature, 'gen')
        self.assertEqual(book.lines[0].booktransf_feature, 'gen')

        # check payee
        self.assertEqual(
            book.lines[0].payee.rec_name, 'Book 2 | 0.00 usd | Open')
        self.assertEqual(Line.search_count([('payee', 'ilike', 'book 2%')]), 1)

        # set line to 'checked', this creates the counterpart
        Line.wfcheck(list(book.lines))

        self.prep_valstore_run_worker()

        self.assertEqual(len(book.lines), 1)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|to|-1.00 usd|Transfer Out [Book 2 | 1.00 usd | Open]')
        self.assertEqual(book.lines[0].state, 'check')
        self.assertEqual(len(book.lines[0].references), 1)
        self.assertEqual(book.lines[0].reference, None)
        self.assertEqual(book.lines[0].references[0].id, book2.lines[0].id)

        self.assertEqual(len(book2.lines), 1)
        self.assertEqual(
            book2.lines[0].rec_name,
            '05/01/2022|from|1.00 usd|Transfer Out [Book 1 | -1.00 usd | Open]')
        self.assertEqual(book2.lines[0].state, 'check')
        self.assertEqual(
            book2.lines[0].reference.rec_name,
            '05/01/2022|to|-1.00 usd|Transfer Out [Book 2 | 1.00 usd | Open]')
        self.assertEqual(len(book2.lines[0].references), 0)

    @with_transaction()
    def test_line_check_bookingtype_mvin(self):
        """ create cashbook + line, bookingtype 'mvin'
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        types = self.prep_type()
        category_in = self.prep_category(cattype='in')
        self.prep_category(name='Out Category', cattype='out')
        company = self.prep_company()
        self.prep_party()

        book2, = Book.create([{
            'name': 'Book 2',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }])

        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Transfer In',
                    'category': category_in.id,
                    'bookingtype': 'mvin',
                    'amount': Decimal('1.0'),
                    'booktransf': book2.id,
                }])],
            }])
        self.assertEqual(book.rec_name, 'Book 1 | 1.00 usd | Open')
        self.assertEqual(len(book.lines), 1)
        self.assertEqual(len(book2.lines), 0)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|from|1.00 usd|Transfer In [Book 2 | 0.00 usd | Open]')
        self.assertEqual(len(book.lines[0].references), 0)

        # set line to 'checked', this creates the counterpart
        Line.wfcheck(list(book.lines))

        self.prep_valstore_run_worker()

        self.assertEqual(len(book.lines), 1)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|from|1.00 usd|Transfer In [Book 2 | -1.00 usd | Open]')
        self.assertEqual(book.lines[0].state, 'check')
        self.assertEqual(len(book.lines[0].references), 1)
        self.assertEqual(book.lines[0].reference, None)
        self.assertEqual(book.lines[0].references[0].id, book2.lines[0].id)

        self.assertEqual(len(book2.lines), 1)
        self.assertEqual(
            book2.lines[0].rec_name,
            '05/01/2022|to|-1.00 usd|Transfer In [Book 1 | 1.00 usd | Open]')
        self.assertEqual(book2.lines[0].state, 'check')
        self.assertEqual(
            book2.lines[0].reference.rec_name,
            '05/01/2022|from|1.00 usd|Transfer In [Book 2 | -1.00 usd | Open]')
        self.assertEqual(len(book2.lines[0].references), 0)

        # tryt wfedit to 'book2.lines[0]'
        self.assertRaisesRegex(
            UserError,
            "The current line is managed by the cashbook line " +
            "'05/01/2022|from|1.00 usd|Transfer In [Book 2 | -1.00 usd " +
            "| Open]', cashbook: 'Book 1 | 1.00 usd | Open'.",
            Line.wfedit,
            [book2.lines[0]])

        Line.wfedit([book.lines[0]])
        self.assertEqual(len(book2.lines), 0)

    @with_transaction()
    def test_line_create_check_debit_credit(self):
        """ create cashbook + line, check calculation of debit/credit
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        types = self.prep_type()
        category_in = self.prep_category(cattype='in')
        category_out = self.prep_category(name='Out Category', cattype='out')
        company = self.prep_company()
        party = self.prep_party()

        book2, = Book.create([{
            'name': 'Book 2',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }])

        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Revenue',
                    'category': category_in.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 6, 1),
                    'description': 'Expense',
                    'category': category_out.id,
                    'bookingtype': 'out',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 6, 1),
                    'description': 'Transfer from',
                    'category': category_in.id,
                    'bookingtype': 'mvin',
                    'amount': Decimal('1.0'),
                    'booktransf': book2.id,
                }, {
                    'date': date(2022, 6, 1),
                    'description': 'Transfer to',
                    'category': category_out.id,
                    'bookingtype': 'mvout',
                    'amount': Decimal('1.0'),
                    'booktransf': book2.id,
                }, {
                    'date': date(2022, 6, 1),       # in-category, return
                    'description': 'in-return',     # amount negative
                    'category': category_in.id,
                    'bookingtype': 'in',
                    'amount': Decimal('-1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 6, 1),       # out-category, return
                    'description': 'out-return',    # amount negative
                    'category': category_out.id,
                    'bookingtype': 'out',
                    'amount': Decimal('-1.0'),
                    'party': party.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        self.assertEqual(len(book.lines), 6)

        self.assertEqual(book.lines[0].amount, Decimal('1.0'))
        self.assertEqual(book.lines[0].bookingtype, 'in')
        self.assertEqual(book.lines[0].credit, Decimal('1.0'))
        self.assertEqual(book.lines[0].debit, Decimal('0.0'))

        # check payee
        self.assertEqual(book.lines[0].payee.rec_name, 'Party')
        self.assertEqual(Line.search_count([('payee', 'ilike', 'party%')]), 4)
        self.assertEqual(Line.search_count([('payee', 'ilike', 'book%')]), 2)

        self.assertEqual(book.lines[1].amount, Decimal('1.0'))
        self.assertEqual(book.lines[1].bookingtype, 'out')
        self.assertEqual(book.lines[1].credit, Decimal('0.0'))
        self.assertEqual(book.lines[1].debit, Decimal('1.0'))

        self.assertEqual(book.lines[2].amount, Decimal('1.0'))
        self.assertEqual(book.lines[2].bookingtype, 'mvin')
        self.assertEqual(book.lines[2].credit, Decimal('1.0'))
        self.assertEqual(book.lines[2].debit, Decimal('0.0'))

        self.assertEqual(book.lines[3].amount, Decimal('1.0'))
        self.assertEqual(book.lines[3].bookingtype, 'mvout')
        self.assertEqual(book.lines[3].credit, Decimal('0.0'))
        self.assertEqual(book.lines[3].debit, Decimal('1.0'))

        self.assertEqual(book.lines[4].amount, Decimal('-1.0'))
        self.assertEqual(book.lines[4].bookingtype, 'in')
        self.assertEqual(book.lines[4].credit, Decimal('-1.0'))
        self.assertEqual(book.lines[4].debit, Decimal('0.0'))

        self.assertEqual(book.lines[5].amount, Decimal('-1.0'))
        self.assertEqual(book.lines[5].bookingtype, 'out')
        self.assertEqual(book.lines[5].credit, Decimal('0.0'))
        self.assertEqual(book.lines[5].debit, Decimal('-1.0'))

        Line.write(*[
            [book.lines[0]],
            {
                'amount': Decimal('2.0'),
            }])
        self.assertEqual(book.lines[0].amount, Decimal('2.0'))
        self.assertEqual(book.lines[0].bookingtype, 'in')
        self.assertEqual(book.lines[0].credit, Decimal('2.0'))
        self.assertEqual(book.lines[0].debit, Decimal('0.0'))

        Line.write(*[
            [book.lines[0]],
            {
                'bookingtype': 'out',
                'category': category_out.id,
            }])
        self.assertEqual(book.lines[0].amount, Decimal('2.0'))
        self.assertEqual(book.lines[0].bookingtype, 'out')
        self.assertEqual(book.lines[0].credit, Decimal('0.0'))
        self.assertEqual(book.lines[0].debit, Decimal('2.0'))

        Line.write(*[
            [book.lines[0]],
            {
                'category': category_in.id,
                'bookingtype': 'mvin',
                'amount': Decimal('3.0'),
                'booktransf': book2.id,
            }])
        self.assertEqual(book.lines[0].amount, Decimal('3.0'))
        self.assertEqual(book.lines[0].bookingtype, 'mvin')
        self.assertEqual(book.lines[0].credit, Decimal('3.0'))
        self.assertEqual(book.lines[0].debit, Decimal('0.0'))

    @with_transaction()
    def test_line_create_check_category_view(self):
        """ create cashbook + line, check 'category_view'
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Configuration = pool.get('cashbook.configuration')
        Category = pool.get('cashbook.category')

        types = self.prep_type()
        self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()

        with Transaction().set_context({
                'company': company.id}):

            category2, = Category.create([{
                'company': company.id,
                'name': 'Level1',
                'cattype': 'in',
                'childs': [('create', [{
                    'company': company.id,
                    'name': 'Level2',
                    'cattype': 'in',
                    }])],
                }])
            self.assertEqual(category2.rec_name, 'Level1')
            self.assertEqual(len(category2.childs), 1)
            self.assertEqual(category2.childs[0].rec_name, 'Level1/Level2')

            cfg1 = Configuration()
            cfg1.save()

            book, = Book.create([{
                'name': 'Book 1',
                'btype': types.id,
                'company': company.id,
                'currency': company.currency.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1),
                'lines': [('create', [{
                        'date': date(2022, 5, 1),
                        'description': 'Text 1',
                        'category': category2.id,
                        'bookingtype': 'in',
                        'amount': Decimal('1.0'),
                        'party': party.id,
                    }, {
                        'date': date(2022, 6, 1),
                        'description': 'Text 2',
                        'category': category2.childs[0].id,
                        'bookingtype': 'in',
                        'amount': Decimal('1.0'),
                        'party': party.id,
                    }])],
                }])
            self.assertEqual(book.name, 'Book 1')
            self.assertEqual(book.state, 'open')
            self.assertEqual(len(book.lines), 2)

            self.assertEqual(cfg1.catnamelong, True)

            self.assertEqual(book.lines[0].category.rec_name, 'Level1')
            self.assertEqual(book.lines[1].category.rec_name, 'Level1/Level2')
            self.assertEqual(book.lines[0].category_view, 'Level1')
            self.assertEqual(book.lines[1].category_view, 'Level1/Level2')

            cfg1.catnamelong = False
            cfg1.save()
            self.assertEqual(book.lines[0].category.rec_name, 'Level1')
            self.assertEqual(book.lines[1].category.rec_name, 'Level1/Level2')
            self.assertEqual(book.lines[0].category_view, 'Level1')
            self.assertEqual(book.lines[1].category_view, 'Level2')

    @with_transaction()
    def test_line_delete_with_book_in_open_state(self):
        """ create cashbook + line, book in state=open, delete a line
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'start_date': date(2022, 5, 1),
            'number_sequ': self.prep_sequence().id,
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Text 1',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 2),
                    'description': 'Text 2',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(len(book.lines), 2)
        self.assertEqual(book.state, 'open')

        Lines.delete([book.lines[0]])

    @with_transaction()
    def test_line_delete_with_book_in_closed_state(self):
        """ create cashbook + line, book in state=closed, delete a line
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Text 1',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 2),
                    'description': 'Text 2',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(len(book.lines), 2)
        self.assertEqual(book.state, 'open')
        Book.wfclosed([book])
        self.assertEqual(book.state, 'closed')

        self.assertRaisesRegex(
            UserError,
            "The cashbook line '05/01/2022 Text 1' cannot be deleted " +
            "because the Cashbook 'Book | 2.00 usd | Closed' is" +
            " in state 'Closed'.",
            Lines.delete,
            [book.lines[0]])

    @with_transaction()
    def test_line_delete_with_line_in_check_state(self):
        """ create cashbook + line, line in state=check, delete a line
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Text 1',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 2),
                    'description': 'Text 2',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(len(book.lines), 2)
        self.assertEqual(book.state, 'open')

        self.assertEqual(book.lines[0].state, 'edit')
        Lines.wfcheck([book.lines[0]])
        self.assertEqual(book.lines[0].state, 'check')

        self.assertRaisesRegex(
            UserError,
            "The cashbook line '05/01/2022|1.00 usd|Test 1 [Cat1]' " +
            "cannot be deleted, its in state 'Checked'.",
            Lines.delete,
            [book.lines[0]])

    @with_transaction()
    def test_line_permission_owner(self):
        """ create book+line + 2x users, add users to group, check access
        """
        pool = Pool()
        ResUser = pool.get('res.user')
        ResGroup = pool.get('res.group')
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        grp_cashbook, = ResGroup.search([('name', '=', 'Cashbook')])
        usr_lst = ResUser.create([{
            'login': 'frida',
            'name': 'Frida',
            'groups': [('add', [grp_cashbook.id])],
            'companies': [('add', [company.id])],
            'company': company.id,
            }, {
            'login': 'diego',
            'name': 'Diego',
            'groups': [('add', [grp_cashbook.id])],
            'companies': [('add', [company.id])],
            'company': company.id,
            }])
        self.assertEqual(len(usr_lst), 2)
        self.assertEqual(usr_lst[0].name, 'Frida')
        self.assertEqual(usr_lst[1].name, 'Diego')

        book, = Book.create([{
            'name': 'Fridas book',
            'owner': usr_lst[0].id,
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                'date': date(2022, 5, 1),
                'description': 'Test 1',
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('1.0'),
                'party': party.id,
                }])],
            }])
        self.assertEqual(book.rec_name, 'Fridas book | 1.00 usd | Open'),
        self.assertEqual(book.owner.rec_name, 'Frida'),

        with Transaction().set_context({
                '_check_access': True}):
            # change to user 'diego' , try access
            with Transaction().set_user(usr_lst[1].id):
                lines = Line.search([])
                self.assertEqual(len(lines), 0)

            # change to user 'frida' read/write book
            with Transaction().set_user(usr_lst[0].id):
                lines = Line.search([])
                self.assertEqual(len(lines), 1)
                self.assertEqual(
                    lines[0].cashbook.rec_name,
                    'Fridas book | 1.00 usd | Open')
                self.assertEqual(
                    lines[0].rec_name,
                    '05/01/2022|Rev|1.00 usd|Test 1 [Cat1]')

                Line.write(*[
                    lines,
                    {
                        'description': 'Test 2',
                    }])
                self.assertEqual(
                    lines[0].rec_name,
                    '05/01/2022|Rev|1.00 usd|Test 2 [Cat1]')
                self.assertEqual(
                    lines[0].owner_cashbook.rec_name, 'Frida')

    @with_transaction()
    def test_line_permission_reviewer(self):
        """ create book+line + 2x users + 1x reviewer-group,
            add users to group, check access
        """
        pool = Pool()
        ResUser = pool.get('res.user')
        ResGroup = pool.get('res.group')
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        grp_cashbook, = ResGroup.search([('name', '=', 'Cashbook')])
        grp_reviewer, = ResGroup.create([{
            'name': 'Cashbook Reviewer',
            }])

        usr_lst = ResUser.create([{
            'login': 'frida',
            'name': 'Frida',
            'groups': [('add', [grp_cashbook.id])],
            'companies': [('add', [company.id])],
            'company': company.id,
            }, {
            'login': 'diego',
            'name': 'Diego',
            'groups': [('add', [grp_cashbook.id, grp_reviewer.id])],
            'companies': [('add', [company.id])],
            'company': company.id,
            }])
        self.assertEqual(len(usr_lst), 2)
        self.assertEqual(usr_lst[0].name, 'Frida')
        self.assertEqual(usr_lst[1].name, 'Diego')

        # create cashbook
        # add reviewer-group to allow write for users in group
        book, = Book.create([{
            'name': 'Fridas book',
            'owner': usr_lst[0].id,
            'reviewer': grp_reviewer.id,
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                'date': date(2022, 5, 1),
                'description': 'Test 1',
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('1.0'),
                'party': party.id,
                }])],
            }])
        self.assertEqual(book.rec_name, 'Fridas book | 1.00 usd | Open'),
        self.assertEqual(book.owner.rec_name, 'Frida'),

        with Transaction().set_context({
                '_check_access': True}):
            # change to user 'diego' , try access
            with Transaction().set_user(usr_lst[1].id):
                lines = Line.search([])
                self.assertEqual(len(lines), 1)
                self.assertEqual(len(lines[0].cashbook.reviewer.users), 1)
                self.assertEqual(
                    lines[0].cashbook.reviewer.users[0].rec_name,
                    'Diego')
                self.assertEqual(
                    lines[0].rec_name,
                    '05/01/2022|Rev|1.00 usd|Test 1 [Cat1]')
                Line.write(*[
                    lines,
                    {
                        'description': 'Test 2',
                    }])
                self.assertEqual(
                    lines[0].rec_name,
                    '05/01/2022|Rev|1.00 usd|Test 2 [Cat1]')

            # change to user 'frida' read/write line
            with Transaction().set_user(usr_lst[0].id):
                lines = Line.search([])
                self.assertEqual(len(lines), 1)
                self.assertEqual(
                    lines[0].rec_name,
                    '05/01/2022|Rev|1.00 usd|Test 2 [Cat1]')
                Line.write(*[
                    lines,
                    {
                        'description': 'Test 3',
                    }])
                self.assertEqual(
                    lines[0].rec_name,
                    '05/01/2022|Rev|1.00 usd|Test 3 [Cat1]')

    @with_transaction()
    def test_line_permission_observer(self):
        """ create book+line + 2x users + 1x observer-group,
            add users to group, check access
        """
        pool = Pool()
        ResUser = pool.get('res.user')
        ResGroup = pool.get('res.group')
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        grp_cashbook, = ResGroup.search([('name', '=', 'Cashbook')])
        grp_observer, = ResGroup.create([{
            'name': 'Cashbook Observer',
            }])

        usr_lst = ResUser.create([{
            'login': 'frida',
            'name': 'Frida',
            'groups': [('add', [grp_cashbook.id])],
            'companies': [('add', [company.id])],
            'company': company.id,
            }, {
            'login': 'diego',
            'name': 'Diego',
            'groups': [('add', [grp_cashbook.id, grp_observer.id])],
            'companies': [('add', [company.id])],
            'company': company.id,
            }])
        self.assertEqual(len(usr_lst), 2)
        self.assertEqual(usr_lst[0].name, 'Frida')
        self.assertEqual(usr_lst[1].name, 'Diego')

        # create cashbook
        # add reviewer-group to allow write for users in group
        book, = Book.create([{
            'name': 'Fridas book',
            'owner': usr_lst[0].id,
            'observer': grp_observer.id,
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                'date': date(2022, 5, 1),
                'description': 'Test 1',
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('1.0'),
                'party': party.id,
                }])],
            }])
        self.assertEqual(book.rec_name, 'Fridas book | 1.00 usd | Open'),
        self.assertEqual(book.owner.rec_name, 'Frida'),

        with Transaction().set_context({
                '_check_access': True}):
            # change to user 'diego' , try access
            with Transaction().set_user(usr_lst[1].id):
                lines = Line.search([])
                self.assertEqual(len(lines), 1)
                self.assertEqual(len(lines[0].cashbook.observer.users), 1)
                self.assertEqual(
                    lines[0].cashbook.observer.users[0].rec_name,
                    'Diego')
                self.assertEqual(
                    lines[0].rec_name,
                    '05/01/2022|Rev|1.00 usd|Test 1 [Cat1]')

                self.assertRaisesRegex(
                    UserError,
                    'You are not allowed to write to records ' +
                    '"[0-9]{1,}" of "Cashbook Line" because of at least ' +
                    'one of these rules:\nOwners and reviewers: ' +
                    'Cashbook line write - ',
                    Line.write,
                    *[
                        lines,
                        {
                            'description': 'Test 2',
                        },
                    ])

            # change to user 'frida' read/write line
            with Transaction().set_user(usr_lst[0].id):
                lines = Line.search([])
                self.assertEqual(len(lines), 1)
                self.assertEqual(
                    lines[0].rec_name,
                    '05/01/2022|Rev|1.00 usd|Test 1 [Cat1]')
                Line.write(*[
                    lines,
                    {
                        'description': 'Test 2',
                    }])
                self.assertEqual(
                    lines[0].rec_name,
                    '05/01/2022|Rev|1.00 usd|Test 2 [Cat1]')

# end LineTestCase
