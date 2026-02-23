from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class StockByAssginedPerson(models.Model):
    _name = 'stock.by.assigned.person'
    _description = 'Stock By Assigned Person'
    _auto = False #Important to set this to False to avoid auto creation of the record #Very Important for SQL View

    assigned_to = fields.Many2one('res.partner', readonly=True)
    name = fields.Char(string='Name', compute='_compute_name')
    manager_id = fields.Many2one('hr.employee', readonly=True)
    line_ids = fields.One2many(
        'isy.stock.report',
        compute='_compute_lines',
        string='Products'
    )

    def _compute_name(self):
        for rec in self:
            rec.name = rec.assigned_to.name

    def _compute_lines(self):
        for rec in self:
            rec.line_ids = self.env['isy.stock.report'].search([
                ('assigned_to', '=', rec.assigned_to.id)
            ])

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW stock_by_assigned_person AS (
                SELECT
                    MIN(rp.id) AS id,
                    rp.assigned_to,
                    emp.parent_id AS manager_id
                FROM isy_stock_report rp LEFT JOIN hr_employee emp ON rp.assigned_to = emp.address_id
                WHERE rp.assigned_to IS NOT NULL AND rp.assigned_type = 'employee'
                GROUP BY rp.assigned_to, emp.parent_id
            )
        """)

    def _get_customer_information(self):
       return {
        'name': self.assigned_to.name or '',
        'email': self.assigned_to.email or '',
       }
