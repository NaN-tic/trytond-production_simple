from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Bool, Eval


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'
    boms_editor = fields.One2Many('production.bom', 'template', 'BOMs Editor',
        states={
            'invisible': ~Bool(Eval('producible')),
            })

    @classmethod
    def copy(cls, templates, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('boms_editor', None)
        return super().copy(templates, default=default)


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'

    boms_editor = fields.One2Many('production.bom', 'product', 'BOMs Editor',
        states={
            'invisible': ~Bool(Eval('producible')),
            })

    @classmethod
    def copy(cls, products, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('boms_editor', None)
        return super().copy(products, default=default)
