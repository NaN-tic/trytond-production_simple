# This file is part production_simple module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase


class ProductionSimplifiedTestCase(ModuleTestCase):
    'Test Production Simplified module'
    module = 'production_simple'
    extras = ['production_routing']

del ModuleTestCase
