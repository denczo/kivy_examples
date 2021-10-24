from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, LinePlot
import numpy as np


class MainApp(App):

    def build(self):
        return MainGrid()


class MainGrid(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.samples = 300
        self.graph = Graph(y_ticks_major=0.5,
                           x_ticks_major=50,
                           border_color=[0, 1, 1, 1],
                           tick_color=[0, 1, 1, 0.5],
                           x_grid=True, y_grid=True,
                           xmin=0, xmax=self.samples,
                           ymin=-1.0, ymax=1.0,
                           draw_border=True,
                           x_grid_label=True, y_grid_label=True)

        self.ids.modulation.add_widget(self.graph)
        self.plot_x = np.linspace(0, 1, self.samples)
        self.plot_y = np.zeros(self.samples)
        self.plot = LinePlot(color=[0, 1, 1, 1])
        self.graph.add_plot(self.plot)
        self.update_plot(1)

    def update_plot(self, freq):
        self.plot_y = np.sin(2*np.pi*freq*self.plot_x)
        self.plot.points = [(x, self.plot_y[x]) for x in range(self.samples)]


MainApp().run()
