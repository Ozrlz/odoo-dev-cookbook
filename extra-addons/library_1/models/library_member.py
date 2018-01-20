# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LibraryMember(models.Model):
    """
    This class is an abstraction of a person who interacts with a library.

    fields:
        partner_id (many2one) --> res.partner: A relation to the model.
    """

    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        ondelete="cascade",
    )
    date_start = fields.Date(string="Member since", )
    date_end = fields.Date(string="Termination date", )
    member_number = fields.Char(string="Member number", )
