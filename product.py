from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Bool, Eval


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'
    boms_editor = fields.One2Many('production.bom', 'template', 'BOMs Editor',
        states={
            'invisible': ~Bool(Eval('producible')),
            })


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'

    boms_editor = fields.One2Many('production.bom', 'product', 'BOMs Editor',
        states={
            'invisible': ~Bool(Eval('producible')),
            })
