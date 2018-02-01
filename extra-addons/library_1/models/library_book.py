# -*- coding: utf-8 -*-

from datetime import timedelta as td
from odoo.fields import Date as fDate

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError, UserError

from pdb import set_trace as debug


STATE_SELECTION = [
    ('draft', 'Not available'),
    ('available', 'Available'),
    ('borrowed', 'Borrowed'),
    ('lost', 'Lost'),
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

    isbn = fields.Char('ISBN')
    manager_remarks = fields.Text('Manager Remarks')

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

    @api.model
    def _referencable_models(self):
        models = self.env['res.request.link'].search([])
        return [(x.object, x.name) for x in models]

    '''    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id,
                u"%s (%s)" % (record.short_name, record.date_released)
                )
            )
        return result    '''
    # Second version, name and author_ids.name
    @api.model
    def name_get(self):
        result = []
        for book in self:
            authors = book.author_ids.mapped('name')
            name = u'%s (%s)' % (book.name,
                                u', '.join(authors))
            result.append(
                (book.id, name)
            )
        return result

    # Search by name, name of authors or isbn
    @api.model
    def _name_search(self, name='', args=None, operator='ilike',
                    limit=100, name_get_uid=None):
        args = [] if args is None else list(args)
        if not(name == '' and operator == 'ilike'):
            args += [ '|', '|',
                ('name', operator, name),
                ('isbn', operator, name),
                ('author_ids.name', operator, name),
            ]
        return super(LibraryBook, self)._name_search(
            name='', args=args, operator='ilike', 
            limit=limit, name_get_uid=name_get_uid,
        )

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        """ Checks if the transition is valid
        Given the old and new states checks if the transition is valid

        Args:
            old_state: The state in which the book was before the transition.
            new_state: The state in which the book will be after the transition.

        Return:
            Returns a boolean indicating whether the transition is valid or not.
        """
        allowed = [
                ('draft', 'available'),
                ('available', 'borrowed'),
                ('borrowed', 'available'),
                ('available', 'lost'),
                ('borrowed', 'lost'),
                ('lost', 'available')
            ]
        return (old_state, new_state) in allowed

    @api.multi
    def change_state(self, new_state):
        """ Changes the state of the current book(s).
        Args:
            new_state: The state in which the book is going to be.
        """
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                continue

    @api.model
    def get_all_library_members(self):
        library_member_model = self.env['library.member']
        return library_member_model.search([])

    # Override create method, pag 118
    @api.model
    @api.returns('self', lambda rec: rec.id)
    def create(self, values):
        # debug()
        if not self.user_has_groups(
            'base.group_erp_manager'):
            if 'short_name' in values:
                raise UserError(
                    'You are not allowed to modify '
                    'short_name'
                )
        return super(LibraryBook, self).create(values)


    # Override write method, pag 118
    @api.multi
    def write(self, values):
        # debug()
        if not self.user_has_groups(
            'base.group_erp_manager'):
            if 'short_name' in values:
                raise UserError(
                    'You are not allowed to modify '
                    'short_name'
                )
        return super(LibraryBook, self).write(values)

    # Override fields_get method, pag 118-119
    @api.model
    def fields_get( self,
                    allfields=None,
                    attributes=None):
        # debug()
        fields = super (LibraryBook, self).fields_get(
            allfields=allfields,
            attributes=attributes,
        )
        if not self.user_has_groups(
            'base.group_erp_manager'):
            if 'short_name' in fields:
                fields['short_name']['readonly'] = True
                
        return fields