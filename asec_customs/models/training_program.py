from odoo import models, fields, api, _

class TrainingProgram(models.Model):
    _name = 'training.program'
    _description = 'Training Programs'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    def _default_stage_id(self):
        default_stage = self.env['training.program.stage'].search([('name', '=', _('New'))], limit=1)
        if not default_stage:
            default_stage = self.env['training.program.stage'].create({
                'name': _("New"),
                'sequence': 0,
                'code': 'new',
            })
        return default_stage.id

    name = fields.Char(string="Name", compute='compute_name')
    reference = fields.Char(string="Reference")
    active = fields.Boolean(string="Active", default=True)
    stage_id = fields.Many2one('training.program.stage', string="State", default=_default_stage_id,
                               group_expand='_read_group_stage_ids', tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string="Partner")
    employee_id = fields.Many2one('hr.employee', string="Instructor")
    course_id = fields.Many2one('training.program.courses', string="Course")
    venue_id = fields.Many2one('training.program.venue', string="Venue")
    date_start = fields.Datetime(string="Training Start")
    date_end = fields.Datetime(string="Training End")
    user_id = fields.Many2one('res.users', 'User',default=lambda self: self.env.uid)
    color = fields.Integer(string="Color")
    employee_ids = fields.Many2many('hr.employee', string="Participants")
    material_ids = fields.One2many('training.program.material','program_id', string="Participants")
    document_ids = fields.One2many('training.program.document','program_id',string="Documents")
    document_count = fields.Integer(string="Document Count",  compute='compute_document_count')

    @api.depends('reference','course_id')
    def compute_name(self):
        for rec in self:
            rec.name = ""
            if rec.reference and rec.course_id:
                rec.name = "%s - %s" % (rec.reference,rec.course_id.name)

    @api.depends('document_ids')
    def compute_document_count(self):
        for rec in self:
            rec.document_count = 0
            if rec.document_ids:
                rec.document_count = len(rec.document_ids)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['training.program.stage'].search([])
        return stage_ids

    @api.model
    def create(self, vals):
        if 'reference' not in vals or vals['reference'] == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('training.program.sequence') or _('New')
        return super(TrainingProgram, self).create(vals)


    def action_create_invoice(self):
        x = 1