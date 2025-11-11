# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.model import (
    MultiValueMixin, ValueMixin, fields, Unique, Index)
from trytond.transaction import Transaction
from trytond.pool import Pool
from sql import With
from sql.functions import Function
from .const import DEF_NONE


class ArrayAgg(Function):
    """input values, including nulls, concatenated into an array.
    """
    __slots__ = ()
    _function = 'ARRAY_AGG'

# end ArrayAgg


class ArrayAppend(Function):
    """ sql: array_append
    """
    __slots__ = ()
    _function = 'ARRAY_APPEND'

# end ArrayApppend


class ArrayToString(Function):
    """ sql: array_to_string
    """
    __slots__ = ()
    _function = 'ARRAY_TO_STRING'

# end ArrayToString


class AnyInArray(Function):
    """ sql: array_to_string
    """
    __slots__ = ()
    _function = 'ANY'

    def __str__(self):
        return self._function + '(' + ', '.join(
            map(self._format, self.args)) + '::int[])'

# end AnyInArray


class Array(Function):
    """ sql: array-type
    """
    __slots__ = ()
    _function = 'ARRAY'

    def __str__(self):
        return self._function + '[' + ', '.join(
            map(self._format, self.args)) + ']'

# end Array


def sub_ids_hierarchical(model_name):
    """ get table with id and sub-ids
    """
    Model2 = Pool().get(model_name)
    tab_mod = Model2.__table__()
    tab_mod2 = Model2.__table__()

    lines = With('parent', 'id', recursive=True)
    lines.query = tab_mod.select(
            tab_mod.id, tab_mod.id,
        ) | tab_mod2.join(
            lines,
            condition=lines.id == tab_mod2.parent,
        ).select(lines.parent, tab_mod2.id)
    lines.query.all_ = True

    query = lines.select(
            lines.parent,
            ArrayAgg(lines.id).as_('subids'),
            group_by=[lines.parent],
            with_=[lines])
    return query


def order_name_hierarchical(model_name, tables):
    """ order by pos
        a recursive sorting
    """
    Model2 = Pool().get(model_name)
    tab_mod = Model2.__table__()
    tab_mod2 = Model2.__table__()
    table, _ = tables[None]

    lines = With('id', 'name', 'name_path', recursive=True)
    lines.query = tab_mod.select(
            tab_mod.id, tab_mod.name, Array(tab_mod.name),
            where=tab_mod.parent == DEF_NONE,
        )
    lines.query |= tab_mod2.join(
            lines,
            condition=lines.id == tab_mod2.parent,
        ).select(
            tab_mod2.id,
            tab_mod2.name,
            ArrayAppend(lines.name_path, tab_mod2.name),
        )
    lines.query.all_ = True

    query = lines.select(
            ArrayToString(lines.name_path, '/').as_('rec_name'),
            where=table.id == lines.id,
            with_=[lines])
    return [query]


class UserValueMixin(ValueMixin):
    iduser = fields.Many2One(
        model_name='res.user', string="User",
        ondelete='CASCADE', required=True)

    @classmethod
    def __setup__(cls):
        super(UserValueMixin, cls).__setup__()
        tab_val = cls.__table__()
        cls._sql_indexes.update({
            Index(
                tab_val,
                (tab_val.iduser, Index.Equality())),
            })
        cls._sql_constraints.extend([
            ('val_uniq',
                Unique(tab_val, tab_val.iduser),
                'cashbook.msg_setting_already_exists'),
            ])

# end UserValueMixin


class UserMultiValueMixin(MultiValueMixin):

    def updt_multivalue_pattern(self, pattern):
        """ add values to pattern
        """
        pattern.setdefault('iduser', Transaction().user)
        return pattern

    def get_multivalue(self, name, **pattern):
        Value = self.multivalue_model(name)
        if issubclass(Value, UserValueMixin):
            pattern = self.updt_multivalue_pattern(pattern)
        return super(UserMultiValueMixin, self).get_multivalue(name, **pattern)

    def set_multivalue(self, name, value, **pattern):
        Value = self.multivalue_model(name)
        if issubclass(Value, UserValueMixin):
            pattern = self.updt_multivalue_pattern(pattern)
        return super(
            UserMultiValueMixin, self).set_multivalue(name, value, **pattern)

# end UserMultiValueMixin
