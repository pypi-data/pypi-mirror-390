# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.pool import PoolMeta, Pool


class CurrencyRate(metaclass=PoolMeta):
    __name__ = 'currency.currency.rate'

    @classmethod
    def create(cls, vlist):
        """ update cache-value
        """
        pool = Pool()
        Cashbook = pool.get('cashbook.book')
        ValueStore = pool.get('cashbook.values')

        records = super(CurrencyRate, cls).create(vlist)

        ValueStore.update_books(
            ValueStore.get_book_by_books(
                Cashbook.search([
                    ('currency', 'in', [
                        x.currency.id for x in records])])))
        return records

    @classmethod
    def write(cls, *args):
        """ update cache-value
        """
        pool = Pool()
        Cashbook = pool.get('cashbook.book')
        ValueStore = pool.get('cashbook.values')

        actions = iter(args)
        all_rates = []
        for rates, values in zip(actions, actions):
            all_rates.extend(rates)

        super(CurrencyRate, cls).write(*args)

        ValueStore.update_books(
            ValueStore.get_book_by_books(
                Cashbook.search([
                    ('currency', 'in', [
                        x.currency.id for x in all_rates])])))

    @classmethod
    def delete(cls, records):
        """ set cache to None
        """
        pool = Pool()
        Cashbook = pool.get('cashbook.book')
        ValueStore = pool.get('cashbook.values')

        books = ValueStore.get_book_by_books(Cashbook.search([
            ('currency', 'in', [x.currency.id for x in records])]))
        super(CurrencyRate, cls).delete(records)
        ValueStore.update_books(books)

# end
