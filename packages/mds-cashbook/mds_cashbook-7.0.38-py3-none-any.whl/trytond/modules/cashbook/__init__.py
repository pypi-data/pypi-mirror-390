# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.pool import Pool
from .book import Book
from .types import Type
from .line import Line, LineContext
from .splitline import SplitLine
from .wizard_openline import OpenCashBook, OpenCashBookStart, OpenCashBookTree
from .wizard_runreport import RunCbReport, RunCbReportStart
from .wizard_booking import EnterBookingWizard, EnterBookingStart
from .configuration import Configuration, UserConfiguration
from .category import Category
from .reconciliation import Reconciliation
from .cbreport import ReconciliationReport
from .currency import CurrencyRate
from .valuestore import ValueStore
from .ir import Rule
from .cron import Cron


def register():
    Pool.register(
        Configuration,
        UserConfiguration,
        CurrencyRate,
        Type,
        Category,
        Book,
        LineContext,
        Line,
        SplitLine,
        Reconciliation,
        OpenCashBookStart,
        RunCbReportStart,
        EnterBookingStart,
        ValueStore,
        Rule,
        Cron,
        module='cashbook', type_='model')
    Pool.register(
        ReconciliationReport,
        module='cashbook', type_='report')
    Pool.register(
        OpenCashBook,
        OpenCashBookTree,
        RunCbReport,
        EnterBookingWizard,
        module='cashbook', type_='wizard')
