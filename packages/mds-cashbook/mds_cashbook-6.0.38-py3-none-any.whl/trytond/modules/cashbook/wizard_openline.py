# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import ModelView, fields
from trytond.pyson import PYSONEncoder
from trytond.wizard import Wizard, StateView, StateTransition, \
    StateAction, Button
from trytond.i18n import gettext
from trytond.pool import Pool
from trytond.exceptions import UserError
from trytond.transaction import Transaction


class OLineMixin:
    """ mixin to extend action-data
    """
    def add_action_data(self, book):
        """ add book and cfg
        """
        Configuration = Pool().get('cashbook.configuration')
        cfg1 = Configuration.get_singleton()
        action = {
            'pyson_context': PYSONEncoder().encode({
                'cashbook': getattr(book, 'id', None),
                'date_from': getattr(cfg1, 'date_from', None),
                'date_to': getattr(cfg1, 'date_to', None),
                'checked': getattr(cfg1, 'checked', None),
                'done': getattr(cfg1, 'done', None),
                }),
            'name': '%(name)s: %(cashbook)s' % {
                'name': gettext('cashbook.msg_name_cashbook'),
                'cashbook': getattr(book, 'rec_name', '-/-'),
                },
            }
        return action

# OLineMixin


class OpenCashBookStart(ModelView):
    'Open Cashbook'
    __name__ = 'cashbook.open_lines.start'

    cashbook = fields.Many2One(
        string='Cashbook', model_name='cashbook.book',
        required=True, domain=[('btype', '!=', None)])
    checked = fields.Boolean(
        string='Checked', help="Show cashbook lines in Checked-state.")
    done = fields.Boolean(
        string='Done', help="Show cashbook lines in Done-state")
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')

    @classmethod
    def default_checked(cls):
        return True

    @classmethod
    def default_done(cls):
        return False

# end OpenCashBookStart


class OpenCashBook(OLineMixin, Wizard):
    'Open Cashbook'
    __name__ = 'cashbook.open_lines'

    start_state = 'check'
    check = StateTransition()
    askuser = StateView(
        'cashbook.open_lines.start',
        'cashbook.open_lines_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Open', 'open_', 'tryton-ok', default=True),
            ])
    open_ = StateAction('cashbook.act_line_view2')

    def transition_check(self):
        """ dont ask and open cashbook if user has 1x only
        """
        Book = Pool().get('cashbook.book')

        with Transaction().set_context({
                '_check_access': True}):
            books = Book.search([('btype', '!=', None)])
            if len(books) == 1:
                return 'open_'
        return 'askuser'

    def default_askuser(self, fields):
        """ setup form
        """
        Configuration = Pool().get('cashbook.configuration')

        cfg1 = Configuration.get_singleton()
        result = {
            'date_from': getattr(cfg1, 'date_from', None),
            'date_to': getattr(cfg1, 'date_to', None),
            'checked': getattr(cfg1, 'checked', True),
            'done': getattr(cfg1, 'done', False),
            }
        return result

    def do_open_(self, action):
        """ open view, use data from dialog
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Configuration = pool.get('cashbook.configuration')

        cfg1 = Configuration.get_singleton()
        if cfg1 is None:
            cfg1 = Configuration()
            cfg1.save()

        book = getattr(self.askuser, 'cashbook', None)
        if book is None:
            with Transaction().set_context({
                    '_check_access': True}):
                books = Book.search([('btype', '!=', None)])
                if len(books) > 0:
                    book = books[0]

        # save settings
        cfg1.date_from = getattr(self.askuser, 'date_from', None)
        cfg1.date_to = getattr(self.askuser, 'date_to', None)
        cfg1.checked = getattr(self.askuser, 'checked', True)
        cfg1.done = getattr(self.askuser, 'done', False)
        cfg1.save()
        action.update(self.add_action_data(book))
        return action, {}

    def transition_open_(self):
        return 'end'

# end OpenCashBook


class OpenCashBookTree(OLineMixin, Wizard):
    'Open Cashbook2'
    __name__ = 'cashbook.open_lines_tree'

    start_state = 'open_'
    open_ = StateAction('cashbook.act_line_view2')

    def do_open_(self, action):
        """ open view from doubleclick
        """
        pool = Pool()
        Book = pool.get('cashbook.book')
        Configuration = pool.get('cashbook.configuration')

        cfg1 = Configuration.get_singleton()
        if cfg1 is None:
            cfg1 = Configuration()
            cfg1.save()

        book = self.record
        if book is None:
            with Transaction().set_context({
                    '_check_access': True}):
                books = Book.search([('btype', '!=', None)])
                if len(books) > 0:
                    book = books[0]
        else:
            if book.btype is None:
                raise UserError(gettext(
                    'cashbook.msg_book_no_type_noopen',
                    bookname=book.rec_name))

        action.update(self.add_action_data(book))
        return action, {}

# end OpenCashBookTree
