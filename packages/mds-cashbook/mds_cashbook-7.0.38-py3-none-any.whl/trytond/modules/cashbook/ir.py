# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.pool import PoolMeta


class Rule(metaclass=PoolMeta):
    __name__ = 'ir.rule'

    @classmethod
    def _context_modelnames(cls):
        """ list of models to add 'user_id' to context
        """
        result = super(Rule, cls)._context_modelnames()
        return result | {
            'cashbook.book',
            'cashbook.line',
            'cashbook.recon',
            'cashbook.split'
        }

# end Rule
