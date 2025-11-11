# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields, Unique, Exclude, tree
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.pyson import Eval, If, Bool
from trytond.exceptions import UserError
from trytond.i18n import gettext
from sql.operators import Equal
from .model import order_name_hierarchical
from .const import DEF_NONE


sel_categorytype = [
    ('in', 'Revenue'),
    ('out', 'Expense'),
    ]


class Category(tree(separator='/'), ModelSQL, ModelView):
    'Category'
    __name__ = 'cashbook.category'

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Char(string='Description', translate=True)
    cattype = fields.Selection(
        string='Type', required=True,
        help='Type of Category', selection=sel_categorytype,
        states={'readonly': Bool(Eval('parent_cattype'))},
        domain=[If(Bool(Eval('parent_cattype')),
                ('cattype', '=', Eval('parent_cattype', '')),
                ())],
        depends=['parent_cattype'])
    parent_cattype = fields.Function(fields.Char(
        string='Parent Category Type',
        readonly=True, states={'invisible': True}),
        'on_change_with_parent_cattype')

    company = fields.Many2One(
        string='Company', model_name='company.company',
        required=True, ondelete="RESTRICT")
    parent = fields.Many2One(
        string="Parent",
        model_name='cashbook.category', ondelete='RESTRICT')
    childs = fields.One2Many(
        string='Children', field='parent',
        model_name='cashbook.category')

    @classmethod
    def __register__(cls, module_name):
        super(Category, cls).__register__(module_name)
        table = cls.__table_handler__(module_name)
        table.drop_column('left')
        table.drop_column('right')
        cls.migrate_sequence(module_name)

    @classmethod
    def __setup__(cls):
        super(Category, cls).__setup__()
        cls._order.insert(0, ('rec_name', 'ASC'))
        t = cls.__table__()
        cls._sql_constraints.extend([
                ('name_uniq',
                    Unique(t, t.name, t.company, t.parent),
                    'cashbook.msg_category_name_unique'),
                ('name2_uniq',
                    Exclude(
                        t,
                        (t.name, Equal),
                        (t.cattype, Equal),
                        where=(t.parent == DEF_NONE)),
                    'cashbook.msg_category_name_unique'),
            ])

    @classmethod
    def migrate_sequence(cls, module_name):
        """ remove colum 'sequence'
        """
        table = cls.__table_handler__(module_name)
        table.drop_column('sequence')

    @classmethod
    def default_cattype(cls):
        return 'out'

    @staticmethod
    def default_company():
        return Transaction().context.get('company') or None

    @staticmethod
    def order_rec_name(tables):
        """ order by pos
            a recursive sorting
        """
        return order_name_hierarchical('cashbook.category', tables)

    @fields.depends('parent', '_parent_parent.cattype')
    def on_change_with_parent_cattype(self, name=None):
        """ get type of parent category or None
        """
        if self.parent:
            return self.parent.cattype

    @classmethod
    def check_category_hierarchy(cls, categories):
        """ check if current category-type is equal to parent
        """
        for category in categories:
            if category.parent:
                if category.parent.cattype != category.cattype:
                    raise UserError(gettext(
                        'cashbook.msg_category_type_not_like_parent',
                        parentname=category.parent.rec_name,
                        catname=category.rec_name,))

    @classmethod
    def create(cls, vlist):
        """ add debit/credit
        """
        records = super(Category, cls).create(vlist)
        cls.check_category_hierarchy(records)
        return records

    @classmethod
    def write(cls, *args):
        """ parent.cattape == cattype,
            update sub-categories
        """
        Category2 = Pool().get('cashbook.category')

        actions = iter(args)
        to_check = []
        to_write = []
        to_write2 = []
        for categories, values in zip(actions, actions):
            to_write2.extend([categories, values])

            if 'cattype' in values.keys():
                # update sub-categories
                cats = Category2.search([
                    ('parent', 'child_of', [x.id for x in categories]),
                    ])
                if len(cats) > 0:
                    to_write.extend([
                        cats,
                        {
                            'cattype': values['cattype'],
                        }])
                to_check.extend(categories)
                to_check.extend(cats)

        # add category-updates after regulary writes
        to_write2.extend(to_write)
        super(Category, cls).write(*to_write2)
        cls.check_category_hierarchy(to_check)

# end Category
