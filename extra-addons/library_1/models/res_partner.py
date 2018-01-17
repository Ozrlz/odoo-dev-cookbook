# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _name = 'res.partner' # optional
    _inherit = 'res.partner'

    book_ids = fields.One2many(
            string="Published books",
            comodel_name="library.book",
            inverse_name="publisher_id",
        )
    authored_book_ids = fields.Many2many(
            comodel_name='library.book',
            string='Authored Books'
        )
    count_books = fields.Integer(
            string='Number of authored books',
            compute='_compute_count_books',
        )
    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for record in self:
            record.count_books = len(record.authored_book_ids)
