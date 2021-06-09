# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    hold_delivery_till_payment = fields.Boolean()
