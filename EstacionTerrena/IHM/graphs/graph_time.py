import pyqtgraph as pg


class graph_time(pg.PlotItem):
        
    def __init__(self, parent=None, name=None, labels=None, title=None, viewBox=None, axisItems=None, enableMenu=True, font = None,**kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)

        self.hideAxis('bottom')
        self.hideAxis('left')
        self.time_text = pg.TextItem("test", anchor=(0.5, 0.5), color="k")
        
        if font != None:
            self.time_text.setFont(font)
            
        self.addItem(self.time_text)


    def update(self, value):
        self.time_text.setText('')
        total_seconds = int(value) // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.tiempo = f"{minutes}.{seconds}"
        
        self.time_text.setText("Time: " + str(self.tiempo))