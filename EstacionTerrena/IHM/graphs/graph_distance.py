import pyqtgraph as pg

class graph_distance(pg.PlotItem):
    def __init__(self, parent=None, name=None, labels=None, title='Distancia entre cargas (m)', viewBox=None, axisItems=None, enableMenu=True, **kwargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kwargs)
        self.points_plot = self.plot(symbol='o', symbolSize=5, pen=None, symbolPen=(29, 185, 84))
        self.primary_text = pg.TextItem(text="CP", anchor=(0.5, 0.5))
        self.secondary_text = pg.TextItem(text="CS", anchor=(0.5, 0.5))
        self.addItem(self.primary_text)
        self.addItem(self.secondary_text)

    def update(self, x1, y1, x2, y2, distance):
        self.setTitle(f"Distancia entre cargas ({distance}m)")
        self.points_plot.setData([x1, x2], [y1, y2])
        self.primary_text.setPos(x1, y1)
        self.secondary_text.setPos(x2, y2)
        

