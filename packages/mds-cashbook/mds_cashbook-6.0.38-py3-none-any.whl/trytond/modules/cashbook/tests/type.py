# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError


class TypeTestCase(object):
    """ test types
    """
    def prep_type(self, name='Cash', short='CAS'):
        """ create book-type
        """
        AccType = Pool().get('cashbook.type')

        company = self.prep_company()
        at, = AccType.create([{
            'name': name,
            'short': short,
            'company': company.id,
            }])
        self.assertEqual(at.name, name)
        self.assertEqual(at.short, short)
        return at

    @with_transaction()
    def test_type_create(self):
        """ create account type
        """
        AccType = Pool().get('cashbook.type')

        company = self.prep_company()

        at, = AccType.create([{
            'name': 'Test 1',
            'short': 'T1',
            'company': company.id,
            }])
        self.assertEqual(at.name, 'Test 1')
        self.assertEqual(at.short, 'T1')

        # check unique of short
        self.assertRaisesRegex(UserError,
            'The Abbreviation must be unique.',
            AccType.create,
            [{
            'name': 'Test 2',
            'short': 'T1',
            'company': company.id,
            }])

# end TypeTestCase
