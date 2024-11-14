from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval


class BOM(metaclass=PoolMeta):
    __name__ = 'production.bom'
    routings = fields.Many2Many(
        'production.routing-production.bom', 'bom', 'routing', 'Routings')
    routings_editor = fields.One2Many('production.routing', 'bom', 'Routings Editor')

    def _product_boms(self):
        pool = Pool()
        ProductBOM = pool.get('product.product-production.bom')

        pbs = super()._product_boms()
        if not self.routings:
            return pbs
        to_add = []
        for pb in pbs:
            pb.routing = self.routings[0]
            for routing in self.routings[1:]:
                npb = ProductBOM()
                npb.product = pb.product
                npb.bom = pb.bom
                npb.routing = routing
                to_add.append(npb)
        return pbs + to_add

    @classmethod
    def _product_bom_key(cls, product_bom):
        routing = getattr(product_bom, 'routing', None)
        return super()._product_bom_key(product_bom) + (routing and routing.id,)


class Routing(metaclass=PoolMeta):
    __name__ = 'production.routing'
    bom = fields.Function(fields.Many2One('production.bom', 'BOM',
        states={
            'readonly': Eval('bom_readonly', True),
            }), 'get_bom', setter='set_bom', searcher='search_bom')
    bom_readonly = fields.Function(fields.Boolean('BOM Readonly'),
        'get_bom_readonly')

    def get_rec_name(self, name):
        if self.boms:
            return ', '.join([x.rec_name for x in self.boms])
        if self.steps:
            return ', '.join([x.rec_name for x in self.steps])
        return '-'

    @classmethod
    def search_rec_name(cls, name, clause):
        return ['OR',
            ('name',) + tuple(clause[1:]),
            ('boms.rec_name',) + tuple(clause[1:]),
            ]

    def get_bom(self, name):
        if len(self.boms) != 1:
            return
        return self.boms[0].id

    @classmethod
    def set_bom(cls, routings, name, value):
        for routing in routings:
            if value:
                routing.boms = (value,)
            else:
                routing.boms = ()
        cls.save(routings)

    @classmethod
    def search_bom(cls, name, clause):
        return [('boms.id',) + tuple(clause[1:])]

    def get_bom_readonly(self, name):
        return len(self.boms) > 1

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
        routings = super().create(vlist)
        cls.update_products(routings)
        return routings

    @classmethod
    def write(cls, *args):
        super().write(*args)
        cls.update_products(sum(args[::2], []))

    @classmethod
    def update_products(cls, routings):
        pool = Pool()
        BOM = pool.get('production.bom')
        ProductBOM = pool.get('product.product-production.bom')

        existing = ProductBOM.search([
                ('routing', 'in', routings),
                ])
        to_save = []
        for pb in existing:
            products = [x.product for bom in pb.routing.boms for x in
                bom.outputs]
            if pb.product not in products:
                pb.routing = None
                to_save.append(pb)
        ProductBOM.save(to_save)


        boms = sum([list(x.boms) for x in routings], [])
        BOM.update_products(boms)
