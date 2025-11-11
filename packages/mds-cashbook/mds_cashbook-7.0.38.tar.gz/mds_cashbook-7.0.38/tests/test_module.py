# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.


from trytond.tests.test_tryton import ModuleTestCase

from .type import TypeTestCase
from .book import BookTestCase
from .line import LineTestCase
from .splitline import SplitLineTestCase
from .config import ConfigTestCase
from .category import CategoryTestCase
from .reconciliation import ReconTestCase
from .bookingwiz import BookingWizardTestCase
from .valuestore import ValuestoreTestCase


class CashbookTestCase(
        ValuestoreTestCase,
        BookingWizardTestCase,
        ReconTestCase,
        CategoryTestCase,
        ConfigTestCase,
        LineTestCase,
        SplitLineTestCase,
        BookTestCase,
        TypeTestCase,
        ModuleTestCase):
    'Test cashbook module'
    module = 'cashbook'

# end CashbookTestCase


del ModuleTestCase
