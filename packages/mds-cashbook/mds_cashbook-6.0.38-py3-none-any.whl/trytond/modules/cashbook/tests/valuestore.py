# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from datetime import date, timedelta
from decimal import Decimal
from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.exceptions import UserError
from trytond.transaction import Transaction


class ValuestoreTestCase(object):
    """ test storage of values
    """
    @with_transaction()
    def test_valstore_update_currency_rate(self):
        """ create cashbook, check update of cashbook on
            update of rates of currency
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        ValueStore = pool.get('cashbook.values')
        Currency = pool.get('currency.currency')
        Queue = pool.get('ir.queue')

        types = self.prep_type()
        company = self.prep_company()
        (usd, euro) = self.prep_2nd_currency(company)
        self.assertEqual(company.currency.rec_name, 'Euro')

        with Transaction().set_context({
                'company': company.id,
                'date': date(2022, 5, 20)}):

            self.assertEqual(Queue.search_count([]), 0)

            category = self.prep_category(cattype='in')
            party = self.prep_party()
            book, = Book.create([{
                'name': 'Book 1',
                'btype': types.id,
                'company': company.id,
                'currency': usd.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1),
                'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': '10 US$',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('10.0'),
                    'party': party.id,
                    }, {
                    'date': date(2022, 5, 10),
                    'description': '5 US$',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('5.0'),
                    'party': party.id,
                    }])],
                }])

            # run worker
            self.assertEqual(
                ValueStore.search_count([]),
                len(Book.valuestore_fields()))
            self.prep_valstore_run_worker()

            book, = Book.search([])
            self.assertEqual(book.rec_name, 'Book 1 | 15.00 usd | Open')
            self.assertEqual(book.balance, Decimal('15.0'))
            self.assertEqual(book.balance_all, Decimal('15.0'))
            self.assertEqual(book.balance_ref, Decimal('14.29'))
            self.assertEqual(
                len(book.value_store),
                len(Book.valuestore_fields()))
            self.assertEqual(
                book.value_store[0].rec_name,
                '[Book 1 | 15.00 usd | Open]|balance|15.00|2')
            self.assertEqual(
                book.value_store[1].rec_name,
                '[Book 1 | 15.00 usd | Open]|balance_all|15.00|2')
            self.assertEqual(
                book.value_store[2].rec_name,
                '[Book 1 | 15.00 usd | Open]|balance_ref|14.29|2')

            # add rate to usd
            self.assertEqual(Queue.search_count([]), 0)
            Currency.write(*[
                [usd],
                {
                    'rates': [('create', [{
                        'date': date(2022, 5, 6),
                        'rate': Decimal('1.08'),
                        }])],
                }])
            self.assertEqual(Queue.search_count([]), 1)
            self.prep_valstore_run_worker()
            self.assertEqual(Queue.search_count([]), 0)

            # check reference-currency
            book, = Book.search([])
            self.assertEqual(book.rec_name, 'Book 1 | 15.00 usd | Open')
            self.assertEqual(book.balance, Decimal('15.0'))
            self.assertEqual(book.balance_all, Decimal('15.0'))
            self.assertEqual(book.balance_ref, Decimal('13.89'))
            self.assertEqual(
                len(book.value_store),
                len(Book.valuestore_fields()))
            self.assertEqual(
                book.value_store[0].rec_name,
                '[Book 1 | 15.00 usd | Open]|balance|15.00|2')
            self.assertEqual(
                book.value_store[1].rec_name,
                '[Book 1 | 15.00 usd | Open]|balance_all|15.00|2')
            self.assertEqual(
                book.value_store[2].rec_name,
                '[Book 1 | 15.00 usd | Open]|balance_ref|13.89|2')

            # find rate
            self.assertEqual(len(usd.rates), 2)
            self.assertEqual(usd.rates[0].date, date(2022, 5, 6))
            self.assertEqual(usd.rates[0].rate, Decimal('1.08'))

            # update rate
            self.assertEqual(Queue.search_count([]), 0)
            Currency.write(*[
                [usd],
                {
                    'rates': [(
                        'write',
                        [usd.rates[0]],
                        {'rate': Decimal('1.12')})],
                }])
            self.assertEqual(Queue.search_count([]), 1)
            self.prep_valstore_run_worker()
            self.assertEqual(Queue.search_count([]), 0)

            book, = Book.search([])
            self.assertEqual(book.rec_name, 'Book 1 | 15.00 usd | Open')
            self.assertEqual(book.balance_ref, Decimal('13.39'))
            self.assertEqual(
                book.value_store[2].rec_name,
                '[Book 1 | 15.00 usd | Open]|balance_ref|13.39|2')

            # delete rate
            self.assertEqual(Queue.search_count([]), 0)
            Currency.write(*[
                [usd],
                {
                    'rates': [('delete', [usd.rates[0]])],
                }])
            self.assertEqual(Queue.search_count([]), 1)
            self.prep_valstore_run_worker()
            self.assertEqual(Queue.search_count([]), 0)

            book, = Book.search([])
            self.assertEqual(book.rec_name, 'Book 1 | 15.00 usd | Open')
            self.assertEqual(book.balance_ref, Decimal('14.29'))
            self.assertEqual(
                book.value_store[2].rec_name,
                '[Book 1 | 15.00 usd | Open]|balance_ref|14.29|2')

    def prep_valstore_run_worker(self):
        """ run tasks from queue
        """
        Queue = Pool().get('ir.queue')

        tasks = Queue.search([])
        for task in tasks:
            task.run()
        Queue.delete(tasks)

    @with_transaction()
    def test_valstore_update_store_values(self):
        """ create cashbook, store value
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        ValueStore = pool.get('cashbook.values')
        Queue = pool.get('ir.queue')

        types = self.prep_type()
        company = self.prep_company()
        (usd, euro) = self.prep_2nd_currency(company)
        self.assertEqual(company.currency.rec_name, 'Euro')

        with Transaction().set_context({'company': company.id}):

            self.assertEqual(Queue.search_count([]), 0)

            category = self.prep_category(cattype='in')
            party = self.prep_party()
            book, = Book.create([{
                'name': 'Book 1',
                'btype': types.id,
                'company': company.id,
                'currency': usd.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1),
                'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': '10 US$',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('10.0'),
                    'party': party.id,
                    }, {
                    'date': date(2022, 5, 10),
                    'description': '5 US$',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('5.0'),
                    'party': party.id,
                    }])],
                }])

            # run worker
            self.assertEqual(
                ValueStore.search_count([]),
                len(Book.valuestore_fields()))
            self.prep_valstore_run_worker()

            # check values until 2022-05-05
            with Transaction().set_context({
                    'date': date(2022, 5, 5)}):

                book, = Book.search([])
                self.assertEqual(book.rec_name, 'Book 1 | 10.00 usd | Open')
                self.assertEqual(book.balance, Decimal('10.0'))
                self.assertEqual(book.balance_all, Decimal('15.0'))
                self.assertEqual(book.balance_ref, Decimal('14.29'))
                self.assertEqual(
                    len(book.value_store),
                    len(Book.valuestore_fields()))
                self.assertEqual(
                    book.value_store[0].rec_name,
                    '[Book 1 | 10.00 usd | Open]|balance|15.00|2')
                self.assertEqual(
                    book.value_store[1].rec_name,
                    '[Book 1 | 10.00 usd | Open]|balance_all|15.00|2')
                self.assertEqual(
                    book.value_store[2].rec_name,
                    '[Book 1 | 10.00 usd | Open]|balance_ref|14.29|2')

                # values created by book-create, without context
                self.assertEqual(
                    ValueStore.search_count([]),
                    len(Book.valuestore_fields()))

                values = ValueStore.search([], order=[('field_name', 'ASC')])
                self.assertEqual(
                    len(values),
                    len(Book.valuestore_fields()))
                self.assertEqual(
                    values[0].rec_name,
                    '[Book 1 | 10.00 usd | Open]|balance|15.00|2')
                self.assertEqual(
                    values[1].rec_name,
                    '[Book 1 | 10.00 usd | Open]|balance_all|15.00|2')
                self.assertEqual(
                    values[2].rec_name,
                    '[Book 1 | 10.00 usd | Open]|balance_ref|14.29|2')

                # check write of too much digits
                self.assertRaisesRegex(
                    UserError,
                    r"The number of digits in the value " +
                    r'"Decimal\(' +
                    r"'12\.345'\)" +
                    r'" for field "Value" in "Value Store" exceeds ' +
                    r'the limit of "2".',
                    ValueStore.write,
                    *[
                        [values[0]],
                        {
                            'numvalue': Decimal('12.345'),
                        }
                    ])

                # update with context
                Book.valuestore_update_records([book])

                values = ValueStore.search([], order=[('field_name', 'ASC')])
                self.assertEqual(
                    len(values),
                    len(Book.valuestore_fields()))

                self.assertEqual(
                    values[0].rec_name,
                    '[Book 1 | 10.00 usd | Open]|balance|10.00|2')
                self.assertEqual(
                    values[1].rec_name,
                    '[Book 1 | 10.00 usd | Open]|balance_all|15.00|2')
                self.assertEqual(
                    values[2].rec_name,
                    '[Book 1 | 10.00 usd | Open]|balance_ref|14.29|2')

            # check values until 2022-05-15
            with Transaction().set_context({
                    'date': date(2022, 5, 15)}):

                book, = Book.search([])
                self.assertEqual(book.rec_name, 'Book 1 | 15.00 usd | Open')
                self.assertEqual(book.balance, Decimal('15.0'))
                self.assertEqual(book.balance_all, Decimal('15.0'))
                self.assertEqual(book.balance_ref, Decimal('14.29'))

                # update values
                self.assertEqual(
                    ValueStore.search_count([]),
                    len(Book.valuestore_fields()))
                Book.valuestore_update_records([book])

                values = ValueStore.search(
                    [('field_name', 'in', [
                        'balance', 'balance_all', 'balance_ref'])],
                    order=[('field_name', 'ASC')])
                self.assertEqual(len(values), 3)

                self.assertEqual(
                    values[0].rec_name,
                    '[Book 1 | 15.00 usd | Open]|balance|15.00|2')
                self.assertEqual(
                    values[1].rec_name,
                    '[Book 1 | 15.00 usd | Open]|balance_all|15.00|2')
                self.assertEqual(
                    values[2].rec_name,
                    '[Book 1 | 15.00 usd | Open]|balance_ref|14.29|2')

            # delete book, should delete values
            Book.write(*[
                [book],
                {'lines': [('delete', [x.id for x in book.lines])]}
                ])
            self.assertEqual(
                ValueStore.search_count([]),
                len(Book.valuestore_fields()))
            Book.delete([book])
            self.assertEqual(ValueStore.search_count([]), 0)

    @with_transaction()
    def test_valstore_update_store_values_line(self):
        """ create cashbooks hierarchical, add lines
            check update of parent cashbooks
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')
        ValueStore = pool.get('cashbook.values')

        types = self.prep_type()
        company = self.prep_company()
        (usd, euro) = self.prep_2nd_currency(company)
        self.assertEqual(company.currency.rec_name, 'Euro')

        with Transaction().set_context({'company': company.id}):
            category = self.prep_category(cattype='in')
            party = self.prep_party()
            book, = Book.create([{
                'name': 'Lev 0',
                'btype': types.id,
                'company': company.id,
                'currency': usd.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1),
                'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': '10 US$',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('10.0'),
                    'party': party.id,
                    }])],
                'childs': [('create', [{
                    'name': 'Lev 1a',
                    'btype': types.id,
                    'company': company.id,
                    'currency': euro.id,
                    'number_sequ': self.prep_sequence().id,
                    'start_date': date(2022, 5, 1),
                    }, {
                    'name': 'Lev 1b',
                    'btype': types.id,
                    'company': company.id,
                    'currency': euro.id,
                    'number_sequ': self.prep_sequence().id,
                    'start_date': date(2022, 5, 1),
                    }])],
                }])
            self.assertEqual(book.rec_name, 'Lev 0 | 10.00 usd | Open')
            self.assertEqual(len(book.lines), 1)
            self.assertEqual(
                book.lines[0].rec_name,
                '05/01/2022|Rev|10.00 usd|10 US$ [Cat1]')
            self.assertEqual(len(book.childs), 2)
            self.assertEqual(
                book.childs[0].rec_name, 'Lev 0/Lev 1a | 0.00 € | Open')
            self.assertEqual(len(book.childs[0].lines), 0)
            self.assertEqual(
                book.childs[1].rec_name, 'Lev 0/Lev 1b | 0.00 € | Open')
            self.assertEqual(len(book.childs[1].lines), 0)

            self.assertEqual(
                ValueStore.search_count([]),
                3 * len(Book.valuestore_fields()))
            self.prep_valstore_run_worker()

            values = ValueStore.search(
                [('field_name', 'in', [
                    'balance', 'balance_all', 'balance_ref'])],
                order=[('cashbook', 'ASC'), ('field_name', 'ASC')])
            self.assertEqual(len(values), 3 * 3)

            self.assertEqual(
                values[0].rec_name,
                '[Lev 0 | 10.00 usd | Open]|balance|10.00|2')
            self.assertEqual(
                values[1].rec_name,
                '[Lev 0 | 10.00 usd | Open]|balance_all|10.00|2')
            self.assertEqual(
                values[2].rec_name,
                '[Lev 0 | 10.00 usd | Open]|balance_ref|9.52|2')

            self.assertEqual(
                values[3].rec_name,
                '[Lev 0/Lev 1a | 0.00 € | Open]|balance|0.00|2')
            self.assertEqual(
                values[4].rec_name,
                '[Lev 0/Lev 1a | 0.00 € | Open]|balance_all|0.00|2')
            self.assertEqual(
                values[5].rec_name,
                '[Lev 0/Lev 1a | 0.00 € | Open]|balance_ref|0.00|2')

            self.assertEqual(
                values[6].rec_name,
                '[Lev 0/Lev 1b | 0.00 € | Open]|balance|0.00|2')
            self.assertEqual(
                values[7].rec_name,
                '[Lev 0/Lev 1b | 0.00 € | Open]|balance_all|0.00|2')
            self.assertEqual(
                values[8].rec_name,
                '[Lev 0/Lev 1b | 0.00 € | Open]|balance_ref|0.00|2')

            # add bookings
            Line.create(self.prep_valstore_line_create_data(
                [{
                'cashbook': values[0].cashbook.id,  # Lev 0
                'amount': Decimal('2.0'),
                'bookingtype': 'in',
                'category': category.id,
                'date': date(2022, 5, 10),
                }, {
                'cashbook': values[3].cashbook.id,  # Lev 1a
                'amount': Decimal('3.0'),
                'bookingtype': 'in',
                'category': category.id,
                'date': date(2022, 5, 10),
                }]))

            # add 'date' to context, will return computed
            # (not stored) values
            with Transaction().set_context({'date': date(2022, 5, 10)}):
                values = ValueStore.search(
                    [('field_name', 'in', [
                        'balance', 'balance_all', 'balance_ref'])],
                    order=[('cashbook', 'ASC'), ('field_name', 'ASC')])
                self.assertEqual(len(values), 9)
                self.assertEqual(
                    values[0].rec_name,
                    '[Lev 0 | 15.15 usd | Open]|balance|10.00|2')
                self.assertEqual(
                    values[1].rec_name,
                    '[Lev 0 | 15.15 usd | Open]|balance_all|10.00|2')
                self.assertEqual(
                    values[2].rec_name,
                    '[Lev 0 | 15.15 usd | Open]|balance_ref|9.52|2')

                self.assertEqual(
                    values[3].rec_name,
                    '[Lev 0/Lev 1a | 3.00 € | Open]|balance|0.00|2')
                self.assertEqual(
                    values[4].rec_name,
                    '[Lev 0/Lev 1a | 3.00 € | Open]|balance_all|0.00|2')
                self.assertEqual(
                    values[5].rec_name,
                    '[Lev 0/Lev 1a | 3.00 € | Open]|balance_ref|0.00|2')

                self.assertEqual(
                    values[6].rec_name,
                    '[Lev 0/Lev 1b | 0.00 € | Open]|balance|0.00|2')
                self.assertEqual(
                    values[7].rec_name,
                    '[Lev 0/Lev 1b | 0.00 € | Open]|balance_all|0.00|2')
                self.assertEqual(
                    values[8].rec_name,
                    '[Lev 0/Lev 1b | 0.00 € | Open]|balance_ref|0.00|2')

            # before run of workers - w/o 'date' in context
            values = ValueStore.search(
                [('field_name', 'in', [
                    'balance', 'balance_all', 'balance_ref'])],
                order=[('cashbook', 'ASC'), ('field_name', 'ASC')])
            self.assertEqual(len(values), 9)
            self.assertEqual(
                values[0].rec_name,
                '[Lev 0 | 10.00 usd | Open]|balance|10.00|2')
            self.assertEqual(
                values[1].rec_name,
                '[Lev 0 | 10.00 usd | Open]|balance_all|10.00|2')
            self.assertEqual(
                values[2].rec_name,
                '[Lev 0 | 10.00 usd | Open]|balance_ref|9.52|2')

            self.assertEqual(
                values[3].rec_name,
                '[Lev 0/Lev 1a | 0.00 € | Open]|balance|0.00|2')
            self.assertEqual(
                values[4].rec_name,
                '[Lev 0/Lev 1a | 0.00 € | Open]|balance_all|0.00|2')
            self.assertEqual(
                values[5].rec_name,
                '[Lev 0/Lev 1a | 0.00 € | Open]|balance_ref|0.00|2')

            self.assertEqual(
                values[6].rec_name,
                '[Lev 0/Lev 1b | 0.00 € | Open]|balance|0.00|2')
            self.assertEqual(
                values[7].rec_name,
                '[Lev 0/Lev 1b | 0.00 € | Open]|balance_all|0.00|2')
            self.assertEqual(
                values[8].rec_name,
                '[Lev 0/Lev 1b | 0.00 € | Open]|balance_ref|0.00|2')

            self.prep_valstore_run_worker()

            # after run of workers
            values = ValueStore.search(
                [('field_name', 'in', [
                    'balance', 'balance_all', 'balance_ref'])],
                order=[('cashbook', 'ASC'), ('field_name', 'ASC')])
            self.assertEqual(len(values), 9)

            self.assertEqual(
                values[0].rec_name,
                '[Lev 0 | 15.15 usd | Open]|balance|15.15|2')
            self.assertEqual(
                values[1].rec_name,
                '[Lev 0 | 15.15 usd | Open]|balance_all|15.15|2')
            self.assertEqual(
                values[2].rec_name,
                '[Lev 0 | 15.15 usd | Open]|balance_ref|14.43|2')

            self.assertEqual(
                values[3].rec_name,
                '[Lev 0/Lev 1a | 3.00 € | Open]|balance|3.00|2')
            self.assertEqual(
                values[4].rec_name,
                '[Lev 0/Lev 1a | 3.00 € | Open]|balance_all|3.00|2')
            self.assertEqual(
                values[5].rec_name,
                '[Lev 0/Lev 1a | 3.00 € | Open]|balance_ref|3.00|2')

            self.assertEqual(
                values[6].rec_name,
                '[Lev 0/Lev 1b | 0.00 € | Open]|balance|0.00|2')
            self.assertEqual(
                values[7].rec_name,
                '[Lev 0/Lev 1b | 0.00 € | Open]|balance_all|0.00|2')
            self.assertEqual(
                values[8].rec_name,
                '[Lev 0/Lev 1b | 0.00 € | Open]|balance_ref|0.00|2')

    def prep_valstore_line_create_data(self, query):
        """ allow add of data
        """
        return query

    @with_transaction()
    def test_valstore_search_sort_books(self):
        """ create cashbooks add lines, search/sort
            with and w/o 'date' in context
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')

        types = self.prep_type()
        company = self.prep_company()
        (usd, euro) = self.prep_2nd_currency(company)
        self.assertEqual(company.currency.rec_name, 'Euro')

        with Transaction().set_context({'company': company.id}):
            category = self.prep_category(cattype='in')
            party = self.prep_party()
            books = Book.create([{
                'name': 'Cashbook 1',
                'btype': types.id,
                'company': company.id,
                'currency': usd.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1),
                'lines': [('create', [{
                    'date': date(2022, 5, 1),
                    'description': '10 US$',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('10.0'),
                    'party': party.id,
                    }])]}, {
                'name': 'Cashbook 2',
                'btype': types.id,
                'company': company.id,
                'currency': euro.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1),
                }, {
                'name': 'Cashbook 3',
                'btype': types.id,
                'company': company.id,
                'currency': euro.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1),
                }])
            self.assertEqual(len(books), 3)
            self.assertEqual(books[0].rec_name, 'Cashbook 1 | 10.00 usd | Open')
            self.assertEqual(books[1].rec_name, 'Cashbook 2 | 0.00 € | Open')
            self.assertEqual(books[2].rec_name, 'Cashbook 3 | 0.00 € | Open')

            Line.create(self.prep_valstore_line_create_data(
                [{
                'cashbook': books[1].id,
                'bookingtype': 'in',
                'amount': Decimal('5.0'),
                'date': date(2022, 5, 6),
                'description': '5€ in',
                'category': category.id,
                }, {
                'cashbook': books[2].id,
                'bookingtype': 'in',
                'amount': Decimal('6.0'),
                'date': date(2022, 5, 7),
                'description': '6€ in',
                'category': category.id,
                }]))

            # no 'date' in context, using stored values
            # workers not yet processed
            books = Book.search([], order=[('name', 'ASC')])
            self.assertEqual(len(books), 3)
            self.assertEqual(books[0].rec_name, 'Cashbook 1 | 10.00 usd | Open')
            self.assertEqual(books[1].rec_name, 'Cashbook 2 | 0.00 € | Open')
            self.assertEqual(books[2].rec_name, 'Cashbook 3 | 0.00 € | Open')

            self.assertEqual(
                Book.search_count([('balance', '=', Decimal('0.0'))]),
                2)
            self.assertEqual(
                Book.search_count([('balance_all', '=', Decimal('0.0'))]),
                2)
            self.assertEqual(
                Book.search_count([('balance_ref', '=', Decimal('0.0'))]),
                2)

            # check sorting - using stored values
            books = Book.search([], order=[
                ('balance_all', 'DESC'), ('name', 'ASC')])
            self.assertEqual(len(books), 3)
            self.assertEqual(books[0].rec_name, 'Cashbook 1 | 10.00 usd | Open')
            self.assertEqual(books[1].rec_name, 'Cashbook 2 | 0.00 € | Open')
            self.assertEqual(books[2].rec_name, 'Cashbook 3 | 0.00 € | Open')

            # search again with 'date' - using computed values
            with Transaction().set_context({'date': date(2022, 5, 6)}):
                self.assertEqual(
                    Book.search_count([('balance', '=', Decimal('5.0'))]),
                    1)
                self.assertEqual(
                    Book.search_count([
                        ('balance', '>=', Decimal('5.0')),
                        ('balance', '<', Decimal('9.0')),
                        ]),
                    1)
                self.assertEqual(
                    Book.search_count([
                        ('balance_all', '>=', Decimal('5.0'))]),
                    3)
                self.assertRaisesRegex(
                    UserError,
                    "Search with 'date' no allowed for field " +
                    "'balance_ref' on model 'cashbook.book'.",
                    Book.search_count,
                    [('balance_ref', '=', Decimal('0.0'))])

                self.assertRaisesRegex(
                    UserError,
                    "Search with 'date' no allowed for field " +
                    "'balance_ref' on model 'cashbook.book'.",
                    Book.search,
                    [], order=[('balance_ref', 'ASC')])

                # check sorting - using computed values
                books = Book.search([], order=[
                    ('balance_all', 'DESC'),
                    ('name', 'ASC'),
                    ('balance', 'ASC')])
                self.assertEqual(len(books), 3)
                self.assertEqual(
                    books[0].rec_name, 'Cashbook 1 | 10.00 usd | Open')
                self.assertEqual(
                    books[1].rec_name, 'Cashbook 3 | 0.00 € | Open')
                self.assertEqual(books[1].balance_all, Decimal('6.0'))
                self.assertEqual(
                    books[2].rec_name, 'Cashbook 2 | 5.00 € | Open')

            with Transaction().set_context({'date': date(2022, 5, 7)}):
                self.assertEqual(
                    Book.search_count([('balance', '=', Decimal('5.0'))]),
                    1)
                self.assertEqual(
                    Book.search_count([
                        ('balance', '>=', Decimal('5.0')),
                        ('balance', '<', Decimal('9.0')),
                        ]),
                    2)

            # run workers
            self.prep_valstore_run_worker()

            # check stored values - no 'date' in context
            books = Book.search([], order=[('name', 'ASC')])
            self.assertEqual(len(books), 3)
            self.assertEqual(books[0].rec_name, 'Cashbook 1 | 10.00 usd | Open')
            self.assertEqual(books[1].rec_name, 'Cashbook 2 | 5.00 € | Open')
            self.assertEqual(books[2].rec_name, 'Cashbook 3 | 6.00 € | Open')

            # check sorting - using stored values
            # run most sorters
            books = Book.search([], order=[
                ('balance_all', 'DESC'),
                ('name', 'ASC'),
                ('balance', 'ASC'),
                ('balance_ref', 'ASC')])
            self.assertEqual(len(books), 3)
            self.assertEqual(books[0].rec_name, 'Cashbook 1 | 10.00 usd | Open')
            self.assertEqual(books[1].rec_name, 'Cashbook 3 | 6.00 € | Open')
            self.assertEqual(books[2].rec_name, 'Cashbook 2 | 5.00 € | Open')

            self.assertEqual(
                Book.search_count([('balance', '=', Decimal('0.0'))]),
                0)
            self.assertEqual(
                Book.search_count([('balance', '=', Decimal('5.0'))]),
                1)
            self.assertEqual(
                Book.search_count([('balance', '=', Decimal('6.0'))]),
                1)
            self.assertEqual(
                Book.search_count([
                    ('balance', '>=', Decimal('5.0')),
                    ('balance', '<', Decimal('9.0')),
                    ]),
                2)
            self.assertEqual(
                Book.search_count([('balance_ref', '=', Decimal('6.0'))]),
                1)

    @with_transaction()
    def test_valstore_maintain_values(self):
        """ create cashbook, check maintenance -
            update records by cron, delete lost records
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        ValueStore = pool.get('cashbook.values')
        tab_book = Book.__table__()
        cursor = Transaction().connection.cursor()

        types = self.prep_type()
        company = self.prep_company()
        (usd, euro) = self.prep_2nd_currency(company)
        self.assertEqual(company.currency.rec_name, 'Euro')

        category = self.prep_category(cattype='in')
        party = self.prep_party()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': usd.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                'date': date(2022, 5, 1),
                'description': '10 US$',
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('10.0'),
                'party': party.id,
                }, {
                'date': date(2022, 5, 10),
                'description': '5 US$',
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('5.0'),
                'party': party.id,
                }])],
            }])

        # clean 'numvalue'
        # maintenance_values() will restore it
        val1, = ValueStore.search([('field_name', '=', 'balance')])
        ValueStore.write(*[[val1], {'numvalue': None}])

        self.assertTrue(val1.write_date is not None)
        self.assertTrue(val1.create_date is not None)
        self.assertEqual(val1.numvalue, None)

        # update outdated records
        with Transaction().set_context({
                'maintenance_date': val1.write_date.date() +
                timedelta(days=2)}):
            ValueStore.maintenance_values()

            val1, = ValueStore.search([('field_name', '=', 'balance')])
            self.assertEqual(val1.numvalue, Decimal('15.0'))

        # delete book
        self.assertEqual(Book.search_count([]), 1)
        self.assertEqual(
            ValueStore.search_count([]),
            len(Book.valuestore_fields()))
        query = tab_book.delete(where=tab_book.id == book.id)
        cursor.execute(*query)
        self.assertEqual(Book.search_count([]), 0)
        self.assertEqual(ValueStore.search_count([]), 0)

# end ValuestoreTestCase
