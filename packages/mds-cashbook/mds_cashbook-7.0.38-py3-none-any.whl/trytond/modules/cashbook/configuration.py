# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import ModelSingleton, ModelView, ModelSQL, fields
from .model import UserMultiValueMixin, UserValueMixin
from trytond.pyson import Eval, If
from trytond.pool import Pool


field_checked = fields.Boolean(
    string='Checked',
    help='Show cashbook lines in Checked-state.')
field_done = fields.Boolean(
    string='Done',
    help='Show cashbook lines in Done-state.')
field_catnamelong = fields.Boolean(
    string='Category: Show long name',
    help='Shows the long name of the category in the Category ' +
    'field of a cash book line.')


class Configuration(ModelSingleton, ModelSQL, ModelView, UserMultiValueMixin):
    'Configuration'
    __name__ = 'cashbook.configuration'

    date_from = fields.MultiValue(fields.Date(
        string='Start Date', depends=['date_to'],
        domain=[
            If(Eval('date_to') & Eval('date_from'),
                ('date_from', '<=', Eval('date_to')),
                ())]))
    date_to = fields.MultiValue(fields.Date(
        string='End Date', depends=['date_from'],
        domain=[
            If(Eval('date_to') & Eval('date_from'),
                ('date_from', '<=', Eval('date_to')),
                ())]))
    checked = fields.MultiValue(field_checked)
    done = fields.MultiValue(field_done)
    catnamelong = fields.MultiValue(field_catnamelong)
    defbook = fields.MultiValue(fields.Many2One(
        string='Default Cashbook',
        help='The default cashbook is selected when you open ' +
        'the booking wizard.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[('btype', '!=', None), ('state', '=', 'open')]))
    book1 = fields.MultiValue(fields.Many2One(
        string='Cashbook 1',
        help='Cash book available in selection dialog.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[('btype', '!=', None), ('state', '=', 'open')]))
    book2 = fields.MultiValue(fields.Many2One(
        string='Cashbook 2',
        help='Cash book available in selection dialog.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[('btype', '!=', None), ('state', '=', 'open')]))
    book3 = fields.MultiValue(fields.Many2One(
        string='Cashbook 3',
        help='Cash book available in selection dialog.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[('btype', '!=', None), ('state', '=', 'open')]))
    book4 = fields.MultiValue(fields.Many2One(
        string='Cashbook 4',
        help='Cash book available in selection dialog.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[('btype', '!=', None), ('state', '=', 'open')]))
    book5 = fields.MultiValue(fields.Many2One(
        string='Cashbook 5',
        help='Cash book available in selection dialog.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[('btype', '!=', None), ('state', '=', 'open')]))
    fixate = fields.MultiValue(fields.Boolean(
        string='Check booking', help='Check of the booking is activated.'))

    @classmethod
    def multivalue_model(cls, field):
        """ get model for value
        """
        pool = Pool()

        if field in [
                'date_from', 'date_to', 'checked', 'done',
                'catnamelong', 'defbook', 'book1', 'book2',
                'book3', 'book4', 'book5', 'fixate']:
            return pool.get('cashbook.configuration_user')
        return super(Configuration, cls).multivalue_model(field)

    @classmethod
    def default_checked(cls, **pattern):
        return cls.multivalue_model('checked').default_checked()

    @classmethod
    def default_done(cls, **pattern):
        return cls.multivalue_model('done').default_done()

    @classmethod
    def default_catnamelong(cls, **pattern):
        return cls.multivalue_model('catnamelong').default_catnamelong()

    @classmethod
    def default_fixate(cls, **pattern):
        return cls.multivalue_model('fixate').default_fixate()

# end Configuration


class UserConfiguration(ModelSQL, UserValueMixin):
    'User Configuration'
    __name__ = 'cashbook.configuration_user'

    date_from = fields.Date(
        string='Start Date', depends=['date_to'],
        domain=[
            If(Eval('date_to') & Eval('date_from'),
                ('date_from', '<=', Eval('date_to')),
                ())])
    date_to = fields.Date(
        string='End Date', depends=['date_from'],
        domain=[
            If(Eval('date_to') & Eval('date_from'),
                ('date_from', '<=', Eval('date_to')),
                ())])
    checked = field_checked
    done = field_done
    catnamelong = field_catnamelong
    defbook = fields.Many2One(
        string='Default Cashbook',
        help='The default cashbook is selected when you open ' +
        'the booking wizard.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[
            ('btype', '!=', None),
            ('state', '=', 'open'),
            ('owner.id', '=', Eval('iduser', -1))
        ], depends=['iduser'])
    book1 = fields.Many2One(
        string='Cashbook 1',
        help='Cash book available in selection dialog.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[
            ('btype', '!=', None),
            ('state', '=', 'open'),
            ('owner.id', '=', Eval('iduser', -1))
        ], depends=['iduser'])
    book2 = fields.Many2One(
        string='Cashbook 2',
        help='Cash book available in selection dialog.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[
            ('btype', '!=', None),
            ('state', '=', 'open'),
            ('owner.id', '=', Eval('iduser', -1))
        ], depends=['iduser'])
    book3 = fields.Many2One(
        string='Cashbook 3',
        help='Cash book available in selection dialog.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[
            ('btype', '!=', None),
            ('state', '=', 'open'),
            ('owner.id', '=', Eval('iduser', -1))
        ], depends=['iduser'])
    book4 = fields.Many2One(
        string='Cashbook 4',
        help='Cash book available in selection dialog.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[
            ('btype', '!=', None),
            ('state', '=', 'open'),
            ('owner.id', '=', Eval('iduser', -1))
        ], depends=['iduser'])
    book5 = fields.Many2One(
        string='Cashbook 5',
        help='Cash book available in selection dialog.',
        model_name='cashbook.book', ondelete='SET NULL',
        domain=[
            ('btype', '!=', None),
            ('state', '=', 'open'),
            ('owner.id', '=', Eval('iduser', -1))
        ], depends=['iduser'])

    fixate = fields.Boolean(
        string='Fixate', help='Fixating of the booking is activated.')

    @classmethod
    def default_checked(cls):
        return True

    @classmethod
    def default_catnamelong(cls):
        return True

    @classmethod
    def default_done(cls):
        return False

    @classmethod
    def default_fixate(cls):
        return False

# end UserConfiguration
