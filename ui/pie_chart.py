from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem
from PyQt5.QtGui import QColor


class PieChart(object):
    def __init__(self, ):
        self.colours = [QColor(0, 255, 0, 128), QColor(255, 0, 0, 128)]
        self.scene = QGraphicsScene()

    def set_chart(self, percentage_data):
        self.scene.clear()
        set_angle = 0
        count = 0
        total = sum(percentage_data)

        for data in percentage_data:
            angle = ((data*16.0*360)/total)
            ellipse = QGraphicsEllipseItem(0, 0, 360, 250)
            ellipse.setPos(0, 0)
            ellipse.setStartAngle(set_angle)
            ellipse.setSpanAngle(angle)
            ellipse.setBrush(self.colours[count])
            set_angle += angle
            count += 1
            self.scene.addItem(ellipse)

    def get_chart(self):
        return self.scene