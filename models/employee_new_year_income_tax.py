from odoo import models, fields, api, _
from datetime import date, datetime

class EmployeeNewYearIncomeTax(models.Model):
    _name = 'employee.new.year.income.tax'
    _description = 'Employee New Year Income Tax'

    _inherit = ['mail.thread']

    name = fields.Char(string='Number', default="New")
    increase_percentage = fields.Float(string='Increase Percentage', required=True, track_visibility="onchange")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    employee_tag_ids = fields.Many2many(
            'hr.employee.category',
            'employee_new_year_income_tax_employee_category_rel',
            'employee_id',
            'category_id',
            related='employee_id.category_ids',
            string='Employee Tags',
            store=True,
            depends=['employee_id', 'employee_id.category_ids']
        )
    school_year_date_from = fields.Date(string='School Year Date From', required=True, track_visibility="onchange")
    school_year_date_to = fields.Date(string='School Year Date To', required=True, track_visibility="onchange")
    school_year_monthly_gross_amount = fields.Float(string='School Year Monthly Gross Amount', required=True, track_visibility="onchange")
    school_year_yearly_gross_amount = fields.Float(
            string='School Year Yearly Gross Amount',
            compute='_compute_school_year_yearly_amount', 
            track_visibility="onchange")
    school_year_monthly_net_amount = fields.Float(string='School Year Monthly Net Amount', required=True, track_visibility="onchange")
    school_year_yearly_net_amount = fields.Float(
            string='School Year Yearly Average Tax Amount',
            compute='_compute_school_year_yearly_amount', 
            track_visibility="onchange")

    financial_year_date_from = fields.Date(string='Finical Year Date From', required=True, track_visibility="onchange")
    financial_year_date_to = fields.Date(string='Finical Year Date To', required=True, track_visibility="onchange")
    financial_year_monthly_average_tax_amount = fields.Float(string='Financial Year Monthly Average Tax Amount', required=True, track_visibility="onchange")
    financial_year_yearly_average_tax_amount = fields.Float(
        string='Financial Year Yearly Average Tax Amount',
        compute='_compute_financial_year_yearly_tax_amount',
        track_visibility="onchange")
    tax_difference_amount = fields.Float(string='Tax Difference Amount', track_visibility="onchange")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('check', 'Checked')
    ], string='State', default='draft', track_visibility="onchange")


    #Count calendar months inclusive of the start and end date
    def get_months(self, date_from, date_to):
        if not date_from or not date_to:
            return 0
        return (date_to.year - date_from.year) * 12 + (date_to.month - date_from.month) + 1

    @api.depends('school_year_monthly_gross_amount', 'school_year_monthly_net_amount')
    def _compute_school_year_yearly_amount(self):
        for rec in self:
            tl_month = rec.get_months(rec.school_year_date_from, rec.school_year_date_to)
            rec.school_year_yearly_gross_amount = rec.school_year_monthly_gross_amount * tl_month
            rec.school_year_yearly_net_amount = rec.school_year_monthly_net_amount * tl_month

    @api.depends('financial_year_monthly_average_tax_amount')
    def _compute_financial_year_yearly_tax_amount(self):
        for rec in self:
            tl_month = rec.get_months(rec.financial_year_date_from, rec.financial_year_date_to)
            rec.financial_year_yearly_average_tax_amount = rec.financial_year_monthly_average_tax_amount * tl_month

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New' or not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('employee.new.year.income.tax')
        return super(EmployeeNewYearIncomeTax, self).create(vals)

    def btn_check(self):
        self.state = 'check'

    def btn_draft(self):
        self.state = 'draft'
