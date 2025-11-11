# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.modules.company.tests import create_company
from datetime import date
from decimal import Decimal


class ConfigTestCase(object):
    """ test config
    """
    def prep_company(self):
        """ get/create company
        """
        Company = Pool().get('company.company')

        company = Company.search([])
        if len(company) > 0:
            company = company[0]
        else:
            company = create_company(name='m-ds')
        return company

    def prep_config(self):
        """ store config
        """
        Configuration = Pool().get('cashbook.configuration')

        cfg1 = Configuration()
        cfg1.save()

        cfg2 = Configuration.get_singleton()
        self.assertEqual(cfg2.date_from, None)
        self.assertEqual(cfg2.date_to, None)
        self.assertEqual(cfg2.checked, True)
        self.assertEqual(cfg2.done, False)
        self.assertEqual(cfg2.catnamelong, True)
        self.assertEqual(cfg2.defbook, None)
        return cfg2

    def prep_party(self, name='Party'):
        """ new party
        """
        Party = Pool().get('party.party')
        party, = Party.create([{
            'name': name,
            'addresses': [('create', [{}])],
            }])
        return party

    def prep_2nd_currency(self, company):
        """ add EUR as 2nd currency
        """
        pool = Pool()
        Currency = pool.get('currency.currency')
        CurrencyRate = pool.get('currency.currency.rate')
        Company = pool.get('company.company')

        usd, = Currency.search([('name', '=', 'usd')])
        euros = Currency.search([('code', '=', 'EUR')])
        if len(euros) == 0:
            euro, = Currency.create([{
                'name': 'Euro',
                'symbol': '€',
                'code': 'EUR',
                'numeric_code': '978',
                'rounding': Decimal('0.01'),
                'digits': 2,
                }])
        else:
            euro = euros[0]

        # set company-currency to euro
        self.assertEqual(company.currency.name, 'usd')
        Company.write(*[
            [company],
            {
                'currency': euro.id,
            }])
        self.assertEqual(company.currency.name, 'Euro')

        # add rate for euro/usd @ 05/02/2022
        # EUR is base-currency
        CurrencyRate.create([{
            'date': date(2022, 5, 2),
            'currency': euro.id,
            'rate': Decimal('1.0'),
            }, {
            'date': date(2022, 5, 2),
            'currency': usd.id,
            'rate': Decimal('1.05'),
            }])

        # delete unwanted rates
        usd_1 = CurrencyRate.search([
            ('currency.id', '=', usd.id),
            ('date', '!=', date(2022, 5, 2)),
            ])
        CurrencyRate.delete(usd_1)

        return (usd, euro)

    @with_transaction()
    def test_config_create(self):
        """ create config
        """
        self.prep_config()

    @with_transaction()
    def test_config_defbook(self):
        """ create config, add default-cashbook
        """
        pool = Pool()
        Configuration = pool.get('cashbook.configuration')
        Book = pool.get('cashbook.book')

        self.prep_config()
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

        cfg1 = Configuration.get_singleton()

        Configuration.write(*[
            [cfg1],
            {
                'defbook': book.id,
            }])

        cfg2 = Configuration.get_singleton()
        self.assertEqual(cfg2.defbook.rec_name, 'Book 1 | 0.00 usd | Open')

    @with_transaction()
    def test_config_create_multi_user(self):
        """ create config, multi-user
        """
        pool = Pool()
        Configuration = pool.get('cashbook.configuration')
        ResUser = pool.get('res.user')
        ResGroup = pool.get('res.group')

        grp_cb, = ResGroup.search([('name', '=', 'Cashbook')])

        usr_lst = ResUser.create([{
            'login': 'frida',
            'name': 'Frida',
            'groups': [('add', [grp_cb.id])],
            }, {
            'login': 'diego',
            'name': 'Diego',
            'groups': [('add', [grp_cb.id])],
            }])
        self.assertEqual(len(usr_lst), 2)
        self.assertEqual(usr_lst[0].name, 'Frida')
        self.assertEqual(usr_lst[1].name, 'Diego')

        with Transaction().set_context({
                '_check_access': True}):
            # change to user 'frida'
            with Transaction().set_user(usr_lst[0].id):
                cfg1 = Configuration()
                cfg1.save()

                cfg2 = Configuration.get_singleton()
                self.assertEqual(cfg2.date_from, None)
                self.assertEqual(cfg2.date_to, None)
                self.assertEqual(cfg2.checked, True)
                self.assertEqual(cfg2.done, False)
                self.assertEqual(cfg2.fixate, False)

                cfg2.date_from = date(2022, 4, 1)
                cfg2.date_to = date(2022, 5, 30)
                cfg2.checked = False
                cfg2.fixate = True
                cfg2.save()

            # change to user 'diego'
            with Transaction().set_user(usr_lst[1].id):
                cfg1 = Configuration()
                cfg1.save()

                cfg2 = Configuration.get_singleton()
                self.assertEqual(cfg2.date_from, None)
                self.assertEqual(cfg2.date_to, None)
                self.assertEqual(cfg2.checked, True)
                self.assertEqual(cfg2.done, False)
                self.assertEqual(cfg2.fixate, False)

                cfg2.date_from = date(2022, 4, 15)
                cfg2.date_to = date(2022, 5, 15)
                cfg2.save()

            # change to user 'frida' - check
            with Transaction().set_user(usr_lst[0].id):
                cfg1 = Configuration()
                cfg1.save()

                cfg2 = Configuration.get_singleton()
                self.assertEqual(cfg2.date_from, date(2022, 4, 1))
                self.assertEqual(cfg2.date_to, date(2022, 5, 30))
                self.assertEqual(cfg2.checked, False)
                self.assertEqual(cfg2.done, False)
                self.assertEqual(cfg2.fixate, True)

# end ConfigTestCase
