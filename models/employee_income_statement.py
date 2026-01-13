from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class EmployeeIncomeStatement(models.Model):
    _name = 'employee.income.statement'
    _description = 'Employee Income Statement'

    _inherit = ['mail.thread']

    name = fields.Char(string='Year for')
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    employee_tag_ids = fields.Many2many(
            'hr.employee.category',
            'employee_income_statement_employee_category_rel',
            'employee_id',
            'category_id',
            related='employee_id.category_ids',
            string='Employee Tags',
            store=True,
            depends=['employee_id', 'employee_id.category_ids']
        )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('check', 'Checked')
    ], string='State', default='draft', track_visibility="onchange")

    isy_amount = fields.Float(string='ISY Amount', track_visibility="onchange")
    gty_amount = fields.Float(string='GTY Amount', track_visibility="onchange")
    tax_amount = fields.Float(string='Tax Amount', track_visibility="onchange")
    gross_amount = fields.Float(
        string='Gross Amount',
        compute='_compute_gross_amount', track_visibility="onchange")
    net_amount = fields.Float(
        string='Net Amount',
        compute='_compute_net_amount', track_visibility="onchange")

    @api.depends('isy_amount', 'gty_amount')
    def _compute_gross_amount(self):
        for rec in self:
            rec.gross_amount = rec.isy_amount + rec.gty_amount

    @api.depends('gross_amount', 'tax_amount')
    def _compute_net_amount(self):
        for rec in self:
            rec.net_amount = rec.gross_amount - rec.tax_amount

    def btn_check(self):
        self.state = 'check'

    def btn_draft(self):
        self.state = 'draft'
