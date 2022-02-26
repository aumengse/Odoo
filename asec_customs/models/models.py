# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class /opt/test/asec_customs(models.Model):
#     _name = '/opt/test/asec_customs./opt/test/asec_customs'
#     _description = '/opt/test/asec_customs./opt/test/asec_customs'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
