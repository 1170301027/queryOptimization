from tkinter import Tk, ttk
from tkinter import *

class UI():
    """
    UI类用于前端显示分析树
    """
    def __init__(self):
        pass

    def root(self):
        # 初始化窗口
        window = Tk()
        window.title('LR分析表')
        window.geometry('600x600')
        window.resizable(0, 0)

        column = ['符号', 'First集']
        treeview = ttk.Treeview(window, height=19, columns=column, show='headings')
        treeview.pack(anchor=W, ipadx=100, side=LEFT, expand=True, fill=BOTH)
        treeview.column(column[0], width=100, anchor='center')
        treeview.heading(column[0], text=column[0])
        treeview.column(column[1], width=1000, anchor='w')
        treeview.heading(column[1], text=column[1])
        # ----vertical scrollbar------------
        vbar1 = ttk.Scrollbar(treeview, orient=VERTICAL, command=treeview.yview)
        treeview.configure(yscrollcommand=vbar1.set)
        vbar1.pack(side=RIGHT, fill=Y)
        # ----horizontal scrollbar----------
        hbar1 = ttk.Scrollbar(treeview, orient=HORIZONTAL, command=treeview.xview)
        treeview.configure(xscrollcommand=hbar1.set)
        hbar1.pack(side=BOTTOM, fill=X)
        window.rowconfigure(0, weight=1)
        window.columnconfigure(0, weight=1)

        count = 0
        for i in self.parser.firsts.keys():
            temp = treeview.insert('', index=count)  # 新建行
            treeview.set(temp, column=column[0], value=str(i))
            first = []
            for terminal in self.parser.firsts[i]:
                first.append(str(terminal))
            text = (', ').join(first)
            treeview.set(temp, column=column[1], value=(text))
            count += 1
        window.mainloop()
