# -*- coding: utf-8 -*-

"""
Scoreboard for badminton league
"""

__version__ = '0.1.0'

import os
import os.path as osp
import numpy as np
import pandas as pd
import qtawesome as qta
from qtpy.compat import getopenfilename, getsavefilename
from qtpy.QtCore import Qt, QRegExp, QDate, QVariant
from qtpy.QtGui import QRegExpValidator, QIcon
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCalendarWidget, QTableWidget,
    QTableWidgetItem, QSplitter, QHeaderView)

from qtpy import PYQT5
if PYQT5:
    APP_ICON = QIcon("images/shuttlecock.svg")
else:
    APP_ICON = QIcon("images/shuttlecock.png")


GAME_LIST = ['Date', 'Seq', 'TAP1', 'TAP2', 'TBP1', 'TBP2', 'TAS', 'TBS']
RANK_LIST = ['Player', 'Games', 'Points', 'PPG', 'Bonus', 'GPA']

class ScoreBoard(QWidget):
    NAME = "League Scoreboard - 谁羽争锋"

    def __init__(self, path=None):
        QWidget.__init__(self)
        self.setWindowTitle(self.NAME)
        self.setWindowIcon(APP_ICON)
        self.games = None # pandas dataframe
        self.ranks = None # pandas dataframe
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
        
        # load games and update games table
        self.load_games_from_file()
        self.display_games()
        self.update_ranks()

    def setup_page(self):
        width, height = 1500, 500
        board = self.create_page_board()
        self.games_tbl = self.create_page_game()
        self.ranks_tbl = self.create_page_rank()

        splt = QSplitter(Qt.Horizontal)
        splt.addWidget(self.games_tbl)
        splt.addWidget(board)
        splt.addWidget(self.ranks_tbl)
        splt.setSizes([700, 300, 500])

        layout = QVBoxLayout()
        layout.addWidget(splt)
        self.setLayout(layout)
        
        self.resize(width, height)

    def create_page_board(self):
        self.loader = self.create_browsefile("Load players")
        if self.path is not None:
            self.loader.lineedit.edit.setText(self.path)
        board = self.create_board()
        calendar = self.create_calendar()
        
        splt = QSplitter(Qt.Vertical)
        splt.addWidget(self.loader)
        splt.addWidget(board)
        splt.addWidget(calendar)
        
        layout = QVBoxLayout()
        layout.addWidget(splt)
        widget = QWidget(self)
        widget.setLayout(layout)
        return widget
        
    def create_page_game(self):
        widget = QTableWidget()
        widget.setSortingEnabled(True)
        widget.setRowCount(1000)
        widget.setColumnCount(len(GAME_LIST))
        widget.setHorizontalHeaderLabels(GAME_LIST)
        header = widget.horizontalHeader()
        for i in range(len(GAME_LIST)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        return widget

    def create_page_rank(self):
        widget = QTableWidget()
        widget.setSortingEnabled(True)
        widget.setRowCount(20)
        widget.setColumnCount(len(RANK_LIST))
        widget.setHorizontalHeaderLabels(RANK_LIST)
        header = widget.horizontalHeader()
        for i in range(len(RANK_LIST)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
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
        date = self.cal_date.toString('yyyy-MM-dd')
        seqno = int(self.seqno.edit.text())
        tap1 = self.tap1.combobox.currentText()
        tap2 = self.tap2.combobox.currentText()
        tbp1 = self.tbp1.combobox.currentText()
        tbp2 = self.tbp2.combobox.currentText()
        tas = int(self.tas.edit.text())
        tbs = int(self.tbs.edit.text())
        if seqno > 99:
            print("Too many games per day: {}".format(seqno))
        
        # TODO warn if this game already exist in self.games
        game = pd.DataFrame([[date, seqno, tap1, tap2, tbp1, tbp2,
            tas, tbs]], columns=GAME_LIST)
        if self.games is None:
            self.games = game
        else:
            self.games = self.games.append(game, ignore_index=True)
        self.games = self.games.drop_duplicates(subset=GAME_LIST[:2],
            keep='last')
        
        self.save_games_to_file()
        
        # load games and update games table
        self.load_games_from_file()
        self.display_games()
        # TODO reset all cells or just the one game?
        
        self.update_ranks()

    def update_ranks(self):
        index = list(self.players.Name)
        index.remove('None')
        columns = RANK_LIST[1:]
        nrow, ncol = len(index), len(columns)
        data = np.zeros((nrow, ncol))
        self.ranks = pd.DataFrame(data, index=index, columns=columns)

        # Count number of games and points
        for index, row in self.games.iterrows():
            if row['TAS'] > row['TBS']:
                pointa, pointb = 2, 1
            else:
                pointa, pointb = 1, 2
            tap1 = row['TAP1']
            tap2 = row['TAP2']
            tbp1 = row['TBP1']
            tbp2 = row['TBP2']
            self.ranks.loc[tap1].loc['Games'] += 1
            self.ranks.loc[tap2].loc['Games'] += 1
            self.ranks.loc[tbp1].loc['Games'] += 1
            self.ranks.loc[tbp2].loc['Games'] += 1
            self.ranks.loc[tap1].loc['Points'] += pointa
            self.ranks.loc[tap2].loc['Points'] += pointa
            self.ranks.loc[tbp1].loc['Points'] += pointb
            self.ranks.loc[tbp2].loc['Points'] += pointb

        # Calculate PPG, Bonus, and GPA
        for index, row in self.ranks.iterrows():
            if row['Games'] == 0:
                row['PPG'] = 0
            else:
                row['PPG'] = row['Points'] / row['Games']
            row['Bonus'] = row['Games'] * 0.01
            row['GPA'] = row['PPG'] + row['Bonus']

        # Refresh display
        self.display_ranks()

    def display_ranks(self):
        if self.ranks is None:
            return
        nrow, ncol = self.ranks.shape
        irow = 0
        for index, row in self.ranks.iterrows():
            pcell = QTableWidgetItem()
            pcell.setText(index)
            self.ranks_tbl.setItem(irow, 0, pcell)
            for icol in range(ncol):
                cell = QTableWidgetItem()
                val = row.iloc[icol]
                #if icol in [0, 1]:
                #    val = str(int(val))
                #else:
                #    val = "{0:.3f}".format(val)
                #cell.setText(val)
                if icol in [0, 1]:
                    val = int(val)
                else:
                    val = "{0:.3f}".format(val)
                cell.setData(Qt.EditRole, QVariant(val))
                self.ranks_tbl.setItem(irow, icol+1, cell)
            irow += 1

    def display_games(self):
        if self.games is None:
            return
        nrow, ncol = self.games.shape
        for row in range(nrow):
            for col in range(ncol):
                val = self.games.iloc[row].iloc[col]
                cell = QTableWidgetItem()
                cell.setText(str(val))
                self.games_tbl.setItem(row, col, cell)

    def load_games_from_file(self):
        fn = self.games_filename
        if osp.isfile(fn):
            self.games = pd.read_csv(fn)
        
    def save_games_to_file(self):
        fn = self.games_filename
        #df = pd.DataFrame.from_dict(self.games, orient='index')
        self.games.to_csv(fn, index = False)

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
        combobox.setMinimumContentsLength(12)
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
