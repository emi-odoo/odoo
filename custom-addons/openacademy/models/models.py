# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


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
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)

    

class Session(models.Model):
    _name = 'openacademy.session'
    _description = "OpenAcademy Sessions"

    name = fields.Char(required=True)
    start_date = fields.Date()
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    percentage = fields.Float(string="Percentage of taken seats", compute = '_compute_percentage')

    instructor_id = fields.Many2one('res.partner', string="Instructor",
        domain = [('instructor', '=', True)])
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    course_id = fields.Many2one('openacademy.course',
        ondelete='cascade', string='Course', required=True)
    
    @api.onchange('seats', 'attendee_ids'):
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

    def _compute_percentage(self):
        for record in self:
            if record.seats:
                record.percentage = len(record.attendee_ids)/record.seats
            else:
                record.percentage = 0.0
    
    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise exceptions.ValidationError("A session's instructor can't be an attendee")
    