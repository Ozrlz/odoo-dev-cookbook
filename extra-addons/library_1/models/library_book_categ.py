# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class BookCategory(models.Model):
    _name = 'library.book.category'
    _rec_name = 'name' # optional
    _description = 'Category of books'
    _order = 'name desc' # optional
    # Enable hierarchy support
    _parent_store = True
    _parent_name = 'parent_id'
    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)

    name = fields.Char('Category')
    parent_id = fields.Many2one(
            comodel_name='library.book.category',
            string='Parent Categoy',
            ondelete='restrict',
            index=True,
        )
    child_ids = fields.One2many(
            comodel_name='library.book.category',
            inverse_name='parent_id',
            string='Child Categories',
        )

    # To prevent loop relations
    @api.multi
    @api.constrains("parent_id")
    def _check_hierarchy(self):
        for s in self:
            if not self._check_recursion():
                raise ValidationError(_("Error, you cannot create a recursive category"))
