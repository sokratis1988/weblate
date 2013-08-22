# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2013 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <http://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
from django.utils.translation import ugettext as _
from weblate import appsettings
from PIL import Image, ImageDraw
from trans.fonts import is_cjk, get_font
from cStringIO import StringIO
import os.path


COLOR_DATA = {
    'grey': {
        'bar': 'rgb(0, 67, 118)',
        'border': 'rgb(0, 0, 0)',
        'text': 'rgb(0, 0, 0)',
    },
    'white': {
        'bar': 'rgb(0, 67, 118)',
        'border': 'rgb(0, 0, 0)',
        'text': 'rgb(0, 0, 0)',
    },
    'black': {
        'bar': 'rgb(0, 67, 118)',
        'border': 'rgb(255, 255, 255)',
        'text': 'rgb(255, 255, 255)',
    },
}

WIDGETS = {}


def register_widget(widget):
    '''
    Registers widget in dictionary.
    '''
    WIDGETS[widget.name] = widget


class Widget(object):
    '''
    Generic widget class.
    '''
    name = None
    colors = ('grey', 'white', 'black')
    progress = None

    def __init__(self, obj, color=None, lang=None):
        '''
        Creates Widget object.
        '''
        # Get object and related params
        self.obj = obj
        self.percent = obj.get_translated_percent(lang)
        self.total = obj.get_total()
        self.languages = obj.get_language_count()
        self.params = self.get_text_params()

        # Process parameters
        self.color = self.get_color_name(color)
        self.lang = lang

        # Set rendering variables
        self.image = None
        self.draw = None
        self.width = 0

    def get_color_name(self, color):
        '''
        Return color name based on allowed ones.
        '''
        if color not in self.colors:
            return self.colors[0]
        return color

    def get_line_width(self):
        '''
        Returns line width for current widget.
        '''
        if self.color == 'black':
            return 0.8
        return 0.2

    def get_text_params(self):
        '''
        Creates dictionary used for text formatting.
        '''
        return {
            'name': self.obj.name,
            'count': self.total,
            'languages': self.languages,
            'percent': self.percent,
        }

    def get_filename(self):
        '''
        Returns widgets filename.
        '''
        return os.path.join(
            settings.MEDIA_ROOT,
            'widgets',
            '%(widget)s-%(color)s.png' % {
                'color': self.color,
                'widget': self.name,
            }
        )

    def render(self):
        '''
        Renders widget.
        '''
        # PIL objects
        self.image = Image.open(self.get_filename()).convert('RGB')
        self.draw = ImageDraw.Draw(self.image)
        self.width = self.image.size[0]

        # Render progressbar
        if self.progress:
            self.render_progress()

        # Render texts
        self.render_texts()

    def render_progress(self):
        '''
        Renders progress bar.
        '''
        # Filled bar
        if self.progress['horizontal']:
            self.draw.rectangle(
                (
                    self.progress['x'],
                    self.progress['y'],
                    self.progress['x']
                    + self.progress['width'] / 100.0 * self.percent,
                    self.progress['y'] + self.progress['height']
                ),
                fill=COLOR_DATA[self.color]['bar'],
            )
        else:
            diff = self.progress['height'] / 100.0 * (100 - self.percent)
            self.draw.rectangle(
                (
                    self.progress['x'],
                    self.progress['y'] + diff,
                    self.progress['x'] + self.progress['width'],
                    self.progress['y'] + self.progress['height'] - diff
                ),
                fill=COLOR_DATA[self.color]['bar'],
            )

        # Progress border
        self.draw.rectangle(
            (
                self.progress['x'],
                self.progress['y'],
                self.progress['x'] + self.progress['width'],
                self.progress['y'] + self.progress['height']
            ),
            outline=COLOR_DATA[self.color]['border']
        )

    def render_text(self, text, lang_text, base_font_size, pos_x, pos_y):
        # Use language variant if desired
        if self.lang is not None and lang_text is not None:
            text = lang_text
            if 'English' in text:
                text = text.replace('English', self.lang.name)

        # Format text
        text = text % self.params
        cjk = is_cjk(text)
        print cjk, text
        offset = 0


        for line in text.splitlines():

            # Iterate until text fits into widget
            for font_size in range(base_font_size, 3, -1):
                font = get_font(font_size, cjk=cjk)
                layout_size = font.getsize(line)
                layout_width = layout_size[0]
                if layout_width + pos_x < self.width:
                    break

            # Render text
            self.draw.text(
                (pos_x, pos_y + offset),
                line,
                font=font,
                fill=COLOR_DATA[self.color]['text']
            )

            offset += layout_size[1]

    def render_texts(self):
        '''
        Text rendering method to be overridden.
        '''
        raise NotImplementedError()

    def get_image(self):
        '''
        Returns PNG data.
        '''
        out = StringIO()
        self.image.save(out, 'PNG')
        return out.getvalue()


class NormalWidget(Widget):
    name = '287x66'
    progress = {
        'x': 72,
        'y': 52,
        'height': 6,
        'width': 180,
        'horizontal': True,
    }

    def render_texts(self):
        self.render_text(
            '%(name)s',
            None,
            13,
            72, 6
        )
        self.render_text(
            _(
                'translating %(count)d strings into %(languages)d languages\n'
                '%(percent)d%% complete, help us improve!'
            ),
            # Translators: please use your language name instead of English
            _('translating %(count)d strings into English\n%(percent)d%%'
              ' complete, help us improve!'),
            11,
            72, 22
        )

register_widget(NormalWidget)


class SmallWidget(Widget):
    name = '88x31'

    def render_texts(self):
        self.render_text(
            '%(name)s',
            None,
            9,
            23, 2
        )
        self.render_text(
            _('translation\n%(percent)d%% done'),
            # Translators: please use your language name instead of English
            _('English translation\n%(percent)d%% done'),
            9,
            23, 11
        )

register_widget(SmallWidget)
