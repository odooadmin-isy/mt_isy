from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class EmployeeIncomeStatementWizard(models.TransientModel):
    _name = 'employee.income.statement.wizard'
    _description = 'Employee Income Statement Wizard'

    name = fields.Char(string='Year for')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    tag_ids = fields.Many2many(
            'hr.employee.category',  # model of the tags
            string='Employee Tags', required=True
        )

    @api.onchange('name')
    def onchange_name(self):
        if self.name and self.name.isdigit() and len(self.name) == 4:
            self.date_from = date(int(self.name), 1, 1)
            self.date_to = date(int(self.name), 12, 31)
        else:
            self.date_from = False
            self.date_to = False

    def generate_income_statement(self):
        _logger.info(
            "========================= Starting Employee Income Statement ===================")
        obj_employee_income_statement = self.env['employee.income.statement']
        obj_employee_income_statement = obj_employee_income_statement.search([
                                                ('date_from', '=', self.date_from),
                                                ('date_to', '=', self.date_to),
                                                ('employee_tag_ids', 'in', self.tag_ids.ids)])
        if obj_employee_income_statement:
            raise ValidationError(_("Employee Income Statement already exists for this year!"))

        category_condition = f"AND rel.category_id IN ({','.join(map(str, self.tag_ids.ids))})" if len(self.tag_ids.ids) > 0 else False

        query = f"""
                SELECT
                    slip.employee_id,
                    SUM(CASE WHEN categ.code ILIKE '%basic%' AND cmpy.short_name = 'ISYA' THEN line.amount ELSE 0 END) AS isy_amount,
                    SUM(CASE WHEN categ.code ILIKE '%basic%' AND cmpy.short_name = 'GTY' THEN line.amount ELSE 0 END) AS gty_amount,
                    SUM(CASE WHEN categ.code ILIKE '%DED%' THEN line.amount ELSE 0 END) AS tax_amount
                FROM hr_payslip_line line
                JOIN hr_payslip slip ON slip.id = line.slip_id
                JOIN hr_salary_rule_category categ ON categ.id = line.category_id
                JOIN res_company cmpy ON cmpy.id = slip.company_id
                JOIN employee_category_rel rel ON rel.emp_id = slip.employee_id
                WHERE categ.code ILIKE ANY (ARRAY['%basic%', '%DED%'])
                AND slip.date_from BETWEEN '{self.date_from}' AND '{self.date_to}' {category_condition}
                AND slip.state IN ('draft', 'done', 'paid')
                GROUP BY slip.employee_id;
        """
        _logger.info(f"Query: {query}")
        self.env.cr.execute(query)

        rows = self.env.cr.fetchall()
        for row in rows:
            obj_employee_income_statement.create({
                'name': self.name,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'employee_id': row[0],
                'isy_amount': row[1],
                'gty_amount': row[2],
                'tax_amount': row[3],
            })

        return True
