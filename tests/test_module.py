# This file is part production_simple module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.transaction import Transaction
from trytond.model.exceptions import AccessError


class ProductionSimplifiedTestCase(ModuleTestCase):
    'Test Production Simplified module'
    module = 'production_simple'
    extras = ['production_routing']

    @with_transaction()
    def test_product_change_uom(self):
        'Test products_by_location with_childs and stock_skip_warehouse'
        pool = Pool()
        User = pool.get('res.user')

        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Product = pool.get('product.product')
        BOM = pool.get('production.bom')
        BOMInput = pool.get('production.bom.input')
        BOMOutput = pool.get('production.bom.output')

        user, = User.create([{
                    'name': 'Test User',
                    'login': 'test',
                    }])
        user_id = user.id

        unit, = Uom.search([('name', '=', 'Unit')])
        hour, = Uom.search([('name', '=', 'Hour')])

        template1, template2 = Template.create([{
                    'name': 'Test1',
                    'type': 'goods',
                    'producible': True,
                    'default_uom': unit.id,
                    }, {
                    'name': 'Test2',
                    'type': 'goods',
                    'producible': True,
                    'default_uom': unit.id,
                    }])
        product1, product2 = Product.create([{
                    'template': template1.id,
                    }, {
                    'template': template2.id,
                    }])

        bom, = BOM.create([{
                    'name': 'BOM Test',
                    }])
        BOMInput.create([{
            'bom': bom.id,
            'product': product1.id,
            'quantity': Decimal(1),
            'unit': unit,
            }])
        BOMOutput.create([{
            'bom': bom.id,
            'product': product2.id,
            'quantity': Decimal(1),
            'unit': unit,
            }])
        
        with Transaction().set_user(user_id), \
            Transaction().set_context(_check_access=True), \
            self.assertRaises(AccessError):
                Template.write([template1], {'default_uom': hour.id})
                Template.write([template2], {'default_uom': hour.id})


del ModuleTestCase
