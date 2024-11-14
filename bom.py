from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval


class BOMOutput(metaclass=PoolMeta):
    __name__ = 'production.bom.output'

    @staticmethod
    def default_quantity():
        return 1

    @classmethod
    def __setup__(cls):
        super().__setup__()
        domain = [('producible', '=', True)]
        if cls.product.domain:
            cls.product.domain.append(domain)
        else:
            cls.product.domain = domain

    @classmethod
    def write(cls, *args):
        pool = Pool()
        ProductBOM = pool.get('product.product-production.bom')

        actions = iter(args)
        boms = set()
        for outputs, values in zip(actions, actions):
            if 'product' in values:
                for output in outputs:
                    boms.add(output.bom)
        to_delete = ProductBOM.search([
                ('bom', 'in', boms),
                ])
        ProductBOM.delete(to_delete)
        super().write(*args)

    @classmethod
    def delete(cls, outputs):
        pool = Pool()
        ProductBOM = pool.get('product.product-production.bom')

        boms = set()
        for output in outputs:
            boms.add(output.bom)
        to_delete = ProductBOM.search([
                ('bom', 'in', boms),
                ])
        ProductBOM.delete(to_delete)
        super().delete(outputs)


class BOM(metaclass=PoolMeta):
    __name__ = 'production.bom'

    product = fields.Function(fields.Many2One('product.product', 'Product',
        states={
            'readonly': Eval('product_readonly', True),
            }), 'get_product', setter='set_product', searcher='search_product')
    template = fields.Function(fields.Many2One('product.template', 'Template'),
        'get_template', setter='set_template', searcher='search_template')
    product_readonly = fields.Function(fields.Boolean('Product Readonly'),
        'get_product_readonly')

    def get_rec_name(self, name):
        return ', '.join([x.product.rec_name for x in self.outputs])

    @classmethod
    def search_rec_name(cls, name, clause):
        return ['OR',
            ('outputs.product.rec_name',) + tuple(clause[1:]),
            ]

    def get_product(self, name):
        if len(self.outputs) != 1:
            return
        return self.outputs[0].product.id

    @classmethod
    def set_product(cls, boms, name, value):
        pool = Pool()
        BOMOutput = pool.get('production.bom.output')
        Product = pool.get('product.product')

        to_save = []
        to_delete = []
        for bom in boms:
            if not value:
                if bom.outputs:
                    to_delete += bom.outputs
                continue
            if bom.outputs:
                output = bom.outputs[0]
                output.product = value
            else:
                product = Product(value)
                output = BOMOutput(bom=bom, product=product, quantity=1,
                   unit=product.default_uom)
            to_save.append(output)

        BOMOutput.save(to_save)
        BOMOutput.delete(to_delete)

    @classmethod
    def search_product(cls, name, clause):
        return [('outputs.product.id',) + tuple(clause[1:])]

    def get_template(self, name):
        if len(self.outputs) != 1:
            return
        return self.outputs[0].product.template.id

    @classmethod
    def set_template(cls, boms, name, value):
        pool = Pool()
        BOMOutput = pool.get('production.bom.output')
        Template = pool.get('product.template')

        to_save = []
        to_delete = []
        for bom in boms:
            if not value:
                if bom.outputs:
                    to_delete += bom.outputs
                continue
            template = Template(value)
            if len(template.products) != 1:
                to_delete += bom.outputs
                continue
            product, = template.products
            if bom.outputs:
                output = bom.outputs[0]
                output.product = product
            else:
                output = BOMOutput(bom=bom, product=product, quantity=1,
                   unit=product.default_uom)
            to_save.append(output)
        BOMOutput.save(to_save)
        BOMOutput.delete(to_delete)

    @classmethod
    def search_template(cls, name, clause):
        return [('outputs.product.template.id',) + tuple(clause[1:])]

    def get_product_readonly(self, name):
        return len(self.outputs) > 1

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.name.translate = False
        cls.name.readonly = True

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            values.setdefault('name', '-')
        boms = super().create(vlist)
        cls.update_products(boms)
        return boms

    @classmethod
    def write(cls, *args):
        super().write(*args)
        cls.update_products(sum(args[::2], []))

    def _product_boms(self):
        pool = Pool()
        ProductBOM = pool.get('product.product-production.bom')

        res = []
        for output in self.outputs:
            res.append(ProductBOM(
                    product=output.product,
                    bom=self,
                    ))
        return res

    @classmethod
    def _product_bom_key(cls, product_bom):
        return (product_bom.product.id, product_bom.bom.id,)

    @classmethod
    def update_products(cls, boms):
        pool = Pool()
        ProductBOM = pool.get('product.product-production.bom')

        existing_keys = set()
        existing = ProductBOM.search([
                ('bom', 'in', boms),
                ])
        to_delete = []
        for pb in existing:
            key = cls._product_bom_key(pb)
            existing_keys.add(cls._product_bom_key(pb))

        # Find missing records
        all_keys = set()
        to_save = []
        for bom in boms:
            for pb in bom._product_boms():
                pb_key = cls._product_bom_key(pb)
                all_keys.add(pb_key)
                if not pb_key in existing_keys:
                    to_save.append(pb)

        # Remove unnecessary records
        for pb in existing:
            key = cls._product_bom_key(pb)
            if not key in all_keys:
                to_delete.append(pb)

        ProductBOM.save(to_save)
        ProductBOM.delete(to_delete)
        return to_save
