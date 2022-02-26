from odoo import models, fields, api, _

class TrainingProgramCourses(models.Model):
    _name = 'training.program.material'
    _description = 'Training Materials'

    name = fields.Many2one(related='product_id')
    product_id = fields.Many2one('product.product', string="Product")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id',)
    program_id = fields.Many2one('training.program', 'Training Program')
    quantity = fields.Float(string="Quantity")
    price = fields.Float(related='product_id.list_price', readonly=False, string="Price")
    subtotal = fields.Monetary(string="Subtotal", currency_field='company_currency', compute='compute_subtotal')
    program_id = fields.Many2one('training.program', 'Training Program')

    @api.depends('quantity','price')
    def compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.price * rec.quantity