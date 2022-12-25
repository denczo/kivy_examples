import threading
from kivy.app import App
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, LinePlot
import numpy as np
import multiprocessing as mp
from multiprocessing import Pool
import ctypes as c
from kivy.clock import Clock
from random import randrange


samples = 4096
amount_graphs = 4
total_samples = samples * amount_graphs
shared_array = mp.Array(c.c_double, np.zeros(total_samples), lock=False)
shared_array_np = np.ndarray(total_samples, dtype=c.c_double, buffer=shared_array)
# frequency
shared_value = mp.Value('i', 5)
plot_x = np.linspace(0, 1, total_samples)


def task():
    freq = shared_value.value
    plot_y_top_left = np.sin(2*np.pi*freq*plot_x[:samples])* 0.8
    plot_y_bottom_left = np.sign(np.sin(2*np.pi*freq*plot_x[samples:samples*2])) * 0.8
    plot_y_top_right = np.sign(np.sin(2*np.pi*freq*plot_x[samples*2:samples*3])) * 0.8
    plot_y_bottom_right = np.sign(np.sin(2*np.pi*freq*plot_x[samples*3:samples*4])) * 0.8
    
    array = np.zeros(samples*4)
    array[:samples] = plot_y_top_left
    array[samples:samples*2] = plot_y_bottom_left
    array[samples*2:samples*3] = plot_y_top_right
    array[samples*3:samples*4] = plot_y_bottom_right

    np.copyto(shared_array_np, array)
    print("running task")

cpus = mp.cpu_count()
print("Amount of CPUs", cpus)
pool = Pool(cpus)


class MainApp(App):

    def build(self):
        self.app = MainGrid()
        return self.app

class MainGrid(BoxLayout):

    freq = NumericProperty(5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.samples = samples
        self.graph_top_left = Graph(y_ticks_major=0.5,
                           x_ticks_major=self.samples/8,
                           border_color=[0, 1, 1, 1],
                           tick_color=[0, 1, 1, 0.7],
                           x_grid=True, y_grid=True,
                           xmin=0, xmax=self.samples,
                           ymin=-1.0, ymax=1.0,
                           draw_border=False,
                           x_grid_label=True, y_grid_label=False)

        self.graph_bottom_left = Graph(y_ticks_major=0.5,
                           x_ticks_major=self.samples/8,
                           border_color=[0, 1, 1, 1],
                           tick_color=[0, 1, 1, 0.7],
                           x_grid=True, y_grid=True,
                           xmin=self.samples, xmax=self.samples*2,
                           ymin=-1.0, ymax=1.0,
                           draw_border=False,
                           x_grid_label=True, y_grid_label=False)

        self.graph_top_right = Graph(y_ticks_major=0.5,
                           x_ticks_major=self.samples/8,
                           border_color=[0, 1, 1, 1],
                           tick_color=[0, 1, 1, 0.7],
                           x_grid=True, y_grid=True,
                           xmin=self.samples*2, xmax=self.samples*3,
                           ymin=-1.0, ymax=1.0,
                           draw_border=False,
                           x_grid_label=True, y_grid_label=False)

        self.graph_bottom_right = Graph(y_ticks_major=0.5,
                           x_ticks_major=self.samples/8,
                           border_color=[0, 1, 1, 1],
                           tick_color=[0, 1, 1, 0.7],
                           x_grid=True, y_grid=True,
                           xmin=self.samples*3, xmax=self.samples*4,
                           ymin=-1.0, ymax=1.0,
                           draw_border=False,
                           x_grid_label=True, y_grid_label=False)

        # Mono, Sampling Rate, Chunksize
        self.ids.graph_top_left.add_widget(self.graph_top_left)
        self.ids.graph_bottom_left.add_widget(self.graph_bottom_left)
        self.ids.graph_top_right.add_widget(self.graph_top_right)
        self.ids.graph_bottom_right.add_widget(self.graph_bottom_right)
        self.plot_x = np.linspace(0, 1, self.samples*4)
        self.plot_y = np.zeros(self.samples)
        self.plot_top_left = LinePlot(color=[1, 1, 0, 1], line_width=1.5)
        self.plot_bottom_left = LinePlot(color=[1, 0, 1, 1], line_width=1.5)
        self.plot_top_right = LinePlot(color=[1, 0, 0, 1], line_width=1.5)
        self.plot_bottom_right = LinePlot(color=[1, 1, 0, 1], line_width=1.5)
        

        self.graph_top_left.add_plot(self.plot_top_left)
        self.graph_bottom_left.add_plot(self.plot_bottom_left)
        self.graph_top_right.add_plot(self.plot_top_right)
        self.graph_bottom_right.add_plot(self.plot_bottom_right)

        self.update_freq(4)
        # self.update_plot_single_core(10)

    def update_plot_multi_core(self, freq):
        pool.apply(task)
        self.plot_top_left.points = [(x, shared_array_np[x]) for x in range(self.samples)]
        self.plot_bottom_left.points = [(x, shared_array_np[x]) for x in range(self.samples, self.samples*2)]
        self.plot_top_right.points = [(x, shared_array_np[x]) for x in range(self.samples*2, self.samples*3)]
        self.plot_bottom_right.points = [(x, shared_array_np[x]) for x in range(self.samples*3, self.samples*4)]
   

    def update_plot_single_core(self, freq):
        self.plot_y = np.sin(2*np.pi*freq*self.plot_x)
        self.plot.points = [(x, self.plot_y[x]) for x in range(self.samples)]
  
    def update_freq(self, value):
        # with shared_value.get_lock():
        shared_value.value = value
        self.update_plot_multi_core(shared_value.value)
    

MainApp().run()
