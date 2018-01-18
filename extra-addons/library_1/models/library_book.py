# -*- coding: utf-8 -*-

from datetime import timedelta as td
from odoo.fields import Date as fDate

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


STATE_SELECTION = [
    ('draft', 'Not available'),
    ('available', 'Available'),
    ('lost', 'Lost'),
]

COMPUTED_SELECTION = [
    {'draft': [1,2,3]},
    {'available': ['1','2','3']},
    {'lost': [11,22,33]}
]


class LibraryBook(models.Model):
    """
    This class represents an abstraction of a book.

    """
    _name = 'library.book'
    _inherit = [
            'base.archive',
        ]
    _description = 'Library Book'
    _order = 'date_released desc, name'
    _rec_name = 'short_name'
    short_name = fields.Char(string="Short title")


    name = fields.Char('Title', required=True)
    date_released = fields.Date('Release date')
    author_ids = fields.Many2many(
            comodel_name='res.partner',
            string='Authors'
        )

    notes = fields.Text('Internal notes')
    state = fields.Selection(
        selection=STATE_SELECTION,
        string='Field name',
    )
    other_selection = fields.Selection(
        selection=STATE_SELECTION,
        string='Another selection',
    )
    description = fields.Html(string="Description", )
    cover = fields.Binary(string="Book Cover", )
    out_of_print = fields.Boolean(string="Out of print?", )
    # date_released = fields.Date(string="Release date", )
    date_updated = fields.Datetime(string="Last Updated", )
    pages = fields.Integer(string="Total pages", )
    reader_rating = fields.Float("Reader average rating",
            # (14,4) # Precision (total, decimals)
            dp.get_precision('Book price'),
        )
    currency_id = fields.Many2many(
            comodel_name='res.currency',
            string='Currency',
        )
    retail_price = fields.Monetary(
            string="Retail price",
            currency_field='currency_id', # Optional, by default it searches for a currency_id field
        )
    publisher_id = fields.Many2one(
            comodel_name="res.partner",
            string="Publisher",
        )

    age_days = fields.Float(
            string="Days since release",
            compute='_compute_age',
            inverse='_inverse_age',
            search='_search_age',
            store=False,
            compute_sudo=False,
        )
    # Related field
    publisher_city = fields.Char(
            string='Publisher City',
            related='publisher_id.city',
        )

    ref_doc_id = fields.Reference(
            selection='_referencable_models',
            string='Reference document',
        )

    # SQL Constraints
    _sql_constraints = [
            ('name uniq',
            'UNIQUE (name)',
            'Book title must be unique. ')
        ]

    @api.multi
    @api.constrains("date_released")
    def _check_date_released(self):
        for s in self:
            if s.date_released > fields.Date.today():
                raise ValidationError(_("Release date must be in past"))

    @api.depends('date_released')
    def _compute_age(self):
        today = fields.Date.from_string(fields.Date.today() )
        for book in self.filtered('date_released'):
            delta = fields.Date.from_string(book.date_released - today)
            book.age_days = delta.days

    def _inverse_age(self):
        today = fields.Date.from_string(fields.Date.today())
        for book in self.filtered('date_released'):
            d = td(days=book.age_days) - today
            book.date_released = fDate.to_string(d)

    def _search_age(self, operator, value):
        today = fDate.from_string(fDate.today())
        value_days = td(days=value)
        value_date = fDate.to_string(today - value_days)
        return [('date_released', operator, value_date)]

    # computed_selection = fields.Selection(
    #     selection=_get_computed_selection,
    #     string='Computed selection'
    # )

    # def _get_computed_selection(self):
    #     return COMPUTED_SELECTION[self.other_selection]

    @api.model
    def _referencable_models(self):
        models = self.env['res.request.link'].search([])
        return [(x.object, x.name) for x in models]

    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id,
                u"%s (%s)" % (record.short_name, record.date_released)
                )
            )
        return result
