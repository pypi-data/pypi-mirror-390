# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.report import Report
from trytond.i18n import gettext
from trytond.pool import Pool
from trytond.transaction import Transaction
from slugify import slugify


class ReconciliationReport(Report):
    __name__ = 'cashbook.reprecon'

    @classmethod
    def get_context(cls, records, header, data):
        """ update context
        """
        Company = Pool().get('company.company')
        context2 = Transaction().context

        context = super(
            ReconciliationReport, cls).get_context(records, header, data)
        context['company'] = Company(context2['company'])
        return context

    @classmethod
    def execute(cls, ids, data):
        """ edit filename
        """
        pool = Pool()
        IrDate = pool.get('ir.date')

        if data['model'] == 'cashbook.book':
            ExpObj = pool.get(data['model'])(data['id'])
            rep_name = ExpObj.rec_name[:50]
        elif data['model'] == 'cashbook.line':
            line_obj = pool.get(data['model'])(data['id'])
            rep_name = line_obj.cashbook.rec_name[:50]
        elif data['model'] == 'cashbook.recon':
            recon_obj = pool.get(data['model'])(data['id'])
            rep_name = gettext(
                'cashbook.msg_rep_reconciliation_fname',
                recname=recon_obj.cashbook.rec_name[:50],
                date_from=recon_obj.date_from.isoformat(),
                date_to=recon_obj.date_to.isoformat())
        else:
            raise ValueError('invalid model')

        (ext1, cont1, dirprint, title) = super(
            ReconciliationReport, cls).execute(ids, data)

        return (
            ext1,
            cont1,
            dirprint,
            slugify('%(date)s-%(book)s-%(descr)s' % {
                'date': IrDate.today().isoformat().replace('-', ''),
                'book': gettext('cashbook.msg_name_cashbook'),
                'descr': rep_name,
                },
                max_length=100, word_boundary=True, save_order=True),
            )

# end ReconciliationReport
