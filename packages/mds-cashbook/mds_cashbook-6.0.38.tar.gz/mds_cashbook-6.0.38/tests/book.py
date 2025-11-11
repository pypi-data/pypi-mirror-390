# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from datetime import date
from decimal import Decimal


class BookTestCase(object):
    """ test cashbook
    """
    def prep_sequence(self, name='Book Sequ'):
        """ create numbering-equence
        """
        pool = Pool()
        IrSequence = pool.get('ir.sequence')
        IrSequType = pool.get('ir.sequence.type')

        sequ_type, = IrSequType.search([('name', '=', 'Cashbook Line')])

        sequ = IrSequence.search([('name', '=', name)])
        if len(sequ) > 0:
            return sequ[0]

        sequ, = IrSequence.create([{
            'name': name,
            'sequence_type': sequ_type.id,
            }])
        return sequ

    @with_transaction()
    def test_book_create(self):
        """ create cashbook
        """
        pool = Pool()
        Book = pool.get('cashbook.book')

        types = self.prep_type()
        company = self.prep_company()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.rec_name, 'Book 1 | 0.00 usd | Open')
        self.assertEqual(book.btype.rec_name, 'CAS - Cash')
        self.assertEqual(book.state, 'open')
        self.assertEqual(book.state_string, 'Open')

    @with_transaction()
    def test_book_create_2nd_currency(self):
        """ create cashbook, in 2nd currency, check balance-fields
        """
        pool = Pool()
        Book = pool.get('cashbook.book')

        types = self.prep_type()
        company = self.prep_company()

        # add EURO, set company-currency to EURO
        (usd, euro) = self.prep_2nd_currency(company)
        category = self.prep_category(cattype='in')
        self.assertEqual(company.currency.rec_name, 'Euro')
        party = self.prep_party()

        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': usd.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                    'date': date(2022, 5, 5),
                    'description': 'Amount in USD',
                    'bookingtype': 'in',
                    'category': category.id,
                    'amount': Decimal('10.0'),
                    'party': party.id,
                }])],
            }])

        with Transaction().set_context({
                'date': date(2022, 5, 5)}):
            self.assertEqual(book.rec_name, 'Book 1 | 10.00 usd | Open')
            self.assertEqual(book.currency.rec_name, 'usd')
            self.assertEqual(book.currency.rate, Decimal('1.05'))
            self.assertEqual(book.company_currency.rec_name, 'Euro')
            self.assertEqual(book.company_currency.rate, Decimal('1.0'))

            self.assertEqual(book.balance, Decimal('10.0'))
            self.assertEqual(book.balance_ref, Decimal('9.52'))

            self.assertEqual(len(book.lines), 1)
            self.assertEqual(
                book.lines[0].rec_name,
                '05/05/2022|Rev|10.00 usd|Amount in USD [Cat1]')

    @with_transaction()
    def test_book_create_2nd_currency_hierarchical(self):
        """ create cashbook-hierarchy, in 2nd currency,
            check balance-fields
        """
        pool = Pool()
        Book = pool.get('cashbook.book')

        types = self.prep_type()
        company = self.prep_company()

        # add EURO, set company-currency to EURO
        (usd, euro) = self.prep_2nd_currency(company)
        category = self.prep_category(cattype='in')
        self.assertEqual(company.currency.rec_name, 'Euro')
        party = self.prep_party()

        book, = Book.create([{
            'name': 'Book 1',
            'company': company.id,
            'currency': euro.id,
            'childs': [('create', [{
                'name': 'Book 2',
                'btype': types.id,
                'company': company.id,
                'currency': usd.id,
                'number_sequ': self.prep_sequence().id,
                'start_date': date(2022, 5, 1),
                'lines': [('create', [{
                        'date': date(2022, 5, 5),
                        'description': 'Amount in USD',
                        'bookingtype': 'in',
                        'category': category.id,
                        'amount': Decimal('10.0'),
                        'party': party.id,
                    }])],
                }])],
            }])

        with Transaction().set_context({
                'date': date(2022, 5, 5)}):
            self.assertEqual(book.rec_name, 'Book 1')
            self.assertEqual(book.currency.rec_name, 'Euro')
            self.assertEqual(book.currency.rate, Decimal('1.0'))
            self.assertEqual(book.company_currency, None)
            self.assertEqual(book.balance, Decimal('9.52'))
            self.assertEqual(book.balance_ref, Decimal('9.52'))
            self.assertEqual(len(book.lines), 0)
            self.assertEqual(len(book.childs), 1)

            self.assertEqual(
                book.childs[0].rec_name,
                'Book 1/Book 2 | 10.00 usd | Open')
            self.assertEqual(book.childs[0].currency.rec_name, 'usd')
            self.assertEqual(book.childs[0].currency.rate, Decimal('1.05'))
            self.assertEqual(book.childs[0].company_currency.rec_name, 'Euro')
            self.assertEqual(book.childs[0].balance, Decimal('10.0'))
            self.assertEqual(book.childs[0].balance_ref, Decimal('9.52'))
            self.assertEqual(len(book.childs[0].lines), 1)

    @with_transaction()
    def test_book_create_hierarchy(self):
        """ create cashbook, hierarchical
        """
        pool = Pool()
        Book = pool.get('cashbook.book')

        types = self.prep_type()
        company = self.prep_company()
        book, = Book.create([{
            'name': 'Level 1',
            'btype': None,
            'company': company.id,
            'childs': [('create', [{
                    'name': 'Level 2',
                    'btype': types.id,
                    'company': company.id,
                    'currency': company.currency.id,
                    'number_sequ': self.prep_sequence().id,
                }])],
            }])
        self.assertEqual(book.name, 'Level 1')
        self.assertEqual(book.rec_name, 'Level 1')
        self.assertEqual(len(book.childs), 1)
        self.assertEqual(
            book.childs[0].rec_name,
            'Level 1/Level 2 | 0.00 usd | Open')

    @with_transaction()
    def test_book_deny_delete_open(self):
        """ create cashbook, add lines, try to delete in state 'open'
        """
        pool = Pool()
        Book = pool.get('cashbook.book')

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
                'description': 'test 1',
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('1.0'),
                'party': party.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')

        self.assertRaisesRegex(
            UserError,
            "The cashbook 'Book 1 | 1.00 usd | Open' cannot be deleted" +
            " because it contains 1 lines and is not in the status 'Archive'.",
            Book.delete,
            [book])

    @with_transaction()
    def test_book_check_search_and_sort(self):
        """ create cashbook, check search on balance
        """
        pool = Pool()
        Book = pool.get('cashbook.book')

        types = self.prep_type()
        category = self.prep_category(cattype='in')
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
                'description': 'test 1',
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('10.0'),
                'party': party.id,
                }])],
            }, {
            'name': 'Book 2',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                'date': date(2022, 5, 1),
                'description': 'test 2',
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('100.0'),
                'party': party.id,
                }])],
            }])
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].name, 'Book 1')
        self.assertEqual(books[0].btype.rec_name, 'CAS - Cash')
        self.assertEqual(books[1].name, 'Book 2')
        self.assertEqual(books[1].btype.rec_name, 'CAS - Cash')

        self.assertEqual(
            Book.search_count([('balance', '=', Decimal('10.0'))]),
            1)
        self.assertEqual(
            Book.search_count([('balance', '>', Decimal('5.0'))]),
            2)
        self.assertEqual(
            Book.search_count([('balance', '<', Decimal('5.0'))]),
            0)

        books = Book.search([], order=[('balance', 'ASC')])
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].balance, Decimal('10.0'))
        self.assertEqual(books[1].balance, Decimal('100.0'))

        books = Book.search([], order=[('balance', 'DESC')])
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0].balance, Decimal('100.0'))
        self.assertEqual(books[1].balance, Decimal('10.0'))

        self.assertEqual(
            Book.search_count([('balance_all', '=', Decimal('10.0'))]),
            1)
        self.assertEqual(
            Book.search_count([('balance_all', '>', Decimal('5.0'))]),
            2)
        self.assertEqual(
            Book.search_count([('balance_all', '<', Decimal('5.0'))]),
            0)

        self.assertEqual(
            Book.search_count([('balance_ref', '<', Decimal('5.0'))]),
            0)

    @with_transaction()
    def test_book_deny_btype_set_none(self):
        """ create cashbook, add lines,
            try to set btype to None with lines
        """
        pool = Pool()
        Book = pool.get('cashbook.book')

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
                'description': 'test 1',
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('1.0'),
                'party': party.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.btype.rec_name, 'CAS - Cash')
        self.assertEqual(book.btype.feature, 'gen')
        self.assertEqual(book.feature, 'gen')

        self.assertRaisesRegex(
            UserError,
            "The type cannot be deleted on the cash book 'Book 1 | " +
            "1.00 usd | Open' because it still contains 1 lines.",
            Book.write,
            *[
                [book],
                {
                    'btype': None,
                },
            ])

        Book.write(*[
            [book],
            {
                'lines': [('delete', [book.lines[0].id])],
            }])
        self.assertEqual(len(book.lines), 0)
        self.assertEqual(book.btype.rec_name, 'CAS - Cash')

        Book.write(*[
            [book],
            {
                'btype': None,
            }])
        self.assertEqual(book.btype, None)

    @with_transaction()
    def test_book_deny_delete_closed(self):
        """ create cashbook, add lines, try to delete in state 'closed'
        """
        pool = Pool()
        Book = pool.get('cashbook.book')

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
                'description': 'test 1',
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('1.0'),
                'party': party.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        Book.wfclosed([book])
        self.assertEqual(book.state, 'closed')

        self.assertRaisesRegex(
            UserError,
            "The cashbook 'Book 1 | 1.00 usd | Closed' cannot be " +
            "deleted because it contains 1 lines and is not in the " +
            "status 'Archive'.",
            Book.delete,
            [book])

    @with_transaction()
    def test_book_deny_delete_archive(self):
        """ create cashbook, add lines, try to delete in state 'archive'
        """
        pool = Pool()
        Book = pool.get('cashbook.book')

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
                'description': 'test 1',
                'category': category.id,
                'bookingtype': 'in',
                'amount': Decimal('1.0'),
                'party': party.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        Book.wfclosed([book])
        Book.wfarchive([book])
        self.assertEqual(book.state, 'archive')

        Book.delete([book])

    @with_transaction()
    def test_book_deny_update_1(self):
        """ create cashbook, try to update in states open, closed, archive
        """
        pool = Pool()
        Book = pool.get('cashbook.book')

        types = self.prep_type()
        company = self.prep_company()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')

        Book.write(*[
            [book],
            {
                'name': 'Book 1a',
            }])
        self.assertEqual(book.name, 'Book 1a')

        # wf: open --> closed
        Book.wfclosed([book])
        self.assertEqual(book.state, 'closed')

        self.assertRaisesRegex(
            UserError,
            "The cash book 'Book 1a | 1.00 usd | Closed' is 'Closed' " +
            "and cannot be changed.",
            Book.write,
            *[
                [book],
                {
                    'name': 'Book 1b',
                },
            ])

        Book.wfopen([book])
        self.assertEqual(book.state, 'open')

        Book.write(*[
            [book],
            {
                'name': 'Book 1c',
            }])
        self.assertEqual(book.name, 'Book 1c')

        Book.wfclosed([book])
        Book.wfarchive([book])

        self.assertRaisesRegex(
            UserError,
            "The cash book 'Book 1c | 0.00 usd | Archive' is 'Archive'" +
            " and cannot be changed.",
            Book.write,
            *[
                [book],
                {
                    'name': 'Book 1d',
                },
            ])

    @with_transaction()
    def test_book_permission_owner(self):
        """ create book + 2x users, add users to group, check access
        """
        pool = Pool()
        ResUser = pool.get('res.user')
        ResGroup = pool.get('res.group')
        Book = pool.get('cashbook.book')

        types = self.prep_type()
        company = self.prep_company()
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
            }])
        self.assertEqual(book.rec_name, 'Fridas book | 0.00 usd | Open'),
        self.assertEqual(book.owner.rec_name, 'Frida'),

        with Transaction().set_context({
                '_check_access': True}):
            # change to user 'diego' , try access
            with Transaction().set_user(usr_lst[1].id):
                books = Book.search([])
                self.assertEqual(len(books), 0)

            # change to user 'frida' read/write book
            with Transaction().set_user(usr_lst[0].id):
                books = Book.search([])
                self.assertEqual(len(books), 1)
                self.assertEqual(
                    books[0].rec_name,
                    'Fridas book | 0.00 usd | Open')

                self.assertRaisesRegex(
                    UserError,
                    'You are not allowed to access "Cashbook.Name".',
                    Book.write,
                    *[
                        books,
                        {
                            'name': 'Book2',
                        },
                    ])

    @with_transaction()
    def test_book_permission_reviewer(self):
        """ create book + 2x users + 1x reviewer-group,
            add users to group, check access
        """
        pool = Pool()
        ResUser = pool.get('res.user')
        ResGroup = pool.get('res.group')
        Book = pool.get('cashbook.book')

        types = self.prep_type()
        company = self.prep_company()
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
        # add reviewer-group to allow read for users in group
        book, = Book.create([{
            'name': 'Fridas book',
            'owner': usr_lst[0].id,
            'reviewer': grp_reviewer.id,
            'company': company.id,
            'currency': company.currency.id,
            'btype': types.id,
            'number_sequ': self.prep_sequence().id,
            }])
        self.assertEqual(book.rec_name, 'Fridas book | 0.00 usd | Open'),
        self.assertEqual(book.owner.rec_name, 'Frida'),

        with Transaction().set_context({
                '_check_access': True}):
            # change to user 'diego' , try access
            with Transaction().set_user(usr_lst[1].id):
                books = Book.search([])
                self.assertEqual(len(books), 1)
                self.assertEqual(len(books[0].reviewer.users), 1)
                self.assertEqual(books[0].reviewer.users[0].rec_name, 'Diego')

            # change to user 'frida' read/write book
            with Transaction().set_user(usr_lst[0].id):
                books = Book.search([])
                self.assertEqual(len(books), 1)
                self.assertEqual(
                    books[0].rec_name,
                    'Fridas book | 0.00 usd | Open')

    @with_transaction()
    def test_book_permission_observer(self):
        """ create book + 2x users + 1x observer-group,
            add users to group, check access
        """
        pool = Pool()
        ResUser = pool.get('res.user')
        ResGroup = pool.get('res.group')
        Book = pool.get('cashbook.book')

        types = self.prep_type()
        company = self.prep_company()
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
        # add observer-group to allow read for users in group
        book, = Book.create([{
            'name': 'Fridas book',
            'owner': usr_lst[0].id,
            'observer': grp_observer.id,
            'company': company.id,
            'currency': company.currency.id,
            'btype': types.id,
            'number_sequ': self.prep_sequence().id,
            }])
        self.assertEqual(book.rec_name, 'Fridas book | 0.00 usd | Open'),
        self.assertEqual(book.owner.rec_name, 'Frida'),

        with Transaction().set_context({
                '_check_access': True}):
            # change to user 'diego' , try access
            with Transaction().set_user(usr_lst[1].id):
                books = Book.search([])
                self.assertEqual(len(books), 1)
                self.assertEqual(len(books[0].observer.users), 1)
                self.assertEqual(books[0].observer.users[0].rec_name, 'Diego')

            # change to user 'frida' read/write book
            with Transaction().set_user(usr_lst[0].id):
                books = Book.search([])
                self.assertEqual(len(books), 1)
                self.assertEqual(
                    books[0].rec_name,
                    'Fridas book | 0.00 usd | Open')

# end BookTestCase
