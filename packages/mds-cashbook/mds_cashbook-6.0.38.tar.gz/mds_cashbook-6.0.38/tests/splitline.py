# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from datetime import date
from decimal import Decimal


class SplitLineTestCase(object):
    """ test split lines
    """

    @with_transaction()
    def test_splitline_in_category(self):
        """ add book, check splitbooking - incoming
        """
        pool = Pool()
        Book = pool.get('cashbook.book')

        types = self.prep_type()
        category1 = self.prep_category(cattype='in')
        company = self.prep_company()
        self.prep_party()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }])
        self.assertEqual(book.rec_name, 'Book 1 | 0.00 usd | Open')
        self.assertEqual(len(book.lines), 0)

        Book.write(*[
            [book],
            {
                'lines': [('create', [{
                    'bookingtype': 'spin',
                    'date': date(2022, 5, 1),
                    'splitlines': [('create', [{
                        'amount': Decimal('5.0'),
                        'splittype': 'cat',
                        'description': 'from category',
                        'category': category1.id,
                        }, {
                        'amount': Decimal('6.0'),
                        'splittype': 'cat',
                        'description': 'from cashbook',
                        'category': category1.id,
                        }])],
                    }])],
            }])
        self.assertEqual(len(book.lines), 1)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|Rev/Sp|11.00 usd|- [-]')
        self.assertEqual(book.lines[0].category, None)
        self.assertEqual(len(book.lines[0].splitlines), 2)

        self.assertEqual(book.lines[0].splitlines[0].feature, 'gen')
        self.assertEqual(book.lines[0].splitlines[0].booktransf_feature, None)
        self.assertEqual(book.lines[0].splitlines[1].feature, 'gen')
        self.assertEqual(book.lines[0].splitlines[1].booktransf_feature, None)

        self.assertEqual(
            book.lines[0].splitlines[0].rec_name,
            'Rev/Sp|5.00 usd|from category [Cat1]')
        self.assertEqual(
            book.lines[0].splitlines[1].rec_name,
            'Rev/Sp|6.00 usd|from cashbook [Cat1]')

        # check function fields
        self.assertEqual(
            book.lines[0].splitlines[0].category_view,
            'Cat1')
        self.assertEqual(book.lines[0].splitlines[0].date, date(2022, 5, 1))
        self.assertEqual(book.lines[0].splitlines[0].target.rec_name, 'Cat1')
        self.assertEqual(book.lines[0].splitlines[0].currency.rec_name, 'usd')
        self.assertEqual(book.lines[0].splitlines[0].currency_digits, 2)
        self.assertEqual(book.lines[0].splitlines[0].bookingtype, 'spin')
        self.assertEqual(book.lines[0].splitlines[0].state, 'edit')
        self.assertEqual(
            book.lines[0].splitlines[0].cashbook.rec_name,
            'Book 1 | 11.00 usd | Open')
        self.assertEqual(book.lines[0].splitlines[0].feature, 'gen')
        self.assertEqual(book.lines[0].splitlines[0].booktransf_feature, None)
        self.assertEqual(book.lines[0].splitlines[0].state_cashbook, 'open')
        self.assertEqual(
            book.lines[0].splitlines[0].owner_cashbook.rec_name,
            'Administrator')

    @with_transaction()
    def test_splitline_category_and_transfer(self):
        """ add book, line, two split-lines,
            category + transfer
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        types = self.prep_type()
        category1 = self.prep_category(cattype='in')
        company = self.prep_company()
        party = self.prep_party()
        books = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Text 1',
                    'category': category1.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            }, {
            'name': 'Book 2',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }])
        self.assertEqual(books[0].rec_name, 'Book 1 | 1.00 usd | Open')
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(books[1].rec_name, 'Book 2 | 0.00 usd | Open')

        Book.write(*[
            [books[0]],
            {
                'lines': [('write', [books[0].lines[0]], {
                    'bookingtype': 'spin',
                    'splitlines': [('create', [{
                        'amount': Decimal('5.0'),
                        'splittype': 'cat',
                        'description': 'from category',
                        'category': category1.id,
                        }, {
                        'amount': Decimal('6.0'),
                        'splittype': 'tr',
                        'description': 'from cashbook',
                        'booktransf': books[1].id,
                        }])],
                    })]
            }])
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/01/2022|Rev/Sp|11.00 usd|Text 1 [-]')
        self.assertEqual(books[0].lines[0].category, None)
        self.assertEqual(len(books[0].lines[0].splitlines), 2)
        self.assertEqual(
            books[0].lines[0].splitlines[0].rec_name,
            'Rev/Sp|5.00 usd|from category [Cat1]')
        self.assertEqual(
            books[0].lines[0].splitlines[1].rec_name,
            'Rev/Sp|6.00 usd|from cashbook [Book 2 | 0.00 usd | Open]')
        self.assertEqual(len(books[1].lines), 0)
        self.assertEqual(books[0].lines[0].splitlines[0].feature, 'gen')

        self.assertEqual(books[0].lines[0].splitlines[0].feature, 'gen')
        self.assertEqual(
            books[0].lines[0].splitlines[0].booktransf_feature, None)
        self.assertEqual(books[0].lines[0].splitlines[1].feature, 'gen')
        self.assertEqual(
            books[0].lines[0].splitlines[1].booktransf_feature, 'gen')

        # wf: edit -> check
        Line.wfcheck(books[0].lines)
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(books[0].lines[0].state, 'check')
        self.assertEqual(books[0].lines[0].number, '1')
        self.assertEqual(len(books[0].lines[0].references), 1)
        self.assertEqual(
            books[0].lines[0].references[0].rec_name,
            '05/01/2022|to|-6.00 usd|from cashbook [Book 1 | 11.00 usd | Open]')

        self.assertEqual(len(books[1].lines), 1)
        self.assertEqual(
            books[1].lines[0].reference.rec_name,
            '05/01/2022|Rev/Sp|11.00 usd|Text 1 [-]')
        self.assertEqual(
            books[1].lines[0].rec_name,
            '05/01/2022|to|-6.00 usd|from cashbook [Book 1 | 11.00 usd | Open]')

        # wf: check --> edit
        Line.wfedit(books[0].lines)
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(len(books[0].lines[0].references), 0)
        self.assertEqual(len(books[1].lines), 0)

    @with_transaction()
    def test_splitline_category_and_transfer_2ndcurrency(self):
        """ add book, line, two split-lines,
            category + transfer, target-cashbook in USD
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        types = self.prep_type()
        category1 = self.prep_category(cattype='out')
        company = self.prep_company()
        party = self.prep_party()
        (usd, euro) = self.prep_2nd_currency(company)

        books = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': euro.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': 'Text 1',
                    'category': category1.id,
                    'bookingtype': 'out',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            }, {
            'name': 'Book 2',
            'btype': types.id,
            'company': company.id,
            'currency': usd.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            }])
        self.assertEqual(books[0].rec_name, 'Book 1 | -1.00 € | Open')
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/01/2022|Exp|-1.00 €|Text 1 [Cat1]')
        self.assertEqual(books[1].rec_name, 'Book 2 | 0.00 usd | Open')

        # EUR --> USD
        Book.write(*[
            [books[0]],
            {
                'lines': [('write', [books[0].lines[0]], {
                    'bookingtype': 'spout',
                    'splitlines': [('create', [{
                        'amount': Decimal('5.0'),
                        'splittype': 'cat',
                        'description': 'to category',
                        'category': category1.id,
                        }, {
                        'amount': Decimal('6.0'),
                        'splittype': 'tr',
                        'description': 'to book2',
                        'booktransf': books[1].id,
                        }])],
                    })]
            }])
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(
            books[0].lines[0].rec_name,
            '05/01/2022|Exp/Sp|-11.00 €|Text 1 [-]')
        self.assertEqual(books[0].lines[0].category, None)
        self.assertEqual(len(books[0].lines[0].splitlines), 2)
        self.assertEqual(
            books[0].lines[0].splitlines[0].rec_name,
            'Exp/Sp|5.00 €|to category [Cat1]')
        self.assertEqual(
            books[0].lines[0].splitlines[0].amount_2nd_currency, None)
        self.assertEqual(
            books[0].lines[0].splitlines[1].rec_name,
            'Exp/Sp|6.00 €|to book2 [Book 2 | 0.00 usd | Open]')
        self.assertEqual(
            books[0].lines[0].splitlines[1].amount_2nd_currency,
            Decimal('6.3'))
        self.assertEqual(len(books[1].lines), 0)

        # wf: edit -> check
        Line.wfcheck(books[0].lines)
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(books[0].lines[0].state, 'check')
        self.assertEqual(books[0].lines[0].number, '1')
        self.assertEqual(len(books[0].lines[0].references), 1)
        self.assertEqual(
            books[0].lines[0].references[0].rec_name,
            '05/01/2022|from|6.30 usd|to book2 [Book 1 | -11.00 € | Open]')

        self.assertEqual(len(books[1].lines), 1)
        self.assertEqual(
            books[1].lines[0].reference.rec_name,
            '05/01/2022|Exp/Sp|-11.00 €|Text 1 [-]')
        self.assertEqual(
            books[1].lines[0].rec_name,
            '05/01/2022|from|6.30 usd|to book2 [Book 1 | -11.00 € | Open]')
        self.assertEqual(
            books[1].lines[0].amount, Decimal('6.3'))
        self.assertEqual(
            books[1].lines[0].amount_2nd_currency, Decimal('6.0'))

        # wf: check --> edit
        Line.wfedit(books[0].lines)
        self.assertEqual(len(books[0].lines), 1)
        self.assertEqual(len(books[0].lines[0].references), 0)
        self.assertEqual(len(books[1].lines), 0)

    @with_transaction()
    def test_splitline_check_clear_by_bookingtype(self):
        """ add book, line, category, set line to 'in',
            then update to 'spin'
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')

        types = self.prep_type()
        category1 = self.prep_category(cattype='in')
        category2 = self.prep_category(name='Cat2', cattype='in')
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
                    'category': category1.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            }])

        self.assertEqual(len(book.lines), 1)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(book.lines[0].amount, Decimal('1.0'))
        self.assertEqual(book.lines[0].category.rec_name, 'Cat1')

        Lines.write(*[
            [book.lines[0]],
            {
                'bookingtype': 'spin',
                'splitlines': [('create', [{
                    'amount': Decimal('5.0'),
                    'category': category1.id,
                    'description': 'line 1'
                    }, {
                    'amount': Decimal('2.0'),
                    'category': category2.id,
                    'description': 'line 2',
                    }])],
            }])

        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|Rev/Sp|7.00 usd|Text 1 [-]')
        self.assertEqual(book.lines[0].amount, Decimal('7.0'))
        self.assertEqual(book.lines[0].category, None)

        self.assertEqual(len(book.lines[0].splitlines), 2)
        self.assertEqual(book.lines[0].splitlines[0].amount, Decimal('5.0'))
        self.assertEqual(book.lines[0].splitlines[0].category.rec_name, 'Cat1')
        self.assertEqual(book.lines[0].splitlines[0].description, 'line 1')
        self.assertEqual(
            book.lines[0].splitlines[0].rec_name,
            'Rev/Sp|5.00 usd|line 1 [Cat1]')

        self.assertEqual(book.lines[0].splitlines[1].amount, Decimal('2.0'))
        self.assertEqual(book.lines[0].splitlines[1].category.rec_name, 'Cat2')
        self.assertEqual(book.lines[0].splitlines[1].description, 'line 2')
        self.assertEqual(
            book.lines[0].splitlines[1].rec_name,
            'Rev/Sp|2.00 usd|line 2 [Cat2]')

        Lines.write(*[
            [book.lines[0]],
            {
                'splitlines': [
                    ('write',
                        [book.lines[0].splitlines[0]],
                        {
                            'amount': Decimal('3.5'),
                        })],
            }])
        self.assertEqual(book.lines[0].splitlines[0].amount, Decimal('3.5'))
        self.assertEqual(book.lines[0].splitlines[1].amount, Decimal('2.0'))
        self.assertEqual(book.lines[0].amount, Decimal('5.5'))

        Lines.write(*[
            [book.lines[0]],
            {
                'bookingtype': 'in',
                'amount': Decimal('7.5'),
                'category': category2.id,
            }])
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|Rev|7.50 usd|Text 1 [Cat2]')
        self.assertEqual(book.lines[0].category.rec_name, 'Cat2')
        self.assertEqual(len(book.lines[0].splitlines), 0)

# end SplitLineTestCase
