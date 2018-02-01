# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError

STATE_SELECTION = [
    ('ongoing', 'Ongoing'),
    ('done', 'Done')´,
]

class LibraryBookLoan(models.Model):
    _name = 'library.book.loan'

    book_id = fields.Many2one('library.book', 'Book', required=True)
    member_id = fields.Many2one('library.member', 'Borrower', required=True)
    state = fields.Selection(selection=STATE_SELECTION, string='State', 
        default='ongoing', required=True)