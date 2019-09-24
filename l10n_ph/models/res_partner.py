from odoo import fields, models, api, tools

class ResPartner(models.Model):
    _inherit = 'res.partner'

    city_id = fields.Many2one('res.state.city',string="City",domain="[('state_id','=',state_id)]")
    barangay_id = fields.Many2one('res.city.barangay',string="Barangay",domain="[('city_id','=',city_id)]")
    country_code = fields.Char(related='country_id.code',string="Country Code")

    @api.onchange('city_id')
    def onchange_city_id(self):
        self.city = self.city_id.name

    @api.model
    def create(self, values):
        result = super(ResPartner, self).create(values)

        city = self.env['res.state.city'].browse(values['city_id'])
        result['city'] = city.name
        barangay = self.env['res.city.barangay'].browse(values['barangay_id'])
        result['street2'] = barangay.name

        return result

    @api.multi
    def write(self, values):
        if 'barangay_id' in values:
            barangay = self.env['res.city.barangay'].browse(values['barangay_id'])
            values['street2'] = barangay.name
        return super(ResPartner, self).write(values)