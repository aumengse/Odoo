from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    DAYS = [
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
        ('9','9'),
        ('10','10'),
        ('11', '11'),
        ('12', '12'),
        ('13', '13'),
        ('14', '14'),
        ('15', '15'),
        ('16', '16'),
        ('17', '17'),
        ('18', '18'),
        ('19', '19'),
        ('20', '20'),
        ('21', '21'),
        ('22', '22'),
        ('23', '23'),
        ('24', '24'),
        ('25', '25'),
        ('26', '26'),
        ('27', '27'),
        ('28', '28'),
        ('29', '29'),
        ('30', '30'),
        ('31', '31'),
            ]


    contribution_due_day = fields.Selection(DAYS, string="Contribution Due Day")
    contribution_late_fee = fields.Float(string="Contribution Late Fee")
    grace_period = fields.Selection(DAYS, string="Grace Period")