# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock


class BookingWizardTestCase(object):
    """ test booking wizard
    """
    @with_transaction()
    def test_bookwiz_expense(self):
        """ run booking-wizard to store expense
        """
        pool = Pool()
        BookingWiz = pool.get('cashbook.enterbooking', type='wizard')
        Book = pool.get('cashbook.book')
        Category = pool.get('cashbook.category')
        Party = pool.get('party.party')
        IrDate = pool.get('ir.date')
        Config = pool.get('cashbook.configuration')

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            types = self.prep_type()
            book, = Book.create([{
                'name': 'Cash Book',
                'btype': types.id,
                'company': company.id,
                'currency': company.currency.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 1, 1),
                }])

            party, = Party.create([{
                'name': 'Foodshop Zehlendorf',
                'addresses': [('create', [{}])],
                }])

            categories = Category.create([{
                    'name': 'Income',
                    'cattype': 'in',
                }, {
                    'name': 'Food',
                    'cattype': 'out',
                }])

            cfg1 = Config()
            cfg1.fixate = True
            cfg1.save()

            (sess_id, start_state, end_state) = BookingWiz.create()
            w_obj = BookingWiz(sess_id)
            self.assertEqual(start_state, 'start')
            self.assertEqual(end_state, 'end')

            result = BookingWiz.execute(sess_id, {}, start_state)
            self.assertEqual(list(result.keys()), ['view'])
            self.assertEqual(result['view']['defaults']['bookingtype'], 'out')
            self.assertEqual(result['view']['defaults']['cashbook'], None)
            self.assertEqual(result['view']['defaults']['amount'], None)
            self.assertEqual(result['view']['defaults']['party'], None)
            self.assertEqual(result['view']['defaults']['booktransf'], None)
            self.assertEqual(result['view']['defaults']['description'], None)
            self.assertEqual(result['view']['defaults']['category'], None)
            self.assertEqual(result['view']['defaults']['fixate'], True)
            self.assertEqual(result['view']['defaults']['date'], date.today())

            self.assertEqual(len(book.lines), 0)

            r1 = {
                'amount': Decimal('10.0'),
                'cashbook': book.id,
                'party': party.id,
                'description': 'Test 1',
                'category': categories[1].id,
                'bookingtype': 'out',
                'date': date(2022, 5, 1),
                'fixate': True}
            for x in r1.keys():
                setattr(w_obj.start, x, r1[x])

            IrDate.today = MagicMock(return_value=date(2022, 5, 1))
            result = BookingWiz.execute(sess_id, {'start': r1}, 'save_')
            BookingWiz.delete(sess_id)
            IrDate.today = MagicMock(return_value=date.today())

            self.assertEqual(len(book.lines), 1)
            self.assertEqual(
                book.lines[0].rec_name,
                '05/01/2022|Exp|-10.00 usd|Test 1 [Food]')
            self.assertEqual(book.lines[0].state, 'check')

    @with_transaction()
    def test_bookwiz_transfer(self):
        """ run booking-wizard to store expense
        """
        pool = Pool()
        BookingWiz = pool.get('cashbook.enterbooking', type='wizard')
        Book = pool.get('cashbook.book')
        Category = pool.get('cashbook.category')
        Party = pool.get('party.party')
        IrDate = pool.get('ir.date')

        company = self.prep_company()
        with Transaction().set_context({
                'company': company.id}):
            types = self.prep_type()
            books = Book.create([{
                'name': 'Cash Book',
                'btype': types.id,
                'company': company.id,
                'currency': company.currency.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 1, 1),
                }, {
                'name': 'Bank',
                'btype': types.id,
                'company': company.id,
                'currency': company.currency.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 1, 1),
                }])

            party, = Party.create([{
                'name': 'Foodshop Zehlendorf',
                'addresses': [('create', [{}])],
                }])

            Category.create([{
                    'name': 'Income',
                    'cattype': 'in',
                }, {
                    'name': 'Food',
                    'cattype': 'out',
                }])

            (sess_id, start_state, end_state) = BookingWiz.create()
            w_obj = BookingWiz(sess_id)
            self.assertEqual(start_state, 'start')
            self.assertEqual(end_state, 'end')

            result = BookingWiz.execute(sess_id, {}, start_state)
            self.assertEqual(list(result.keys()), ['view'])
            self.assertEqual(result['view']['defaults']['bookingtype'], 'out')
            self.assertEqual(result['view']['defaults']['cashbook'], None)
            self.assertEqual(result['view']['defaults']['amount'], None)
            self.assertEqual(result['view']['defaults']['party'], None)
            self.assertEqual(result['view']['defaults']['booktransf'], None)
            self.assertEqual(result['view']['defaults']['description'], None)
            self.assertEqual(result['view']['defaults']['category'], None)
            self.assertEqual(result['view']['defaults']['fixate'], False)

            self.assertEqual(len(books[0].lines), 0)
            self.assertEqual(len(books[1].lines), 0)

            r1 = {
                'amount': Decimal('10.0'),
                'cashbook': books[0].id,
                'description': 'Test 1',
                'booktransf': books[1].id,
                'bookingtype': 'mvout',
                'date': date(2022, 5, 1),
                'fixate': False}
            for x in r1.keys():
                setattr(w_obj.start, x, r1[x])

            IrDate.today = MagicMock(return_value=date(2022, 5, 1))
            result = BookingWiz.execute(sess_id, {'start': r1}, 'save_')
            BookingWiz.delete(sess_id)
            IrDate.today = MagicMock(return_value=date.today())

            self.assertEqual(len(books[0].lines), 1)
            self.assertEqual(len(books[1].lines), 0)
            self.assertEqual(
                books[0].lines[0].rec_name,
                '05/01/2022|to|-10.00 usd|Test 1 [Bank | 0.00 usd | Open]')

# end BookingWizardTestCase
