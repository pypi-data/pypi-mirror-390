# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.


from sql.functions import CurrentTimestamp, DateTrunc
from sql.aggregate import Count
from sql.conditionals import Coalesce
from trytond.model import ModelSQL, fields, Unique
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.pyson import Eval, PYSON, PYSONEncoder, PYSONDecoder
from trytond.model.modelstorage import EvalEnvironment
from trytond.report import Report


class ValueStore(ModelSQL):
    'Value Store'
    __name__ = 'cashbook.values'

    cashbook = fields.Many2One(
        string='Cashbook', required=True, model_name='cashbook.book',
        ondelete='CASCADE')
    field_name = fields.Char(string='Field Name', required=True, select=True)
    numvalue = fields.Numeric(
        string='Value', digits=(16, Eval('valuedigits', 6)),
        depends=['valuedigits'])
    valuedigits = fields.Function(fields.Integer(
        string='Digits', readonly=True),
        'on_change_with_valuedigits')

    @classmethod
    def __register__(cls, module_name):
        super(ValueStore, cls).__register__(module_name)

        # clear value-store, re-calc
        records = cls.search([])
        if records:
            cls.delete(records)
        cls.maintenance_values()

    @classmethod
    def __setup__(cls):
        super(ValueStore, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints.extend([
            ('uniqu_field',
                Unique(t, t.cashbook, t.field_name),
                'cashbook.msg_value_exists_in_store'),
            ])

    def get_rec_name(self, name):
        """ name, balance, state
        """
        return '|'.join([
            '[' + getattr(self.cashbook, 'rec_name', '-') + ']',
            self.field_name or '-',
            Report.format_number(
                self.numvalue,
                None,
                digits=self.valuedigits or 2)
            if self.numvalue is not None else '-',
            str(self.valuedigits) if self.valuedigits is not None else '-'])

    @fields.depends('cashbook', 'field_name')
    def on_change_with_valuedigits(self, name=None):
        """ get digits by field name
        """
        Cashbook = Pool().get('cashbook.book')

        if self.cashbook and self.field_name:
            fieldobj = Cashbook._fields.get(self.field_name, None)
            if fieldobj:
                digit = getattr(fieldobj, 'digits', (16, 6))[1]
                if isinstance(digit, PYSON):
                    # execute pyson on linked record
                    digit = PYSONDecoder(
                            EvalEnvironment(self.cashbook, Cashbook)
                        ).decode(PYSONEncoder().encode(digit))
                return digit
        return 6

    @classmethod
    def _maintenance_fields(cls):
        """ list of model and fieldnames,
            to daily update
        """
        return ['balance']

    @classmethod
    def maintenance_values(cls):
        """ update values by cron
        """
        pool = Pool()
        Cashbook = pool.get('cashbook.book')
        tab_val = cls.__table__()
        tab_book = Cashbook.__table__()
        cursor = Transaction().connection.cursor()
        context = Transaction().context

        # select records older than 'check_dt'
        check_dt = context.get('maintenance_date', None)
        if not check_dt:
            check_dt = DateTrunc('day', CurrentTimestamp())

        # select records to update
        query = tab_val.select(
                tab_val.id,
                where=tab_val.field_name.in_(cls._maintenance_fields()) &
                (DateTrunc('day', Coalesce(
                    tab_val.write_date,
                    tab_val.create_date,
                    '1990-01-01 00:00:00')) < check_dt))
        cursor.execute(*query)
        records = []
        for x in cursor.fetchall():
            cb = cls(x[0]).cashbook
            if cb not in records:
                records.append(cb)

        # add records with missing fields in value-store
        num_fields = len(Cashbook.valuestore_fields())
        query = tab_book.join(
                tab_val,
                condition=tab_book.id == tab_val.cashbook,
                type_='LEFT OUTER',
            ).select(
                tab_book.id,
                Count(tab_val.id).as_('num'),
                group_by=[tab_book.id],
                having=Count(tab_val.id) < num_fields)
        cursor.execute(*query)
        records.extend([Cashbook(x[0]) for x in cursor.fetchall()])

        if records:
            Cashbook.valuestore_update_records([x for x in records])

    @classmethod
    def get_book_by_line(cls, records):
        """ select books above current record to update
            records: cashbook.line
        """
        Book = Pool().get('cashbook.book')

        to_update = []
        if records:
            books = Book.search([
                ('parent', 'parent_of', [x.cashbook.id for x in records])
                ])
            to_update.extend([
                x for x in books
                if x not in to_update])
        return to_update

    @classmethod
    def get_book_by_books(cls, records):
        """ select books above current record to update
            records: cashbook.book
        """
        Book = Pool().get('cashbook.book')

        to_update = []
        if records:
            books = Book.search([
                ('parent', 'parent_of', [x.id for x in records])
                ])
            to_update.extend([
                x for x in books
                if x not in to_update])
        return to_update

    @classmethod
    def update_books(cls, books):
        """ get cashbooks to update, queue it
        """
        Book = Pool().get('cashbook.book')

        if books:
            Book.__queue__.valuestore_update_records(books)

    @classmethod
    def update_values(cls, data):
        """ data: {'fieldname': {id1: value, id2: value, ...}, ...}
        """
        to_write = []
        to_create = []

        for name in data.keys():
            for record_id in data[name].keys():
                # get existing record
                records = cls.search([
                    ('cashbook', '=', record_id),
                    ('field_name', '=', name)])

                if records:
                    for record in records:
                        to_write.extend([
                            [record],
                            {'numvalue': data[name][record_id]}])
                else:
                    to_create.append({
                        'cashbook': record_id,
                        'field_name': name,
                        'numvalue': data[name][record_id]})

        if to_create:
            cls.create(to_create)
        if to_write:
            cls.write(*to_write)

# end ValueStore
