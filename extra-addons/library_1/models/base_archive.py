# -*- coding: utf-8 -*-

from odoo import models, fields

class BaseArchive(models.AbstractModel):
    """ This model is an abstract model that brings the
    archive capabilities
    """
    _name = 'base.archive'
    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active
