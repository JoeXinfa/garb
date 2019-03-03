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
import pyqtgraph as pg
from qtpy.compat import getopenfilename, getsavefilename
from qtpy.QtCore import Qt, QRegExp, QDate, QVariant
from qtpy.QtGui import QRegExpValidator, QIcon
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCalendarWidget, QTableWidget,
    QTableWidgetItem, QSplitter, QHeaderView, QApplication, QStyleFactory,
    QAbstractItemView)

from qtpy import PYQT5
if PYQT5:
    APP_ICON = QIcon("images/shuttlecock.svg")
else:
    APP_ICON = QIcon("images/shuttlecock.png")


GAME_LIST = ['Date', 'Seq', 'TAP1', 'TAP2', 'TBP1', 'TBP2', 'TAS', 'TBS']
RANK_LIST = ['Player', 'Games', 'Points', 'PPG', 'Bonus', 'GPA']
PLAYERS_FILENAME = "players.csv"
GAMES_FILENAME = "games.csv"
RANKS_FILENAME = "ranks.csv"

class ScoreBoard(QWidget):
    NAME = "Games Automatic Ranking for Badminton (GARB) - 谁羽争锋"

    def __init__(self, path=None):
        QWidget.__init__(self)
        self.setWindowTitle(self.NAME)
        self.setWindowIcon(APP_ICON)
        self.games = None # pandas dataframe
        self.ranks = None # pandas dataframe
        self.fn_players = None
        self.fn_games = None
        self.rank_order = 1 # descending
        self.rank_column = 1
        if path is None:
            path = os.getcwd()
        self.path = path
        self.setup_page()
        QApplication.setStyle(QStyleFactory.create('Cleanlooks'))

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    def load_data(self):
        self.fn_players = self.load_players.lineedit.edit.text()
        if self.path is None:
            self.path = osp.dirname(self.fn_players)
        self.players = pd.read_csv(self.fn_players)
        print(self.players)
        
        players = list(self.players.Name)
        self.tap1.combobox.addItems(players)
        self.tap2.combobox.addItems(players)
        self.tbp1.combobox.addItems(players)
        self.tbp2.combobox.addItems(players)
        
        # load games and update games table
        self.fn_games = self.load_games.lineedit.edit.text()
        self.load_games_from_file()
        self.display_games()
        self.update_ranks()

    def setup_page(self):
        width, height = 1500, 600
        board = self.create_page_board()
        self.games_tbl = self.create_page_game()
        self.ranks_tbl = self.create_page_rank()

        splt = QSplitter(Qt.Horizontal)
        splt.addWidget(self.games_tbl)
        splt.addWidget(board)
        splt.addWidget(self.ranks_tbl)
        splt.setSizes([700, 300, 500])
        #splt.setHandleWidth(10)
        splt.setStyleSheet("QSplitter::handle { background-color: rgb(0, 255, 0); }")

        layout = QVBoxLayout()
        layout.addWidget(splt)
        self.setLayout(layout)
        
        self.resize(width, height)

    def create_chart(self):
        win = pg.PlotWidget()
        # create list of floats
        y = np.linspace(0, 20, num=20)
        # create horizontal list
        x = np.arange(20)
        # create bar chart
        self.bar_graph_item = pg.BarGraphItem(x=x, height=y, width=0.6, brush='r')
        win.addItem(self.bar_graph_item)
        return win

    def update_chart(self, col, order):
        self.rank_column = col
        self.rank_order = order
        print("Sort column {} with order {}".format(col+1, order))
        nplayer = self.players.shape[0] - 1
        x = np.arange(1, nplayer+1)
        y = self.ranks.iloc[:,col-1].values
        y.sort() # numpy ascending order
        #if order == 0: # AscendingOrder
        if order == 1: # DescendingOrder
            y = y[::-1] # reverse the sorted array
        self.bar_graph_item.setOpts(x=x, height=y)

    def create_page_board(self):
        self.load_players = self.create_browsefile("Players file")
        self.load_games = self.create_browsefile("Games file")
        btn_load = QPushButton("Load files")
        btn_load.clicked.connect(self.load_data)
        if self.path is not None:
            fn_players = osp.join(self.path, PLAYERS_FILENAME)
            fn_games = osp.join(self.path, GAMES_FILENAME)
            self.load_players.lineedit.edit.setText(fn_players)
            self.load_games.lineedit.edit.setText(fn_games)
        layout = QVBoxLayout()
        layout.addWidget(self.load_players)
        layout.addWidget(self.load_games)
        layout.addWidget(btn_load)
        wgt_load = QWidget()
        wgt_load.setLayout(layout)

        board = self.create_board()
        calendar = self.create_calendar()
        chart = self.create_chart()
        
        splt = QSplitter(Qt.Vertical)
        splt.addWidget(wgt_load)
        splt.addWidget(board)
        splt.addWidget(calendar)
        splt.addWidget(chart)
        
        layout = QVBoxLayout()
        layout.addWidget(splt)
        widget = QWidget(self)
        widget.setLayout(layout)
        return widget
        
    def create_page_game(self):
        widget = QTableWidget()
        widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
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
        widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        widget.setSortingEnabled(True)
        widget.setRowCount(20)
        widget.setColumnCount(len(RANK_LIST))
        widget.setHorizontalHeaderLabels(RANK_LIST)
        header = widget.horizontalHeader()
        for i in range(len(RANK_LIST)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        widget.horizontalHeader().sortIndicatorChanged.connect(self.update_chart)
        return widget

    def create_calendar(self):
        cal = QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.clicked[QDate].connect(self.insert_date)
        return cal
		
    def insert_date(self, date):
        self.cal_date = date
        self.date.edit.setText(date.toString())

    def edit_game(self):
        """ Edit an existing game in the table """
        pass
        #self.games = self.games.drop_duplicates(subset=GAME_LIST[:2],
        #    keep='last')
    
    def add_game(self):
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
        game = pd.DataFrame([[date, seqno, tap1, tap2, tbp1, tbp2,
            tas, tbs]], columns=GAME_LIST)
        # Add game to database
        # TODO warn if this game already exist in self.games
        if self.games is None:
            self.games = game
        else:
            self.games = self.games.append(game, ignore_index=True)
        # Add game to table for view
        self.add_game_to_table(game)
        
        #self.update_ranks()

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
        # Sort table by descending GPA
        #self.ranks_tbl.horizontalHeader().setSortIndicator(5, Qt.DescendingOrder)

    def add_game_to_table(self, game):
        """ Append a row at bottom of the table for this game """
        nrow, ncol = self.games.shape
        print("Add game to row {}".format(nrow))
        for col in range(ncol):
            cell = QTableWidgetItem()
            val = game.iloc[0].iloc[col]
            if col in [1, 6, 7]:
                val = int(val)
                cell.setData(Qt.EditRole, QVariant(val))
            else:
                val = str(val)
                cell.setText(val)
            self.games_tbl.setItem(nrow-1, col, cell)

    def display_games(self):
        if self.games is None:
            return
        nrow, ncol = self.games.shape
        for row in range(nrow):
            for col in range(ncol):
                cell = QTableWidgetItem()
                val = self.games.iloc[row].iloc[col]
                if col in [1, 6, 7]:
                    val = int(val)
                    cell.setData(Qt.EditRole, QVariant(val))
                else:
                    val = str(val)
                    cell.setText(val)
                self.games_tbl.setItem(row, col, cell)

    def load_games_from_file(self):
        fn = self.fn_games
        if osp.isfile(fn):
            self.games = pd.read_csv(fn)
        
    def save_games_to_file(self):
        fn = self.fn_games
        #df = pd.DataFrame.from_dict(self.games, orient='index')
        self.games.to_csv(fn, index=False)

    def save_ranks_to_file(self):
        fn = osp.join(osp.dirname(self.fn_games), RANKS_FILENAME)
        self.ranks.to_csv(fn, index=True)

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
        btn_add_game = QPushButton("Add game")
        btn_add_game.clicked.connect(self.add_game)
        btn_edit_game = QPushButton("Edit game")
        btn_edit_game.clicked.connect(self.edit_game)
        btn_edit_game.setEnabled(False)
        btn_save_games = QPushButton("Save games to file")
        btn_save_games.clicked.connect(self.save_games_to_file)
        btn_save_ranks = QPushButton("Save ranks to file")
        btn_save_ranks.clicked.connect(self.save_ranks_to_file)
        
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
        hbox.addWidget(btn_add_game)
        hbox.addWidget(btn_edit_game)
        hbox.addWidget(btn_save_games)
        hbox.addWidget(btn_save_ranks)
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
            #self.load_data()


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
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help='path to scores')
    args = parser.parse_args()
    path = args.path
    
    # for qhick beta testing
    path = "C:/Users/xinfa/Documents/league/garb"
    path = path.replace("/", os.sep)
    print("User input path:", path)

    app = QApplication([])
    gui = ScoreBoard(path=path)
    gui.show()
    app.exec_()


if __name__ == '__main__':
    main()
