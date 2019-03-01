# -*- coding: utf-8 -*-

"""
Scoreboard for badminton league
"""

__version__ = '0.1.0'

import os
import os.path as osp

import pandas as pd
import qtawesome as qta
from qtpy.compat import getopenfilename, getsavefilename
from qtpy.QtCore import Qt, QRegExp
from qtpy.QtGui import QRegExpValidator
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QDialog)


class ScoreBoard(QDialog):
    def __init__(self, path=None):
        QDialog.__init__(self)
        if path is None:
            path = os.getcwd()
        self.path = path
        self.setup_page()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    def load_data(self):
        fn = self.loader.lineedit.edit.text()
        self.players = pd.read_csv(fn)
        print(self.players)
        
        players = list(self.players.Name)
        self.tap1.combobox.addItems(players)

    def setup_page(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        text = "Load players"
        self.loader = self.create_browsefile(text)
        if self.path is not None:
            self.loader.lineedit.edit.setText(self.path)
        self.layout.addWidget(self.loader)

        text = "Player 1"
        self.tap1 = self.create_combobox(text)
        self.layout.addWidget(self.tap1)

    def save_file(self):
        pass
    
    def create_combobox(self, text, choices=None, tip=None, restart=False):
        """choices: couples (name, key)"""
        label = QLabel(text)
        combobox = QComboBox()
        # combobox.setMinimumContentsLength(10)
        combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        if tip is not None:
            combobox.setToolTip(tip)
        # for name, key in choices:
        #     if not (name is None and key is None):
        #         combobox.addItem(name, to_qvariant(key))
        # Insert separators
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(combobox)
        layout.addStretch(1)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QWidget(self)
        widget.label = label
        widget.combobox = combobox
        widget.setLayout(layout)
        return widget    
    
    def create_browsefile(self, text, default=None, tip=None,
                          filters=None, new=False):
        widget = self.create_lineedit(text, default=default, tip=tip)
        edit = widget.edit
        browse_btn = QPushButton(icon('FileIcon'), '', self)
        browse_btn.setToolTip("Select file")
        browse_btn.clicked.connect(lambda: self.select_file(edit, filters, new))
        layout = QHBoxLayout()
        layout.addWidget(widget)
        layout.addWidget(browse_btn)
        layout.setContentsMargins(0, 0, 0, 0)
        browsefile = QWidget(self)
        browsefile.lineedit = widget
        browsefile.setLayout(layout)
        return browsefile

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

    def select_file(self, edit, filters=None, new=False):
        """
        -i- edit : QLineEdit, for display the selected file.
        -i- filters : String, filter in the browse-file dialog.
        -i- new : boolean, select existing or create new file.
        """
        initdir = edit.text()
        if osp.isdir(initdir):
            basedir = initdir
        else:
            basedir = osp.dirname(initdir)
            if not osp.isdir(basedir):
                basedir = os.getcwd()
        if filters is None:
            filters = "All files (*)"
        title = "Select file"
        if new:
            filename, _selfilter = getsavefilename(self, title, basedir, filters)
        else:
            filename, _selfilter = getopenfilename(self, title, basedir, filters)
        if filename:
            edit.setText(filename)
            self.load_data()


_resource = {
    'directory': osp.join(osp.dirname(osp.realpath(__file__)), 'fonts'),
    'loaded': False,
}

_qtaargs = {
    'FileIcon': [('fa.file-o',), {}],
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
