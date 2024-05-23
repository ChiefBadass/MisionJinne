import pyqtgraph as pg
from PyQt5.QtGui import QFont

class graph_distance(pg.PlotItem):
    def __init__(self, parent=None, name=None, labels=None, title='Distancia entre cargas (m)', viewBox=None, axisItems=None, enableMenu=True, **kwargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kwargs)
        
        
        self.points_plot = self.plot(symbol='o', symbolSize=25, pen=None, symbolPen=(0, 0, 0))
        
        
        self.primary_text = pg.TextItem(text="CP", anchor=(0.5, 0.5))
        self.secondary_text = pg.TextItem(text="CS", anchor=(0.5, 0.5))
        
        
        self.addItem(self.primary_text)
        self.addItem(self.secondary_text)
        
        
        self.line_between_points = self.plot(pen=(0, 0, 0), width=2)
        
       
        self.cardinal_label = pg.TextItem(anchor=(0.5, 1.5)) 
        self.cardinal_label.setFont(QFont("Arial", 12, QFont.Bold))  
        self.cardinal_label.setColor((0, 0, 0))  
        self.addItem(self.cardinal_label)

    def update(self, x1, y1, x2, y2, distance, cardinal_direction):
        self.setTitle(f"Distancia entre cargas ({distance}m)")
        self.points_plot.setData([x1, x2], [y1, y2])
        self.primary_text.setPos(x1, y1)
        self.secondary_text.setPos(x2, y2)
        
        
        self.line_between_points.setData([x1, x2], [y1, y2])
        
        
        self.cardinal_label.setText(cardinal_direction)
        self.cardinal_label.setPos((x1 + x2) / 2, (y1 + y2) / 2)
        

