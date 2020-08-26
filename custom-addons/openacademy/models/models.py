# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import timedelta

# class openacademy(models.Model):
#     _name = 'openacademy.openacademy'
#     _description = 'openacademy.openacademy'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

class Course(models.Model):
    _name = 'openacademy.course'
    _description = "OpenAcademy Courses"
    name = fields.Char(string='Title', required = True)
    start_date = fields.Date(default=fields.Date.today)
    description = fields.Text()
    responsible_id = fields.Many2one('res.users',
    ondelete='set null', string="Responsible", index=True)
    session_ids = fields.One2many(
        'openacademy.session', 'course_id', string="Sessions"
    )
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the course should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The course title must be unique"),
    ]
    
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', f"Copy of {self.name}")])
        if not copied_count:
            default['name']= f"Copy of {self.name}"
        else:
            default['name'] = f"Copy of {self.name} ({copied_count})"

        return super(Course, self).copy(default)

    

class Session(models.Model):
    _name = 'openacademy.session'
    _description = "OpenAcademy Sessions"
    
    name = fields.Char(required=True)
    start_date = fields.Date()
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    end_date = fields.Date(string="End of course", compute = '_get_end_date', store = True,
        inverse = '_set_end_date')
    seats = fields.Integer(string="Number of seats")
    percentage = fields.Float(string="Percentage of taken seats", compute = '_compute_percentage')

    instructor_id = fields.Many2one('res.partner', string="Instructor",
        domain = [('instructor', '=', True)])
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    attendees_count = fields.Integer(string="Number of attendees", compute='_get_number_attendees')
    course_id = fields.Many2one('openacademy.course',
        ondelete='cascade', string='Course', required=True)
    color = fields.Integer()
    
    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning' : {
                    'title' : 'Wrong number of seats',
                    'message' : 'Number of seats should be more than zero'
                }
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning' : {
                    'title' : 'Too many people',
                    'message' : 'Number of seats should be more or equal to the number of attendees'
                }
            }

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


    def _compute_percentage(self):
        for record in self:
            if record.seats:
                record.percentage = len(record.attendee_ids)/record.seats
            else:
                record.percentage = 0.0
    
    def _get_number_attendees(self):
        for record in self:
            record.attendees_count = len(record.attendee_ids)
    
    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for record in self:
            if record.instructor_id and record.instructor_id in record.attendee_ids:
                raise exceptions.ValidationError('Instructor can\'t be attendee for the same course')
    