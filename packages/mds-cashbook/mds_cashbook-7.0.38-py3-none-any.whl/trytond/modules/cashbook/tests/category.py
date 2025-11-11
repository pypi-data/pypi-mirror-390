# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError


class CategoryTestCase(object):
    """ test category
    """
    def prep_category(self, name='Cat1', cattype='out'):
        """ create category
        """
        pool = Pool()
        Category = pool.get('cashbook.category')

        company = self.prep_company()
        category, = Category.create([{
            'company': company.id,
            'name': name,
            'cattype': cattype,
            }])
        return category

    @with_transaction()
    def test_category_check_rec_name(self):
        """ create category, test rec_name, search, order
        """
        pool = Pool()
        Category = pool.get('cashbook.category')
        company = self.prep_company()

        Category.create([{
            'company': company.id,
            'name': 'Level 1',
            'cattype': 'in',
            'childs': [('create', [{
                'company': company.id,
                'name': 'Level 2a',
                'cattype': 'in',
                }, {
                'company': company.id,
                'name': 'Level 2b',
                'cattype': 'in',
                }])],
            }, {
            'company': company.id,
            'name': 'Level 1b',
            'cattype': 'in',
            'childs': [('create', [{
                'company': company.id,
                'name': 'Level 1b.2a',
                'cattype': 'in',
                }, {
                'company': company.id,
                'name': 'Level 1b.2b',
                'cattype': 'in',
                }])],
            }])

        self.assertEqual(Category.search_count([
                ('rec_name', 'ilike', '%1b.2b%'),
            ]), 1)
        self.assertEqual(Category.search_count([
                ('rec_name', 'ilike', '%1b.2%'),
            ]), 2)
        self.assertEqual(Category.search_count([
                ('rec_name', '=', 'Level 1b/Level 1b.2b'),
            ]), 1)

        # ordering #1
        categories = Category.search([], order=[('rec_name', 'ASC')])
        self.assertEqual(len(categories), 6)
        self.assertEqual(categories[0].rec_name, 'Level 1')
        self.assertEqual(categories[1].rec_name, 'Level 1b')
        self.assertEqual(categories[2].rec_name, 'Level 1b/Level 1b.2a')
        self.assertEqual(categories[3].rec_name, 'Level 1b/Level 1b.2b')
        self.assertEqual(categories[4].rec_name, 'Level 1/Level 2a')
        self.assertEqual(categories[5].rec_name, 'Level 1/Level 2b')

        # ordering #2
        categories = Category.search([], order=[('rec_name', 'DESC')])
        self.assertEqual(len(categories), 6)
        self.assertEqual(categories[0].rec_name, 'Level 1/Level 2b')
        self.assertEqual(categories[1].rec_name, 'Level 1/Level 2a')
        self.assertEqual(categories[2].rec_name, 'Level 1b/Level 1b.2b')
        self.assertEqual(categories[3].rec_name, 'Level 1b/Level 1b.2a')
        self.assertEqual(categories[4].rec_name, 'Level 1b')
        self.assertEqual(categories[5].rec_name, 'Level 1')

    @with_transaction()
    def test_category_create_check_category_type(self):
        """ create category, update type of category
        """
        pool = Pool()
        Category = pool.get('cashbook.category')
        company = self.prep_company()

        category, = Category.create([{
            'company': company.id,
            'name': 'Level 1',
            'cattype': 'in',
            'childs': [('create', [{
                'company': company.id,
                'name': 'Level 2',
                'cattype': 'in',
                }])],
            }])

        self.assertEqual(category.rec_name, 'Level 1')
        self.assertEqual(category.cattype, 'in')
        self.assertEqual(len(category.childs), 1)
        self.assertEqual(category.childs[0].rec_name, 'Level 1/Level 2')
        self.assertEqual(category.childs[0].cattype, 'in')

        self.assertRaisesRegex(
            UserError,
            'The value "out" for field "Type" in "Level 1/Level 2" of ' +
            '"Category" is not valid according to its domain.',
            Category.write,
            *[
                [category.childs[0]],
                {
                    'cattype': 'out',
                },
            ])

        Category.write(*[
            [category],
            {
                'cattype': 'out',
            }])
        self.assertEqual(category.rec_name, 'Level 1')
        self.assertEqual(category.cattype, 'out')
        self.assertEqual(len(category.childs), 1)
        self.assertEqual(category.childs[0].rec_name, 'Level 1/Level 2')
        self.assertEqual(category.childs[0].cattype, 'out')

    @with_transaction()
    def test_category_create_nodupl_at_root(self):
        """ create category, duplicates are allowed at root-level
        """
        pool = Pool()
        Category = pool.get('cashbook.category')

        company = self.prep_company()

        with Transaction().set_context({
                'company': company.id}):
            cat1, = Category.create([{
                'name': 'Test 1',
                'description': 'Info',
                'cattype': 'in',
                }])
            self.assertEqual(cat1.name, 'Test 1')
            self.assertEqual(cat1.rec_name, 'Test 1')
            self.assertEqual(cat1.description, 'Info')
            self.assertEqual(cat1.company.rec_name, 'm-ds')
            self.assertEqual(cat1.parent, None)

            # duplicate of different type, allowed
            cat2, = Category.create([{
                'name': 'Test 1',
                'description': 'Info',
                'cattype': 'out',
                }])
            self.assertEqual(cat2.name, 'Test 1')
            self.assertEqual(cat2.rec_name, 'Test 1')
            self.assertEqual(cat2.description, 'Info')
            self.assertEqual(cat2.company.rec_name, 'm-ds')
            self.assertEqual(cat2.parent, None)

            # deny duplicate of same type
            self.assertRaisesRegex(
                UserError,
                'The category name already exists at this level.',
                Category.create,
                [{
                    'name': 'Test 1',
                    'description': 'Info',
                    'cattype': 'in',
                }])

    @with_transaction()
    def test_category_create_nodupl_diff_level(self):
        """ create category
        """
        pool = Pool()
        Category = pool.get('cashbook.category')

        company = self.prep_company()

        with Transaction().set_context({
                'company': company.id}):
            cat1, = Category.create([{
                'name': 'Test 1',
                'description': 'Info',
                'childs': [('create', [{
                    'name': 'Test 1',
                    }])],
                }])
            self.assertEqual(cat1.name, 'Test 1')
            self.assertEqual(cat1.rec_name, 'Test 1')
            self.assertEqual(cat1.description, 'Info')
            self.assertEqual(cat1.company.rec_name, 'm-ds')

            self.assertEqual(len(cat1.childs), 1)
            self.assertEqual(cat1.childs[0].rec_name, 'Test 1/Test 1')

    @with_transaction()
    def test_category_create_deny_dupl_at_sublevel(self):
        """ create category
        """
        pool = Pool()
        Category = pool.get('cashbook.category')

        company = self.prep_company()

        with Transaction().set_context({
                'company': company.id}):
            self.assertRaisesRegex(
                UserError,
                'The category name already exists at this level.',
                Category.create,
                [{
                    'name': 'Test 1',
                    'description': 'Info',
                    'childs': [('create', [{
                            'name': 'Test 1',
                        }, {
                            'name': 'Test 1',
                        }])],
                }])

# end CategoryTestCase
