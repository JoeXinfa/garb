# -*- coding: utf-8 -*-
"""
https://wiki.python.org/moin/PyQt/Sorting%20numbers%20in%20columns
"""

import random, sys
from qtpy.QtCore import Qt, QVariant, QSortFilterProxyModel
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QApplication, QTableView


class NumberSortModel(QSortFilterProxyModel):
    def lessThan(self, left, right):
        lvalue = float(left.data())
        rvalue = float(right.data())
        return lvalue < rvalue
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = QStandardItemModel(5, 5)
    random.seed()
    for i in range(5):
        for j in range(5):
            item = QStandardItem()
            item.setData(QVariant(str(random.randint(-500, 500)/10.0)), Qt.DisplayRole)
            model.setItem(i, j, item)
            
    proxy = NumberSortModel()
    proxy.setSourceModel(model)
    
    view = QTableView()
    view.setModel(proxy)
    view.setSortingEnabled(True)
    view.show()
    sys.exit(app.exec_())
