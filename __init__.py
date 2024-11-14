# This file is part production_simple module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import bom
from . import product
from . import routing

def register():
    Pool.register(
        bom.BOM,
        bom.BOMOutput,
        product.Template,
        product.Product,
        module='production_simple', type_='model')
    Pool.register(
        routing.BOM,
        routing.Routing,
        depends=['production_routing'],
        module='production_simple', type_='model')
