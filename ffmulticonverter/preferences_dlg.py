#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2013 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from PyQt4.QtCore import QSettings
from PyQt4.QtGui import (QDialog, QDialogButtonBox, QFileDialog, QGridLayout,
                         QHBoxLayout, QLabel, QLineEdit, QRadioButton,
                         QSpacerItem, QTabWidget, QToolButton, QVBoxLayout,
                         QWidget)

import os
import pyqttools


class Preferences(QDialog):
    def __init__(self, parent=None, test = False):
        super(Preferences, self).__init__(parent)
        self.parent = parent
        self.home = os.getenv('HOME')

        saveLabel = QLabel('<html><b>' + self.tr('Save files') + '</b></html>')
        exist_Label = QLabel(self.tr('Existing files:'))
        self.exst_add_prefixRadioButton = QRadioButton(
                                                     self.tr("Add '~' prefix"))
        self.exst_overwriteRadioButton = QRadioButton(self.tr('Overwrite'))
        exist_layout = pyqttools.add_to_layout(QHBoxLayout(),
                                               self.exst_add_prefixRadioButton,
                                               self.exst_overwriteRadioButton)

        defaultLabel = QLabel(self.tr('Default output destination:'))
        self.defaultLineEdit = QLineEdit()
        self.defaultToolButton = QToolButton()
        self.defaultToolButton.setText('...')
        deafult_fol_layout = pyqttools.add_to_layout(QHBoxLayout(),
                                                     self.defaultLineEdit,
                                                     self.defaultToolButton)
        name_Label = QLabel('<html><b>' + self.tr('Name files') +'</b></html>')
        prefixLabel = QLabel(self.tr('Prefix:'))
        suffixLabel = QLabel(self.tr('Suffix:'))
        self.prefixLineEdit = QLineEdit()
        self.suffixLineEdit = QLineEdit()
        grid = pyqttools.add_to_grid(QGridLayout(),
                                     [prefixLabel, self.prefixLineEdit],
                                     [suffixLabel, self.suffixLineEdit])
        prefix_layout = pyqttools.add_to_layout(QHBoxLayout(), grid, None)

        tabwidget1_layout = pyqttools.add_to_layout(QVBoxLayout(), saveLabel,
               QSpacerItem(14, 13), exist_Label, exist_layout,
               QSpacerItem(14, 13), defaultLabel, deafult_fol_layout,
               QSpacerItem(13, 13), name_Label, QSpacerItem(14, 13),
               prefix_layout)

        ffmpegLabel = QLabel('<html><b>' + self.tr('FFmpeg') +'</b></html>')
        default_commandLabel = QLabel(self.tr('Default command:'))
        self.commandLineEdit = QLineEdit()
        useLabel = QLabel(self.tr('Use:'))
        self.ffmpegRadioButton = QRadioButton(self.tr('FFmpeg'))
        self.avconvRadioButton = QRadioButton(self.tr('avconv'))

        hlayout = pyqttools.add_to_layout(QHBoxLayout(),
                                          self.ffmpegRadioButton,
                                          self.avconvRadioButton)

        tabwidget2_layout = pyqttools.add_to_layout(QVBoxLayout(), ffmpegLabel,
                QSpacerItem(14, 13), useLabel, hlayout, QSpacerItem(14, 13),
                default_commandLabel, self.commandLineEdit, None)

        widget1 = QWidget()
        widget1.setLayout(tabwidget1_layout)
        widget2 = QWidget()
        widget2.setLayout(tabwidget2_layout)
        self.TabWidget = QTabWidget()
        self.TabWidget.addTab(widget1, self.tr('General'))
        self.TabWidget.addTab(widget2, self.tr('Audio/Video'))

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                          QDialogButtonBox.Cancel)

        final_layout = pyqttools.add_to_layout(QVBoxLayout(), self.TabWidget,
                                               None, self.buttonBox)
        self.setLayout(final_layout)

        self.defaultToolButton.clicked.connect(self.open_dir)
        self.buttonBox.accepted.connect(self.save_settings)
        self.buttonBox.rejected.connect(self.reject)

        settings = QSettings()
        overwrite_existing = settings.value('overwrite_existing').toBool()
        default_output = settings.value('default_output').toString()
        prefix = settings.value('prefix').toString()
        suffix = settings.value('suffix').toString()
        avconv_prefered = settings.value('avconv_prefered').toBool()
        default_command = settings.value('default_command').toString()

        if overwrite_existing:
            self.exst_overwriteRadioButton.setChecked(True)
        else:
            self.exst_add_prefixRadioButton.setChecked(True)
        if default_output:
            self.defaultLineEdit.setText(default_output)
        if prefix:
            self.prefixLineEdit.setText(prefix)
        if suffix:
            self.suffixLineEdit.setText(suffix)
        if avconv_prefered:
            self.avconvRadioButton.setChecked(True)
        else:
            self.ffmpegRadioButton.setChecked(True)
        if default_command:
            self.commandLineEdit.setText(default_command)
        else:
            self.commandLineEdit.setText('-ab 320k -ar 48000 -ac 2')

        if not test and not self.parent.ffmpeg:
            self.avconvRadioButton.setChecked(True)
            self.ffmpegRadioButton.setEnabled(False)
        if not test and not self.parent.avconv:
            self.ffmpegRadioButton.setChecked(True)
            self.avconvRadioButton.setEnabled(False)

        self.resize(400, 390)
        self.setWindowTitle(self.tr('Preferences'))

    def open_dir(self):
        """Get a directory name using a standard Qt dialog and update
        self.defaultLineEdit with dir's name."""
        if self.defaultLineEdit.isEnabled():
            _dir = QFileDialog.getExistingDirectory(self, 'FF Multi Converter '
                '- ' + self.tr('Choose default output destination'), self.home)
            #_dir = unicode(_dir)
            if _dir:
                self.defaultLineEdit.setText(_dir)

    def save_settings(self):
        """Set settings values, extracting the appropriate information from
        the graphical widgets."""
        overwrite_existing = self.exst_overwriteRadioButton.isChecked()
        default_output = unicode(self.defaultLineEdit.text())
        prefix = unicode(self.prefixLineEdit.text())
        suffix = unicode(self.suffixLineEdit.text())
        avconv_prefered = self.avconvRadioButton.isChecked()
        default_command = unicode(self.commandLineEdit.text())

        settings = QSettings()
        settings.setValue('overwrite_existing', overwrite_existing)
        settings.setValue('default_output', default_output)
        settings.setValue('prefix', prefix)
        settings.setValue('suffix', suffix)
        settings.setValue('avconv_prefered', avconv_prefered)
        settings.setValue('default_command', default_command)

        self.accept()


if __name__ == '__main__':
    #test dialog
    from PyQt4.QtGui import QApplication
    import sys
    app = QApplication(sys.argv)
    dialog = Preferences(test=True)
    dialog.show()
    app.exec_()
