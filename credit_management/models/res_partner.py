# -*- coding: utf-8 -*-
# Copyright 2020 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_overdue_by_x_days = fields.Boolean(
        string="Has Overdue Invoices",
        compute='_check_overdue_invoices',
        help='Has overdue invoices by x no of days'
    )
    override_credit_threshold_limit = fields.Integer(
        string="Override credit Threshold",
        help='Below a specified amount, orders will automatically override the credit limit',
    )
    hold_delivery_till_payment = fields.Boolean(default=False, copy=False, help="If True, then holds the DO until  \
                                    invoices are paid and equals to the total amount on the SO")

    def _check_overdue_invoices(self):
        x_no_of_overdue_days = int(self.env['ir.config_parameter'].sudo().get_param('credit_management.x_no_of_overdue_days',default=0))
        for partner in self:
            for invoice in partner.invoice_ids.filtered(lambda i: i.state == 'posted' and i.move_type == 'out_invoice' and i.payment_state not in ['in_payment', 'paid'] and i.invoice_date_due and i.invoice_date_due < fields.Date.today()):
                date_due = fields.Date.from_string(invoice.invoice_date_due)
                today = fields.Date.from_string(fields.Date.today())
                delta = date_due - today
                if abs(delta.days) > x_no_of_overdue_days:
                    partner.has_overdue_by_x_days = True
                    break
            else:
                partner.has_overdue_by_x_days = False

    def _get_total_credit_used(self):
        self.update({
            'total_credit_used': 0.0,
        })
        for partner in self.mapped('commercial_partner_id'):
            if not isinstance(partner.id, models.NewId):
                if not partner.active:
                    continue
                child_ids = tuple(self.search([('id', 'child_of', partner.id)]).ids)

                not_invoiced_order_lines_query = """
                select sum(price_total) from sale_order_line
                where
                order_partner_id in %s and
                state in %s and
                invoice_status != %s
                """
                self._cr.execute(not_invoiced_order_lines_query, (child_ids, ('sale','done'), 'invoiced'))
                amount_not_invoiced_order_lines = self._cr.dictfetchone()['sum'] or 0.0

                invoiced_downpayment_lines_query = """
                select sum(price_total) from sale_order_line
                where
                order_partner_id in %s and
                state in %s and
                is_downpayment = %s and
                qty_invoiced != %s
                """
                self._cr.execute(invoiced_downpayment_lines_query, (child_ids, ('sale', 'done'), 'true', 0))
                amount_invoiced_downpayment_lines = self._cr.dictfetchone()['sum'] or 0.0

                confirmed_so_not_invoiced = amount_not_invoiced_order_lines - amount_invoiced_downpayment_lines

                draft_invoice_query = """
                select distinct(am.id), am.amount_total from account_move_line aml, sale_order_line_invoice_rel sol_rel, account_move am
                where aml.partner_id in %s and
                sol_rel.invoice_line_id = aml.id and
                am.id = aml.move_id and
                am.state = %s and
                am.move_type != %s and
                am.move_type != %s
                """
                self._cr.execute(draft_invoice_query, (child_ids, 'draft', 'entry', 'out_refund'))
                draft_invoices = self._cr.fetchall()
                draft_invoices_amount = 0.0
                for draft_invoice in draft_invoices:
                    draft_invoices_amount += draft_invoice[1]

                partner.total_credit_used = partner.credit + confirmed_so_not_invoiced + draft_invoices_amount


    total_credit_used = fields.Monetary(
        compute='_get_total_credit_used',
        string='Total Credit Used',
        help='Total credit used by the partner')
    credit_hold = fields.Boolean(
        string='Credit Hold',
        help='True, if the credit is on hold',
        tracking=True,
        copy=False,
    )
