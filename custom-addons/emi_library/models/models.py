# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import timedelta

# class emi_library(models.Model):
#     _name = 'emi_library.emi_library'
#     _description = 'emi_library.emi_library'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

class Book(models.Model):
    _name = 'emi_library.book'
    name = fields.Char(string="Book Title", required = True)
    authors = fields.Many2many('emi_library.author' )
    isbn = fields.Char(size=13, default = '0'*10)
    edition_year = fields.Integer(string='Edition year')
    loans = fields.One2many('emi_library.book_loan', 'book')

    available = fields.Boolean(default = True)

    @api.constrains('isbn')
    def _check_valid_isbn(self):
        for record in self:
            print(record.isbn)
            if len(record.isbn) not in (10, 13):
                raise exceptions.ValidationError('ISBN code should be 10 or 13 digits')
            else:
                if len(record.isbn) == 10:
                    acc = 0
                    for index, value in enumerate(record.isbn):
                        acc += (index + 1)*int(value)
                    if acc % 11 != 0:
                        raise exceptions.ValidationError('ISBN-10 code is not valid')
                else:
                    even_digits = [int(i) for i in record.isbn[1::2]]
                    odd_digits = [int(i) for i in record.isbn[::2]]
                    if (3*sum(even_digits) + sum(odd_digits))%10 != 0:
                        raise exceptions.ValidationError('ISBN-13 code is not valid')
    
    #_sql_constraints = [ ('name_year_unique','UNIQUE(name, edition_year)','The email must be unique') ]
                
class Author(models.Model):
    _name = 'emi_library.author'
    name = fields.Char(string='Author name')
    books_written = fields.Many2many('emi_library.book', readonly=True)

class Member(models.Model):
    # NO this kind of INHERITANCE!
    #_inherit = 'res.partner'
    # we use delegation inheritance
    _name = 'emi_library.member'
    card_number = fields.Char(size=10, string = "Library Card Number")
    book_loans = fields.One2many('emi_library.book_loan', 'member', readonly=True)
    partner_id = fields.Many2one('res.partner', delegate=True,
        ondelete='cascade',
        required=True)

class BookLoan(models.Model):
    _name = 'emi_library.book_loan'
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Integer(string="Borrow Lenght", default = 30)
    end_date = fields.Date(compute='_get_end_date',
        inverse = '_set_end_date', store = True)
    
    book = fields.Many2one('emi_library.book')
    member = fields.Many2one('emi_library.member')
    @api.depends('duration', 'start_date')
    def _get_end_date(self):
        for record in self:
            if record.duration:
                t_days = max(record.duration - 1, 0)
                t_delta = timedelta(days= t_days)
                self.end_date = self.start_date + t_delta

            else:
                self.end_date = self.start_date

    def _set_end_date(self):
        for record in self:
            if record.start_date and record.end_date:
                record.duration = (record.end_date - record.start_date).days +1
