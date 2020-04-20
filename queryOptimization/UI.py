from tkinter import Tk, ttk
from tkinter import *
from queryOptimization.cfg import *
from queryOptimization.tag import Tag

class UI():
    """
    UI类用于前端显示分析树
    """
    def __init__(self,parser,query):
        self.parser = parser
        self.query = query

    def root(self):
        # 初始化窗口
        window = Tk()
        window.title('语法分析树')
        window.geometry('600x600')
        window.resizable(0, 0)

        processTree = ttk.Treeview(window)
        processTree.pack(fill=BOTH, expand=YES)

        self.parser.run(self.query)
        # for production in self

        items = []
        nodes = [self.parser.root_node]
        items.append(processTree.insert('', 0, text=str(nodes[0].grammar_symbol),open=True))
        for pNode in nodes:
            pNodeItem = items[nodes.index(pNode)]
            subNodes = pNode.get_subnodes()
            for subNode in subNodes:
                symbol = subNode.grammar_symbol
                if isinstance(symbol, Terminal):
                    screen_show = symbol.character + ' :' + str(symbol)
                else:
                    screen_show = str(symbol)
                items.append(processTree.insert(pNodeItem, 0, text=screen_show, open=True))
            nodes.extend(subNodes)
        window.mainloop()
