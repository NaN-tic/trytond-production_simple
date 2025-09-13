import functools
from trytond.tools import grouped_slice
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval
from trytond.model.exceptions import AccessError
from trytond.i18n import gettext
from trytond.transaction import Transaction


def check_no_input_output(func):

    def find_inputs_outputs(cls, records):
        pool = Pool()
        BOMInput = pool.get('production.bom.input')
        BOMOutput = pool.get('production.bom.output')

        if cls.__name__ == 'product.template':
            field = 'product.template'
        else:
            field = 'product'
        for sub_records in grouped_slice(records):
            ids = list(map(int, sub_records))
            inputs = BOMInput.search([
                    (field, 'in', ids),
                    ],
                limit=1, order=[])
            outputs = BOMOutput.search([
                    (field, 'in', ids),
                    ],
                limit=1, order=[])
            if inputs or outputs:
                return True
        return False

    @functools.wraps(func)
    def decorator(cls, *args):
        pool = Pool()
        Template = pool.get('product.template')
        transaction = Transaction()
        if transaction.user and transaction.check_access:
            actions = iter(args)
            field = 'default_uom'
            msg = 'production_simple.msg_product_change_default_uom'
            for records, values in zip(actions, actions):
                if field in values:
                    if find_inputs_outputs(cls, records):
                        raise AccessError(gettext(msg))
                    # No inputs/outputs for those records
                    break

                if not values.get('template'):
                    continue
                template = Template(values['template'])
                for record in records:
                    if isinstance(
                            getattr(Template, field), fields.Function):
                        continue
                    if getattr(record, field) != getattr(template, field):
                        if find_inputs_outputs(cls, [record]):
                            raise AccessError(gettext(msg))
                        # No inputs/outputs for this record
                        break
        func(cls, *args)
    return decorator


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'
    boms_editor = fields.One2Many('production.bom', 'template', 'BOMs Editor',
        states={
            'invisible': ~Bool(Eval('producible')),
            })

    @classmethod
    @check_no_input_output
    def write(cls, *args):
        super().write(*args)

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
    @check_no_input_output
    def write(cls, *args):
        super().write(*args)

    @classmethod
    def copy(cls, products, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('boms_editor', None)
        return super().copy(products, default=default)
