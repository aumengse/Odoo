from odoo import api, fields, models

class CountryState(models.Model):
    _description = "Country state"
    _inherit = 'res.country.state'

    city_ids = fields.One2many('res.state.city', 'state_id', string="City/Municipality")
    country_code = fields.Char(related='country_id.code', store=True)

class StateCity(models.Model):
    _name ='res.state.city'
    _description = 'State City'
    _inherit = ['mail.thread']
    _mail_post_access = 'read'

    name = fields.Char(string="City/Municipality")
    display_name = fields.Char(related='name', readonly=True)
    city_code = fields.Char(string="City/Municipality Code")
    active = fields.Boolean(string="Active", default=True)
    state_id = fields.Many2one('res.country.state', string="Province")
    brgy_ids = fields.One2many('res.city.barangay', 'city_id', string="Barangays")

    @api.model
    def create(self, vals):
        if vals['name']:
            vals['name'] = vals['name'].title()

        return super(StateCity, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            if vals['name']:
               vals['name'] = vals['name'].title()
        return super(StateCity, self).write(vals)

class CityBarangay(models.Model):
    _name = 'res.city.barangay'
    _description = 'City Barangay'
    _inherit = ['mail.thread']
    _mail_post_access = 'read'

    name = fields.Char(string="Barangay")
    display_name = fields.Char(related='name', readonly=True)
    brgy_code = fields.Char(string="Barangay Code")
    active = fields.Boolean(string="Active", default=True)
    city_id = fields.Many2one('res.state.city', string="City/Municipality")
    state_id = fields.Many2one('res.country.state', string="State/Province", related='city_id.state_id', store=True)

    @api.model
    def create(self, vals):
        if vals['name']:
            vals['name'] = vals['name'].title()
        return super(CityBarangay, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            if vals['name']:
                vals['name'] = vals['name'].title()
        return super(CityBarangay, self).write(vals)