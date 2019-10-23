from datetime import date, timedelta
import logging

from odoo import api, fields, models, _

logger = logging.getLogger(__name__)


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


class WizardSalesandUtilities(models.TransientModel):
    _name = 'wizard_sales_and_utilities'

    start_date = fields.Date(
        default=lambda self: date(fields.Date.today().year, fields.Date.today().month, 1),
        required=True,
    )
    end_date = fields.Date(
        default=last_day_of_month(fields.Date.today()),
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string=_('Product')
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string=_('Partner')
    )
    salesman_id = fields.Many2one(
        comodel_name='res.users',
        string=_('Salesman')
    )
    warehouse_id = fields.Many2one(
        comodel_name='',  # TODO
        string=_('Warehouse')
    )
    provider_id = fields.Many2one(
        comodel_name='',  # TODO
        string=_('Provider')
    )
    row_ids = fields.One2many(
        comodel_name='wizard_sales_and_utilities.row',
        inverse_name='wizard_id',
        readonly=True,
    )
    qty_total = fields.Float(
        compute='_get_totals',
    )
    cost_unit_total = fields.Float(
        compute='_get_totals',
    )
    price_unit_total = fields.Float(
        compute='_get_totals',
    )
    cost_total_total = fields.Float(
        compute='_get_totals',
    )
    price_total_total = fields.Float(
        compute='_get_totals',
    )
    utility_total = fields.Float(
        compute='_get_totals',
    )
    utility_percentage_total = fields.Float(
        compute='_get_totals',
    )
    margin_total = fields.Float(
        compute='_get_totals',
    )

    @api.multi
    def get_rows(self):
        self.row_ids.unlink()
        AccountInvoice = self.env['account.invoice']
        # TODO filter
        invoices_filter = [
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date),
        ]
        if self.partner_id:
            invoices_filter.append(
                ('partner_id', '=', self.partner_id.id)
            )
        if self.salesman_id:
            invoices_filter.append(
                ('user_id', '=', self.salesman_id.id)
            )
        if self.warehouse_id:
            invoices_filter.append(
                ('warehouse_id', '=', self.warehouse_id.id)  # TODO
            )
        if self.provider_id:
            invoices_filter.append(
                ('provider_id', '=', self.provider_id.id)  # TODO
            )
        groups = {}
        for invoice in AccountInvoice.search(invoices_filter):
            # TODO Filter
            for line in invoice.invoice_line_ids:
                if not line.product_id:
                    continue
                if self.product_id and self.product_id != line.product_id:
                    continue
                cost_unit = line.product_id.get_history_price(invoice.company_id.id, invoice.date or invoice.date_invoice)
                product_id = line.product_id.id
                group = (product_id, line.name, cost_unit, line.price_unit)
                if not groups.get(group):
                    groups[group] = 0
                groups[group] += line.quantity
        WizardSalesandUtilitiesRow = self.env['wizard_sales_and_utilities.row']
        for group, qty in groups.items():
            WizardSalesandUtilitiesRow.create({
                'wizard_id': self.id,
                'product_id': group[0],
                'qty': qty,
                'product_description': group[1],
                'cost_unit': group[2],
                'price_unit': group[3],
            })
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.onchange('row_ids')
    def _get_totals(self):
        for record in self:
            record.qty_total = sum(row.qty for row in record.row_ids)
            record.cost_total_total = sum(row.cost_total for row in record.row_ids)
            record.price_total_total = sum(row.price_total for row in record.row_ids)
            record.utility_total = record.price_total_total - record.cost_total_total
            record.utility_percentage_total = record.cost_total_total and 100 * record.utility_total / record.cost_total_total
            record.margin_total = record.price_total_total and 100 * record.utility_total / record.price_total_total
