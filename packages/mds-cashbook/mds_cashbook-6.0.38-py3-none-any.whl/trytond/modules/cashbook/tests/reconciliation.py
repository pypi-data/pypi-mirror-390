# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.exceptions import UserError
from datetime import date
from decimal import Decimal


class ReconTestCase(object):
    """ test reconciliation
    """
    @with_transaction()
    def test_recon_check_overlap_start(self):
        """ create, check deny of overlap date - date_from
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Reconciliation = pool.get('cashbook.recon')

        types = self.prep_type()
        self.prep_category(cattype='in')
        company = self.prep_company()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'reconciliations': [('create', [{
                'date': date(2022, 5, 1),
                'date_from': date(2022, 5, 1),
                'date_to': date(2022, 5, 31),
                }])],
            }])

        Book.write(*[
            [book], {'reconciliations': [('create', [{
                'date': date(2022, 6, 1),
                'date_from': date(2022, 6, 1),
                'date_to': date(2022, 6, 30),
                }])],
            }])
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/31/2022 - 06/30/2022 | 0.00 usd - 0.00 usd [0]')
        self.assertEqual(
            book.reconciliations[1].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]')

        self.assertRaisesRegex(
            UserError,
            'The date range overlaps with another reconciliation.',
            Reconciliation.write,
            *[
                [book.reconciliations[0]],
                {
                    'date_from': date(2022, 4, 15),
                    'date_to': date(2022, 5, 2),
                },
            ])

    @with_transaction()
    def test_recon_check_overlap_end(self):
        """ create, check deny of overlap date - date_to
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Reconciliation = pool.get('cashbook.recon')

        types = self.prep_type()
        self.prep_category(cattype='in')
        company = self.prep_company()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'reconciliations': [('create', [{
                'date': date(2022, 5, 1),
                'date_from': date(2022, 5, 1),
                'date_to': date(2022, 5, 31),
                }])],
            }])

        Book.write(*[
            [book], {'reconciliations': [('create', [{
                'date': date(2022, 6, 1),
                'date_from': date(2022, 6, 1),
                'date_to': date(2022, 6, 30),
                }])],
            }])
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/31/2022 - 06/30/2022 | 0.00 usd - 0.00 usd [0]')
        self.assertEqual(
            book.reconciliations[1].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]')

        self.assertRaisesRegex(
            UserError,
            'The date range overlaps with another reconciliation.',
            Reconciliation.write,
            *[
                [book.reconciliations[0]],
                {
                    'date_from': date(2022, 5, 30),
                },
            ])

    @with_transaction()
    def test_recon_check_overlap_inside(self):
        """ create, check deny of overlap date - inside of period
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Reconciliation = pool.get('cashbook.recon')

        types = self.prep_type()
        self.prep_category(cattype='in')
        company = self.prep_company()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'reconciliations': [('create', [{
                'date': date(2022, 5, 1),
                'date_from': date(2022, 5, 1),
                'date_to': date(2022, 5, 31),
                }])],
            }])

        Book.write(*[
            [book], {'reconciliations': [('create', [{
                'date': date(2022, 6, 1),
                'date_from': date(2022, 6, 1),
                'date_to': date(2022, 6, 30),
                }])],
            }])
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/31/2022 - 06/30/2022 | 0.00 usd - 0.00 usd [0]')
        self.assertEqual(
            book.reconciliations[1].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]')

        self.assertRaisesRegex(
            UserError,
            'The date range overlaps with another reconciliation.',
            Reconciliation.write,
            *[
                [book.reconciliations[0]],
                {
                    'date_from': date(2022, 5, 5),
                    'date_to': date(2022, 5, 15),
                },
            ])

    @with_transaction()
    def test_recon_check_overlap_enclose(self):
        """ create, check deny of overlap date - enclose a period
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Reconciliation = pool.get('cashbook.recon')

        types = self.prep_type()
        self.prep_category(cattype='in')
        company = self.prep_company()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'reconciliations': [('create', [{
                'date': date(2022, 5, 1),
                'date_from': date(2022, 5, 1),
                'date_to': date(2022, 5, 31),
                }])],
            }])

        Book.write(*[
            [book], {'reconciliations': [('create', [{
                'date': date(2022, 6, 1),
                'date_from': date(2022, 6, 1),
                'date_to': date(2022, 6, 30),
                }])],
            }])
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/31/2022 - 06/30/2022 | 0.00 usd - 0.00 usd [0]')
        self.assertEqual(
            book.reconciliations[1].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]')

        self.assertRaisesRegex(
            UserError,
            'The date range overlaps with another reconciliation.',
            Reconciliation.write,
            *[
                [book.reconciliations[1]],
                {
                    'date_from': date(2022, 4, 25),
                    'date_to': date(2022, 6, 10),
                },
            ])

    @with_transaction()
    def test_recon_set_start_amount_by_cashbook(self):
        """ set stat-amount from cashbook-setting
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Reconciliation = pool.get('cashbook.recon')

        types = self.prep_type()
        company = self.prep_company()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'start_date': date(2022, 5, 1),
            'number_sequ': self.prep_sequence().id,
            'reconciliations': [('create', [{
                    'date': date(2022, 5, 28),
                    'date_from': date(2022, 5, 1),
                    'date_to':  date(2022, 5, 31),
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]')
        self.assertEqual(book.reconciliations[0].feature, 'gen')

        Reconciliation.wfcheck(list(book.reconciliations))
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]')

    @with_transaction()
    def test_recon_set_start_amount_by_predecessor(self):
        """ set stat-amount from end_amount of predecessor
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Lines = pool.get('cashbook.line')
        Reconciliation = pool.get('cashbook.recon')

        types = self.prep_type()
        company = self.prep_company()
        category = self.prep_category(cattype='in')
        party = self.prep_party()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'start_date': date(2022, 5, 1),
            'number_sequ': self.prep_sequence().id,
            'reconciliations': [('create', [{
                    'date': date(2022, 5, 28),
                    'date_from': date(2022, 5, 1),
                    'date_to':  date(2022, 5, 31),
                }])],
            'lines': [('create', [{
                    'date': date(2022, 5, 5),
                    'bookingtype': 'in',
                    'category': category.id,
                    'description': 'Line 1',
                    'amount': Decimal('5.0'),
                    'party': party.id,
                }, {
                    'date': date(2022, 5, 5),
                    'bookingtype': 'in',
                    'category': category.id,
                    'description': 'Line 2',
                    'party': party.id,
                    'amount': Decimal('7.0'),
                },])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(len(book.reconciliations), 1)
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]')
        self.assertEqual(len(book.reconciliations[0].lines), 0)

        Lines.wfcheck(list(book.lines))
        Reconciliation.wfcheck(list(book.reconciliations))

        self.assertEqual(book.reconciliations[0].state, 'check')
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 12.00 usd [2]')
        Reconciliation.wfdone(list(book.reconciliations))
        self.assertEqual(book.reconciliations[0].state, 'done')

        recons = Reconciliation.create([{
            'cashbook': book.id,
            'date_from': date(2022, 5, 31),
            'date_to': date(2022, 6, 30),
            }])
        self.assertEqual(
            recons[0].rec_name,
            '05/31/2022 - 06/30/2022 | 0.00 usd - 0.00 usd [0]')
        Reconciliation.wfcheck(recons)
        self.assertEqual(
            recons[0].rec_name,
            '05/31/2022 - 06/30/2022 | 12.00 usd - 12.00 usd [0]')

    @with_transaction()
    def test_recon_predecessor_done(self):
        """ predecessor must be done
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Reconciliation = pool.get('cashbook.recon')

        types = self.prep_type()
        company = self.prep_company()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'reconciliations': [('create', [{
                    'date': date(2022, 5, 28),
                    'date_from': date(2022, 5, 1),
                    'date_to':  date(2022, 5, 31),
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        Reconciliation.wfcheck(list(book.reconciliations))
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]')
        self.assertEqual(book.reconciliations[0].state, 'check')

        recons = Reconciliation.create([{
            'cashbook': book.id,
            'date_from': date(2022, 5, 31),
            'date_to': date(2022, 6, 30),
            }])
        self.assertRaisesRegex(
            UserError,
            "The predecessor " +
            "'05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]' " +
            "must be in the 'Done' state before you can check the " +
            "current reconciliation " +
            "'05/31/2022 - 06/30/2022 | 0.00 usd - 0.00 usd [0]'.",
            Reconciliation.wfcheck,
            recons)

    @with_transaction()
    def test_recon_autoset_date_to(self):
        """ create reconciliation, check:
            set date_to to last date of checked-line
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Line = pool.get('cashbook.line')
        Reconciliation = pool.get('cashbook.recon')

        types = self.prep_type()
        company = self.prep_company()
        party = self.prep_party()
        category = self.prep_category(cattype='in')
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'lines': [('create', [{
                'date': date(2022, 5, 5),
                'amount': Decimal('10.0'),
                'bookingtype': 'in',
                'party': party.id,
                'category': category.id,
                }, {
                'date': date(2022, 5, 18),
                'amount': Decimal('5.0'),
                'bookingtype': 'in',
                'party': party.id,
                'category': category.id,
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        Line.wfcheck(list(book.lines))

        recon, = Reconciliation.create([{
                'cashbook': book.id,
                'date': date(2022, 5, 28),
                'date_from': date(2022, 5, 5),
                'date_to':  date(2022, 5, 31),
            }])
        # dates are updates by .create()
        self.assertEqual(
            recon.rec_name,
            '05/01/2022 - 05/18/2022 | 0.00 usd - 0.00 usd [0]')

        Reconciliation.wfcheck([recon])
        self.assertEqual(
            recon.rec_name,
            '05/01/2022 - 05/18/2022 | 0.00 usd - 15.00 usd [2]')

    @with_transaction()
    def test_recon_autoset_date_from(self):
        """ create reconciliation, check: set date_from to end of predecessor
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Reconciliation = pool.get('cashbook.recon')

        types = self.prep_type()
        company = self.prep_company()
        book, = Book.create([{
            'name': 'Book 1',
            'btype': types.id,
            'company': company.id,
            'currency': company.currency.id,
            'number_sequ': self.prep_sequence().id,
            'start_date': date(2022, 5, 1),
            'reconciliations': [('create', [{
                    'date': date(2022, 5, 28),
                    'date_from': date(2022, 5, 5),
                    'date_to':  date(2022, 5, 31),
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        Reconciliation.wfcheck([book.reconciliations[0]])
        Reconciliation.wfdone([book.reconciliations[0]])

        # date_from is corrected by .create() to start_date of book
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]')

        r2, = Reconciliation.create([{
            'cashbook': book.id,
            'date_from': date(2022, 6, 10),
            'date_to': date(2022, 6, 30),
            }])
        self.assertEqual(
            r2.rec_name,
            '05/31/2022 - 06/30/2022 | 0.00 usd - 0.00 usd [0]')

        # update 'date_from' to wrong value
        Reconciliation.write(*[
            [r2],
            {
                'date_from': date(2022, 6, 1),
            }])
        self.assertEqual(
            r2.rec_name,
            '06/01/2022 - 06/30/2022 | 0.00 usd - 0.00 usd [0]')

        self.assertRaisesRegex(
            UserError,
            "The start date '06/01/2022' of the current reconciliation" +
            " '06/01/2022 - 06/30/2022 | 0.00 usd - 0.00 usd [0]' " +
            "must correspond to the end date '05/31/2022' of the predecessor.",
            Reconciliation.wfcheck,
            [r2])

    @with_transaction()
    def test_recon_create_check_line_add_to_recon(self):
        """ create, booklines, add reconciliation
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
                    'date': date(2022, 5, 5),
                    'description': 'Text 2',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            'reconciliations': [('create', [{
                    'date': date(2022, 5, 28),
                    'date_from': date(2022, 5, 1),
                    'date_to':  date(2022, 5, 31),
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        self.assertEqual(len(book.lines), 2)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(
            book.lines[1].rec_name,
            '05/05/2022|Rev|1.00 usd|Text 2 [Cat1]')
        self.assertEqual(len(book.reconciliations), 1)
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]')
        self.assertEqual(len(book.reconciliations[0].lines), 0)

        self.assertRaisesRegex(
            UserError,
            "For reconciliation, the line " +
            "'05/01/2022|Rev|1.00 usd|Text 1 [Cat1]' must be in the " +
            "status 'Check' or 'Done'.",
            Lines.write,
            *[
                [book.lines[0]],
                {
                    'reconciliation': book.reconciliations[0].id,
                }
            ])
        Lines.wfcheck(book.lines)

        Lines.write(*[
            list(book.lines),
            {
                'reconciliation': book.reconciliations[0].id,
            }])
        self.assertEqual(len(book.reconciliations[0].lines), 2)

        self.assertRaisesRegex(
            UserError,
            "The status cannot be changed to 'Edit' as long as the line " +
            "'05/01/2022|1.00 usd|Text 1 [Cat1]' is associated " +
            "with a reconciliation.",
            Lines.wfedit,
            [book.lines[0]])

        # unlink lines from reconciliation
        self.assertEqual(book.reconciliations[0].state, 'edit')
        self.assertEqual(len(book.reconciliations[0].lines), 2)
        Reconciliation.wfcheck(list(book.reconciliations))
        Reconciliation.wfedit(list(book.reconciliations))
        self.assertEqual(book.reconciliations[0].state, 'edit')
        self.assertEqual(len(book.reconciliations[0].lines), 0)

        # move date of 2nd line to june 1
        # set reconciliation to 'check'
        Lines.wfedit([book.lines[1]])
        Lines.write(*[
            [book.lines[1]],
            {
                'date': date(2022, 6, 1),
            }])
        # check reconciliation, this linkes the 1st line by date
        Reconciliation.wfcheck(list(book.reconciliations))
        self.assertEqual(book.reconciliations[0].state, 'check')
        self.assertEqual(len(book.reconciliations[0].lines), 1)
        self.assertEqual(
            book.reconciliations[0].lines[0].rec_name,
            '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(book.lines[0].state, 'check')
        self.assertEqual(
            book.lines[1].rec_name,
            '06/01/2022|Rev|1.00 usd|Text 2 [Cat1]')
        self.assertEqual(book.lines[1].state, 'edit')

        # move 1st line into date-range of checked-reconciliation, wf-check
        Lines.write(*[
            [book.lines[1]],
            {
                'date': date(2022, 5, 20),
            }])
        self.assertRaisesRegex(
            UserError,
            "For the date '05/20/2022' there is already a completed " +
            "reconciliation. Use a different date.",
            Lines.wfcheck,
            [book.lines[1]])

        # set date to end of date-range of reconciliation
        # should work
        Lines.write(*[
            [book.lines[1]],
            {
                'date': date(2022, 5, 31),
            }])
        Lines.wfcheck([book.lines[1]])  # ok
        Lines.wfedit([book.lines[1]])
        Lines.write(*[
            [book.lines[1]],
            {
                'date': date(2022, 7, 1),
            }])

        # add 2nd reconciliation
        recon2, = Reconciliation.create([{
            'cashbook': book.id,
            'date_from': date(2022, 5, 31),
            'date_to': date(2022, 6, 30),
            }])
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/31/2022 - 06/30/2022 | 0.00 usd - 0.00 usd [0]')
        self.assertEqual(
            book.reconciliations[1].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 1.00 usd [1]')
        Reconciliation.wfdone([book.reconciliations[1]])
        Reconciliation.wfcheck([recon2])

        Lines.write(*[
            [book.lines[1]],
            {
                'date': date(2022, 5, 31),
            }])
        self.assertRaisesRegex(
            UserError,
            "For the date '05/31/2022' there is already a completed " +
            "reconciliation. Use a different date.",
            Lines.wfcheck,
            [book.lines[1]])

    @with_transaction()
    def test_recon_check_wfcheck_missing_lines(self):
        """ create, booklines, check missing line at wfcheck
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
                    'date': date(2022, 6, 5),
                    'description': 'Text 2',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            'reconciliations': [('create', [{
                    'date': date(2022, 5, 28),
                    'date_from': date(2022, 5, 1),
                    'date_to':  date(2022, 5, 31),
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        self.assertEqual(len(book.lines), 2)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(
            book.lines[1].rec_name,
            '06/05/2022|Rev|1.00 usd|Text 2 [Cat1]')

        Lines.wfcheck([book.lines[0]])
        Reconciliation.wfcheck([book.reconciliations[0]])
        self.assertEqual(len(book.reconciliations[0].lines), 1)
        self.assertEqual(
            book.reconciliations[0].lines[0].rec_name,
            '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')

        Lines.write(*[
            [book.lines[1]],
            {
                'date': date(2022, 5, 15),
            }])

        self.assertRaisesRegex(
            UserError,
            "In the date range from 05/01/2022 to 05/31/2022, " +
            "there are still cashbook lines that do not belong " +
            "to any reconciliation.",
            Reconciliation.wfdone,
            [book.reconciliations[0]])

    @with_transaction()
    def test_recon_check_deny_delete(self):
        """ create, booklines, reconciliation, try delete
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
                }])],
            'reconciliations': [('create', [{
                    'date': date(2022, 5, 28),
                    'date_from': date(2022, 5, 1),
                    'date_to':  date(2022, 5, 31),
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')

        Lines.wfcheck(list(book.lines))
        Reconciliation.wfcheck(list(book.reconciliations))
        self.assertEqual(len(book.reconciliations), 1)
        self.assertEqual(len(book.reconciliations[0].lines), 1)

        self.assertRaisesRegex(
            UserError,
            "The reconciliation '05/01/2022 - 05/31/2022 " +
            "| 0.00 - 0.00 usd [0]' cannot be deleted, its in state 'Check'.",
            Reconciliation.delete,
            list(book.reconciliations))

        Book.wfclosed([book])

        self.assertRaisesRegex(
            UserError,
            "The cashbook line '05/01/2022 - 05/31/2022: 0.00 usd' " +
            "cannot be deleted because the Cashbook " +
            "'Book 1 | 1.00 usd | Closed' is in state 'Closed'.",
            Reconciliation.delete,
            list(book.reconciliations))

        self.assertRaisesRegex(
            UserError,
            "The cash book 'Book 1 | 1.00 usd | Closed' is 'Closed' " +
            "and cannot be changed.",
            Reconciliation.write,
            *[
                list(book.reconciliations),
                {
                    'date': date(2022, 5, 29),
                },
            ])

    @with_transaction()
    def test_recon_check_wf_edit_to_check(self):
        """ create, booklines, add reconciliation
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
                    'date': date(2022, 5, 5),
                    'description': 'Text 2',
                    'category': category.id,
                    'bookingtype': 'in',
                    'amount': Decimal('1.0'),
                    'party': party.id,
                }])],
            'reconciliations': [('create', [{
                    'date': date(2022, 5, 28),
                    'date_from': date(2022, 5, 1),
                    'date_to':  date(2022, 5, 31),
                }])],
            }])
        self.assertEqual(book.name, 'Book 1')
        self.assertEqual(book.state, 'open')
        self.assertEqual(len(book.lines), 2)
        self.assertEqual(
            book.lines[0].rec_name,
            '05/01/2022|Rev|1.00 usd|Text 1 [Cat1]')
        self.assertEqual(
            book.lines[1].rec_name,
            '05/05/2022|Rev|1.00 usd|Text 2 [Cat1]')
        self.assertEqual(book.lines[0].reconciliation, None)
        self.assertEqual(book.lines[1].reconciliation, None)
        self.assertEqual(len(book.reconciliations), 1)
        self.assertEqual(
            book.reconciliations[0].rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 0.00 usd [0]')
        self.assertEqual(len(book.reconciliations[0].lines), 0)

        # run wf, fail with lines not 'checked'
        self.assertRaisesRegex(
            UserError,
            "For the reconciliation '05/01/2022 - 05/31/2022 | " +
            "0.00 usd - 0.00 usd [0]' of the cashbook " +
            "'Book 1 | 2.00 usd | Open', all lines in the date range " +
            "from '05/01/2022' to '05/31/2022' must be in the 'Check' state.",
            Reconciliation.wfcheck,
            list(book.reconciliations),
            )

        # edit --> check
        Lines.wfcheck(book.lines)
        Reconciliation.wfcheck(list(book.reconciliations))
        self.assertEqual(len(book.reconciliations[0].lines), 2)
        self.assertEqual(
            book.lines[0].reconciliation.rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 2.00 usd [2]')
        self.assertEqual(
            book.lines[1].reconciliation.rec_name,
            '05/01/2022 - 05/31/2022 | 0.00 usd - 2.00 usd [2]')

        # check --> edit
        Reconciliation.wfedit(list(book.reconciliations))
        self.assertEqual(len(book.reconciliations[0].lines), 0)
        self.assertEqual(book.lines[0].reconciliation, None)
        self.assertEqual(book.lines[1].reconciliation, None)

# end ReconTestCase
