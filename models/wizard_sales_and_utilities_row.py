from odoo import api, fields, models, _


class WizardSalesandUtilitiesRow(models.TransientModel):
    _name = 'wizard_sales_and_utilities.row'

    wizard_id = fields.Many2one(
        comodel_name='wizard_sales_and_utilities',
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True,
    )
    product_description = fields.Text(
        required=True,
    )
    qty = fields.Float(
        required=True,
    )
    cost_unit = fields.Float(
        required=True,
    )
    price_unit = fields.Float(
        required=True,
    )
    cost_total = fields.Float(
        compute='_get_cost_total',
    )
    price_total = fields.Float(
        compute='_get_price_total',
    )
    utility = fields.Float(
        compute='_get_utility',
    )
    utility_percentage = fields.Float(
        compute='_get_utility_percentage',
    )
    margin = fields.Float(
        compute='_get_margin'
    )

    @api.onchange('cost_unit', 'qty')
    def _get_cost_total(self):
        for record in self:
            record.cost_total = record.cost_unit * record.qty

    @api.onchange('price_unit', 'qty')
    def _get_price_total(self):
        for record in self:
            record.price_total = record.price_unit * record.qty

    @api.onchange('cost_total', 'price_total')
    def _get_utility(self):
        for record in self:
            record.utility = record.price_total - record.cost_total

    @api.onchange('cost_total', 'utility')
    def _get_utility_percentage(self):
        for record in self:
            record.utility_percentage = record.cost_total and 100 * record.utility / record.cost_total

    @api.onchange('price_total', 'utility')
    def _get_margin(self):
        for record in self:
            record.margin = record.price_total and 100 * record.utility / record.price_total
