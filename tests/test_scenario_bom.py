import unittest
from proteus import Model
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules
from trytond.modules.company.tests.tools import create_company


class Test(unittest.TestCase):
    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test_unit(self):
        # Load model and prepare generic data
        activate_modules(['production_simple', 'production_routing'])

        _ = create_company()

        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])

        Template = Model.get('product.template')
        BOM = Model.get('production.bom')

        # Create product
        template = Template()
        template.code = '1'
        template.name = 'Output'
        template.type = 'goods'
        template.default_uom = unit
        template.producible = True
        template.save()
        product_out, = template.products

        # Create product
        template = Template()
        template.name = 'Input'
        template.type = 'goods'
        template.default_uom = unit
        template.save()
        product_in, = template.products

        # Create BOM
        mbom = BOM()
        mbom.outputs.new(product=product_out, quantity=1)
        mbom.inputs.new(product=product_in, quantity=1)
        mbom.save()

        self.assertEqual(mbom.rec_name, '[1] Output')
        self.assertEqual(mbom.name, '-')

        # Create operations
        Operation = Model.get('production.routing.operation')
        operation = Operation(name='Setup')
        operation.save()

        # Create product
        template = Template()
        template.code = '2'
        template.name = 'Output 2'
        template.default_uom = unit
        template.producible = True
        template.save()
        bom = template.boms_editor.new()
        bom.inputs.new(product=product_in, quantity=10)

        routing = bom.routings_editor.new()
        step = routing.steps.new()
        step.operation = operation

        template.save()

        bom, = BOM.find([('id', '!=', mbom.id)])
        self.assertEqual(bom.rec_name, '[2] Output 2')
        routing, = bom.routings
        self.assertEqual(routing.rec_name, '[2] Output 2')
