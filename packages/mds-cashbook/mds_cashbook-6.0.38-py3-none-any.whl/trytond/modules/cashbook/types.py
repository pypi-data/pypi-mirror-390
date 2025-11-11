# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.transaction import Transaction
from trytond.i18n import gettext


class Type(ModelSQL, ModelView):
    'Cashbook Type'
    __name__ = 'cashbook.type'

    name = fields.Char(string='Name', required=True, translate=True)
    short = fields.Char(string='Abbreviation', required=True, size=3)
    company = fields.Many2One(
        string='Company', model_name='company.company',
        required=True, ondelete="RESTRICT")
    feature = fields.Selection(
        string='Feature', required=True,
        selection='get_sel_feature', select=True,
        help='Select feature set of the Cashbook.')

    @classmethod
    def __setup__(cls):
        super(Type, cls).__setup__()
        cls._order.insert(0, ('name', 'ASC'))
        t = cls.__table__()
        cls._sql_constraints.extend([
            ('code_uniq',
                Unique(t, t.short),
                'cashbook.msg_type_short_unique'),
            ])

    @classmethod
    def default_feature(cls):
        """ default: general
        """
        return 'gen'

    @classmethod
    def get_sel_feature(cls):
        """ get feature-modes
        """
        return [('gen', gettext('cashbook.msg_btype_general'))]

    def get_rec_name(self, name):
        """ short + name
        """
        return '%(short)s - %(name)s' % {
            'short': self.short or '-',
            'name': self.name or '-'}

    @classmethod
    def search_rec_name(cls, name, clause):
        """ search in name + short
        """
        return [
            'OR',
            ('name',) + tuple(clause[1:]),
            ('short',) + tuple(clause[1:])]

    @staticmethod
    def default_company():
        return Transaction().context.get('company') or None

# end Type
