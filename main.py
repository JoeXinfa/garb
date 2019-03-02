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
from qtpy.QtCore import Qt, QRegExp, QDate, QVariant
from qtpy.QtGui import QRegExpValidator, QIcon
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCalendarWidget, QTableWidget,
    QTableWidgetItem, QSplitter)

from qtpy import PYQT5
if PYQT5:
    APP_ICON = QIcon("images/shuttlecock.svg")
else:
    APP_ICON = QIcon("images/shuttlecock.png")


class ScoreBoard(QWidget):
    NAME = "League Scoreboard - 谁羽争锋"

    def __init__(self, path=None):
        QWidget.__init__(self)
        self.setWindowTitle(self.NAME)
        self.setWindowIcon(APP_ICON)
        self.games = {}
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

    @property
    def games_filename(self):
        return osp.join(self._path, "games.csv")

    def load_data(self):
        fn = self.loader.lineedit.edit.text()
        self.path = osp.dirname(fn)
        self.players = pd.read_csv(fn)
        print(self.players)
        
        players = list(self.players.Name)
        self.tap1.combobox.addItems(players)
        self.tap2.combobox.addItems(players)
        self.tbp1.combobox.addItems(players)
        self.tbp2.combobox.addItems(players)
        
        # update games list view
        self.load_games_from_file()
        self.display_games()        

    def setup_page(self):
        board = self.create_page_board()
        self.games_tbl = self.create_page_game()
        self.ranks_tbl = self.create_page_rank()

        splt = QSplitter(Qt.Horizontal)
        splt.addWidget(self.games_tbl)
        splt.addWidget(board)
        splt.addWidget(self.ranks_tbl)
        splt.setSizes([300, 100, 300])

        layout = QVBoxLayout()
        layout.addWidget(splt)
        self.setLayout(layout)

    def create_page_board(self):
        layout = QVBoxLayout()
        self.loader = self.create_browsefile("Load players")
        if self.path is not None:
            self.loader.lineedit.edit.setText(self.path)
        layout.addWidget(self.loader)
        board = self.create_board()
        layout.addWidget(board)
        calendar = self.create_calendar()
        layout.addWidget(calendar)
        widget = QWidget(self)
        widget.setLayout(layout)
        return widget
        
    def create_page_game(self):
        widget = QTableWidget()
        widget.setSortingEnabled(True)
        widget.setRowCount(1000)
        widget.setColumnCount(8)
        return widget

    def create_page_rank(self):
        widget = QTableWidget()
        widget.setSortingEnabled(True)
        widget.setRowCount(20)
        widget.setColumnCount(7)
        return widget

    def create_calendar(self):
        cal = QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.clicked[QDate].connect(self.insert_date)
        return cal
		
    def insert_date(self, date):
        self.cal_date = date
        self.date.edit.setText(date.toString())

    def load_game_to_board(self):
        pass

    def save_board_to_game(self):
        game = {}
        game["date"] = self.cal_date.toString('yyyy-MM-dd')
        game["seqno"] = int(self.seqno.edit.text())
        game["tap1"] = self.tap1.combobox.currentText()
        game["tap2"] = self.tap2.combobox.currentText()
        game["tbp1"] = self.tbp1.combobox.currentText()
        game["tbp2"] = self.tbp2.combobox.currentText()
        game["tas"] = int(self.tas.edit.text())
        game["tbs"] = int(self.tbs.edit.text())
        if game["seqno"] > 99:
            print("Too many games per day: {}".format(game["seqno"]))
        key = game["date"] + "-" + "{:02d}".format(game["seqno"])
        self.games[key] = game
        print(key, self.games[key])
        self.save_games_to_file()
        # update games list view
        self.load_games_from_file()
        self.display_games()
        # todo update players rank view

    def display_games(self):
        nrow, ncol = self.games_df.shape
        # todo column width adjust with content
        for row in range(nrow):
            for col in range(ncol):
                val = self.games_df.iloc[row].iloc[col]
                cell = QTableWidgetItem()
                cell.setText(str(val))
                self.games_tbl.setItem(row, col, cell)

    def load_games_from_file(self):
        fn = self.games_filename
        self.games_df = pd.read_csv(fn)
        
    def save_games_to_file(self):
        fn = self.games_filename
        df = pd.DataFrame.from_dict(self.games, orient='index')
        df.to_csv(fn, index = False)

    def create_board(self):
        game  = QLabel("Game ID   ")
        teama = QLabel("Team A    ")
        teamb = QLabel("Team B    ")
        self.date = self.create_lineedit("Date")
        self.seqno = self.create_lineedit("Seqno")
        self.tas = self.create_lineedit("Score")
        self.tbs = self.create_lineedit("Score")
        self.tap1 = self.create_combobox("Player 1")
        self.tap2 = self.create_combobox("Player 2")
        self.tbp1 = self.create_combobox("Player 1")
        self.tbp2 = self.create_combobox("Player 2")
        btn_load = QPushButton("Load")
        btn_load.clicked.connect(self.load_game_to_board)
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save_board_to_game)
        
        layout = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(game)
        hbox.addWidget(self.date)
        hbox.addWidget(self.seqno)
        layout.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(teama)
        hbox.addWidget(self.tap1)
        hbox.addWidget(self.tap2)
        hbox.addWidget(self.tas)
        layout.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(teamb)
        hbox.addWidget(self.tbp1)
        hbox.addWidget(self.tbp2)
        hbox.addWidget(self.tbs)
        layout.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(btn_load)
        hbox.addWidget(btn_save)
        layout.addLayout(hbox)
        
        board = QWidget(self)
        board.setLayout(layout)
        return board
   
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
    path = "C:/Users/xinfa/Documents/score" # for beta testing

    app = QApplication([])
    gui = ScoreBoard(path=path)
    gui.show()
    app.exec_()


if __name__ == '__main__':
    main()
