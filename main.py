# -*- coding: utf-8 -*-

"""
Scoreboard for badminton league
"""

__version__ = '0.1.0'

import os
import os.path as osp


import qtawesome as qta
from qtpy.compat import getexistingdirectory
from qtpy.QtCore import Qt, QRegExp
from qtpy.QtGui import QRegExpValidator
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QLineEdit)


class ScoreBoard(QWidget):
    def __init__(self, path=None):
        QWidget.__init__(self)
        if path is None:
            path = os.getcwd()
        self.path = path
        self.load_data()
        self.setup_page()

    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, value):
        self._path = value

    def load_data(self):
        pass

    def setup_page(self):
        self.layout = QVBoxLayout()
        
        text = "Data folder"
        self.select_dir = self.create_browsedir(text)
        self.layout.addWidget(self.select_dir)

    def save_file(self):
        pass

    def create_browsedir(self, text, default=None, tip=None):
        widget = self.create_lineedit(text, default=default, tip=tip)
        edit = widget.edit
        browse_btn = QPushButton(icon('DirOpenIcon'), '', self)
        browse_btn.setToolTip("Select directory")
        browse_btn.clicked.connect(lambda: self.select_directory(edit))
        layout = QHBoxLayout()
        layout.addWidget(widget)
        layout.addWidget(browse_btn)
        layout.setContentsMargins(0, 0, 0, 0)
        browsedir = QWidget(self)
        browsedir.lineedit = widget
        browsedir.setLayout(layout)
        return browsedir

    def create_lineedit(self, text, default=None, tip=None,
                        alignment=Qt.Horizontal, regex=None, wrap=True):
        label = QLabel(text)
        label.setWordWrap(wrap)
        edit = QLineEdit()
        layout = QHBoxLayout() if alignment == Qt.Horizontal else QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(edit)
        layout.setContentsMargins(0, 0, 0, 0)
        if default:
            edit.setText(default)
        if tip:
            edit.setToolTip(tip)
        if regex:
            edit.setValidator(QRegExpValidator(QRegExp(regex)))
        widget = QWidget(self)
        widget.label = label
        widget.edit = edit
        widget.setLayout(layout)
        return widget

    def select_directory(self, edit):
        basedir = edit.text()
        if not osp.isdir(basedir):
            basedir = os.getcwd()
        title = "Select directory"
        directory = getexistingdirectory(self, title, basedir)
        if directory:
            edit.setText(directory)
            self.path = directory


_resource = {
    'directory': osp.join(osp.dirname(osp.realpath(__file__)), 'fonts'),
    'loaded': False,
}

_qtaargs = {
    'DirOpenIcon':  [('fa.folder-open',), {}],
}

def icon(name, resample=False, icon_path=None):
        if not _resource['loaded']:
            print('Loading iconic fonts...')
            qta.load_font('fa', 'fontawesome-webfont-4.7.0.ttf',
                          'fontawesome-webfont-4.7.0-charmap.json',
                          directory=_resource['directory'])
            _resource['loaded'] = True
        args, kwargs = _qtaargs[name]
        return qta.icon(*args, **kwargs)


def main():
    import argparse
    from qtpy.QtWidgets import QApplication

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help='path to scores')
    args = parser.parse_args()
    path = args.path

    app = QApplication([])
    gui = ScoreBoard(path=path)
    gui.show()
    app.exec_()


if __name__ == '__main__':
    main()
