#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2012 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
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

from PyQt4.QtCore import QTimer
from PyQt4.QtGui import (QApplication, QDialog, QVBoxLayout, QGridLayout,
                  QSpacerItem, QLineEdit, QLabel, QPushButton, QListWidget,
                  QListWidgetItem, QDialogButtonBox, QMessageBox, QSizePolicy,
                  QFileDialog)

import os
import sys
import re
import xml.etree.ElementTree as etree

import pyqttools


class ValidationError(Exception): pass

class MyListItem(QListWidgetItem):
    def __init__(self, text, xml_element, parent=None):
        super(MyListItem, self).__init__(text, parent)
        self.xml_element = xml_element


class ShowPresets(QDialog):
    def __init__(self, parent=None):
        super(ShowPresets, self).__init__(parent)
        self.original_presets_file = '/usr/share/ffmulticonverter/presets.xml'
        self.config_folder = os.getenv('HOME') + '/.config/ffmulticonverter/'
        self.current_presets_file = self.config_folder + 'presets.xml'

        self.presListWidget = QListWidget()
        labelLabel = QLabel(self.tr('Preset label'))
        self.labelLineEdit = QLineEdit()
        self.labelLineEdit.setReadOnly(True)
        commandLabel = QLabel(self.tr('Preset command line parameters'))
        self.commandLineEdit = QLineEdit()
        self.commandLineEdit.setReadOnly(True)
        extLabel = QLabel(self.tr('Output file extension'))
        self.extLineEdit = QLineEdit()
        self.extLineEdit.setReadOnly(True)
        addButton = QPushButton(self.tr('Add'))
        self.deleteButton = QPushButton(self.tr('Delete'))
        self.delete_allButton = QPushButton(self.tr('Delete all'))
        self.editButton = QPushButton(self.tr('Edit'))
        okButton = QPushButton(self.tr('OK'))
        okButton.setDefault(True)

        grid = QGridLayout()
        grid.addWidget(self.delete_allButton, 0, 0, 1, 1)
        grid.addWidget(addButton, 0, 1, 1, 1)
        grid.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding,
                                              QSizePolicy.Minimum), 1, 2, 1, 1)
        grid.addWidget(self.deleteButton, 1, 0, 1, 1)
        grid.addWidget(self.editButton, 1, 1, 1, 1)
        grid.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding,
                                             QSizePolicy.Minimum),  0, 2, 1, 1)
        grid.addWidget(okButton, 1, 3, 1, 1)

        final_layout = pyqttools.add_to_layout(QVBoxLayout(), 
            self.presListWidget, labelLabel, self.labelLineEdit, commandLabel, 
            self.commandLineEdit, extLabel, self.extLineEdit, grid)

        self.setLayout(final_layout)

        okButton.clicked.connect(self.accept)
        self.presListWidget.currentRowChanged.connect(self.show_preset)
        addButton.clicked.connect(self.add_preset)
        self.deleteButton.clicked.connect(self.delete_preset)
        self.delete_allButton.clicked.connect(self.delete_all_presets)
        self.editButton.clicked.connect(self.edit_preset)

        self.resize(410, 410)
        self.setWindowTitle(self.tr('Edit Presets'))
        
        QTimer.singleShot(0, self.load_xml)
        QTimer.singleShot(0, self.fill_LineEdit)

    def load_xml(self):
        try:
            self.tree = etree.parse(self.current_presets_file)
        except IOError:
            self.tree = etree.parse(self.original_presets_file)
            if not os.path.exists(self.config_folder):
                os.makedirs(self.config_folder)
        self.root = self.tree.getroot()

    def set_buttons_clear_lineEdits(self):
        enable = bool(self.presListWidget)
        self.editButton.setEnabled(enable)
        self.deleteButton.setEnabled(enable)
        self.delete_allButton.setEnabled(enable)
        if not enable:
            self.labelLineEdit.clear()
            self.commandLineEdit.clear()
            self.extLineEdit.clear()

    def fill_LineEdit(self):
        self.presListWidget.clear()
        for i in sorted([y.tag for y in self.root]):
            elem = self.root.find(i)
            self.presListWidget.addItem(MyListItem(i, elem))
            self.presListWidget.setCurrentRow(0)
        self.set_buttons_clear_lineEdits()

    def show_preset(self):
        try:
            xml_elem = self.presListWidget.currentItem().xml_element
        except AttributeError:
            return

        self.labelLineEdit.setText(xml_elem[0].text)
        self.commandLineEdit.setText(xml_elem[1].text)
        self.commandLineEdit.home(False)
        self.extLineEdit.setText(xml_elem[2].text)

    def add_preset(self):
        dialog = AddorEditPreset(None, False)
        if dialog.exec_():
            element = etree.Element(dialog.name_text)
            label = etree.Element('label')
            label.text = dialog.label_text
            command = etree.Element('params')
            command.text = dialog.command_text
            ext = etree.Element('extension')
            ext.text = dialog.ext_text
            category = etree.Element('category')
            category.text = 'Scattered'

            for num, elem in enumerate([label, command, ext, category]):
                element.insert(num, elem)
            index = sorted(([i.tag for i in self.root] + [dialog.name_text]))\
                                                       .index(dialog.name_text)
            self.root.insert(index, element)
            self.save_tree()
            self.fill_LineEdit()

    def delete_preset(self):
        try:
            xml_elem = self.presListWidget.currentItem().xml_element
        except AttributeError:
            return

        reply = QMessageBox.question(self, 'FF Multi Converter - ' + self.tr(
            'Delete Preset'), 'Are you sure that you want to delete the {0} '
            'preset?'.format(xml_elem.tag), QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            self.root.remove(xml_elem)
            self.save_tree()
            self.fill_LineEdit()

    def delete_all_presets(self):
        reply = QMessageBox.question(self, 'FF Multi Converter - ' + self.tr(
            'Delete Preset'), 'Are you sure that you want to delete all '
            'presets?', QMessageBox.Yes|QMessageBox.Cancel)        
        if reply == QMessageBox.Yes:        
            self.root.clear()
            self.save_tree()
            self.fill_LineEdit()            

    def edit_preset(self):
        elem = self.presListWidget.currentItem().xml_element
        dialog = AddorEditPreset(elem, True)

        if dialog.exec_():
            elem.tag = dialog.name_text
            elem[0].text = dialog.label_text
            elem[1].text = dialog.command_text
            elem[2].text = dialog.ext_text
            self.save_tree()
            self.fill_LineEdit()

    def save_tree(self):
        with open(self.current_presets_file, 'w') as _file:
            try:
                etree.ElementTree(self.root).write(_file)
            except:
                pass
    
    def import_presets(self):
        title = 'FF Multi Converter - Import'
        reply = QMessageBox.question(self, title, 'All current presets will be '
                'deleted.\nAre you sure that you want to continue?',
                QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            fname = QFileDialog.getOpenFileName(self, title)
            if fname:
                msg = 'Succesful import!'
                try:
                    self.tree = etree.parse(fname)        
                except:
                    msg = 'Import failed!'    
                else:
                    self.root = self.tree.getroot()                                
                    self.save_tree()                
                QMessageBox.information(self, title, msg)                
    
    def export_presets(self):
        fname = QFileDialog.getSaveFileName(self,'FF Multi Converter - Export '
                                                              'presets','.xml')
        if fname:
            self.load_xml()
            with open(fname, 'w') as _file:
                try:
                    etree.ElementTree(self.root).write(_file)
                except:
                    pass                                                   
    
    def reset(self):
        reply = QMessageBox.question(self, 'FF Multi Converter - ' + self.tr(
            'Delete Preset'), 'Are you sure that you want to restore the '
            'default presets?', QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:        
            if os.path.exists(self.current_presets_file):
                os.remove(self.current_presets_file)
                

class AddorEditPreset(QDialog):
    def __init__(self, xml_element, edit=False, parent=None):
        super(AddorEditPreset, self).__init__(parent)

        nameLabel = QLabel(self.tr('Preset name (one word, A-z, 0-9)'))
        self.nameLineEdit = QLineEdit()
        labelLabel = QLabel(self.tr('Preset label'))
        self.labelLineEdit = QLineEdit()
        commandLabel = QLabel(self.tr('Preset command line parameters'))
        self.commandLineEdit = QLineEdit()
        extLabel = QLabel(self.tr('Output file extension'))
        self.extLineEdit = QLineEdit()
        self.buttonBox = QDialogButtonBox(
                                   QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        final_layout = pyqttools.add_to_layout(QVBoxLayout(), nameLabel,
            self.nameLineEdit, labelLabel, self.labelLineEdit, commandLabel,
            self.commandLineEdit, extLabel, self.extLineEdit, self.buttonBox)

        self.setLayout(final_layout)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.resize(410, 280)

        if edit:
            self.nameLineEdit.setText(xml_element.tag)
            self.labelLineEdit.setText(xml_element[0].text)
            self.commandLineEdit.setText(xml_element[1].text)
            self.commandLineEdit.home(False)
            self.extLineEdit.setText(xml_element[2].text)

            title = self.tr('Edit {0}'.format(xml_element.tag))
        else:
            title = self.tr('Add preset')

        self.resize(410, 280)
        self.setWindowTitle(title)

    def validation(self):
        self.name_text = str(self.nameLineEdit.text()).strip()
        self.label_text = str(self.labelLineEdit.text()).strip()
        self.command_text = str(self.commandLineEdit.text()).strip()
        self.ext_text = str(self.extLineEdit.text()).strip()

        if not self.name_text:
            QMessageBox.warning(self, 'Edit Preset - ' + self.tr('Error!'), 
                self.tr("Preset name can't be left blank."))
            self.nameLineEdit.setFocus()
            return False
        if not re.match('^[A-Za-z0-9]*$', self.name_text):
            QMessageBox.warning(self, 'Edit Preset - ' + self.tr('Error!'), 
                self.tr('Preset name must be one word and contain only letters '
                'and digits.'))
            self.nameLineEdit.selectAll()
            self.nameLineEdit.setFocus()
            return False
        if not self.label_text:
            QMessageBox.warning(self, 'Edit Preset - ' + self.tr('Error!'), 
                self.tr("Preset label can't be left blank."))
            self.labelLineEdit.setFocus()
            return False
        if not self.command_text:
            QMessageBox.warning(self, 'Edit Preset - ' + self.tr('Error!'), 
                self.tr("Command label can't be left blank."))
            self.commandLineEdit.setFocus()
            return False
        if not self.ext_text:
            QMessageBox.warning(self, 'Edit Preset - ' + self.tr('Error!'), 
                self.tr("Extension label can't be left blank."))
            self.extLineEdit.setFocus()
            return False
        if len(self.ext_text.split()) != 1 or self.ext_text[0] == '.':
            QMessageBox.warning(self, 'Edit Preset - ' + self.tr('Error!'), 
                self.tr("Extension must be one word and must not start with a"
                " dot."))
            self.extLineEdit.selectAll()
            self.extLineEdit.setFocus()
            return False
        return True

    def accept(self):
        if self.validation():
            QDialog.accept(self)


if __name__ == '__main__':
    #test dialog
    app = QApplication(sys.argv)
    dialog = ShowPresets()
    dialog.show()
    app.exec_()
