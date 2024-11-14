import unittest
from proteus import Model
from trytond.tests.test_tryton import drop_db
from trytond.modules.mobisl.tests.tools import setup
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
        vars = setup()
        activate_modules('production_simple')

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
        template.default_uom = vars.unit
        template.producible = True
        template.save()
        product_out, = template.products

        # Create product
        template = Template()
        template.name = 'Input'
        template.type = 'goods'
        template.default_uom = vars.unit
        template.save()
        product_in, = template.products

        # Create BOM
        bom = BOM()
        bom.outputs.new(product=product_out, quantity=1)
        bom.inputs.new(product=product_in, quantity=1)
        bom.save()

        self.assertEqual(bom.rec_name, '[1] Output')
        self.assertEqual(bom.name, '-')

