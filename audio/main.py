import threading
from kivy.app import App
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, LinePlot
import numpy as np

from tools import AudioPlayer


class MainApp(App):

    def build(self):
        self.app = MainGrid()
        return self.app

    def init_thread(self):
        self.playback_thread = threading.Thread(target=self.app.player.run)
        # daemon threads don't wait for main thread
        self.playback_thread.setDaemon(True)
        self.playback_thread.start()
        print("Playback Thread", self.playback_thread.native_id, "started")
        print("Main Thread", threading.main_thread().native_id)

    def exit_thread(self):
        self.playback_thread.join()
        print("Playback Thread", self.playback_thread.native_id, "stopped")

class MainGrid(BoxLayout):

    zoom = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.samples = 512
        self.zoom = 1
        self.graph = Graph(y_ticks_major=0.5,
                           x_ticks_major=64,
                           border_color=[0, 1, 1, 1],
                           tick_color=[0, 1, 1, 0.7],
                           x_grid=True, y_grid=True,
                           xmin=0, xmax=self.samples,
                           ymin=-1.0, ymax=1.0,
                           draw_border=False,
                           x_grid_label=True, y_grid_label=False)
        # Mono, Sampling Rate, Chunksize
        self.player = AudioPlayer(1, 44100, self.samples)
        self.ids.modulation.add_widget(self.graph)
        self.plot_x = np.linspace(0, 1, self.samples)
        self.plot_y = np.zeros(self.samples)
        self.plot = LinePlot(color=[1, 1, 0, 1], line_width=1.5)
        self.old_freq = 0
        self.freq = 0
        # adds plot to the graph widget
        self.graph.add_plot(self.plot)
        self.update_plot(1)

    def update_plot(self, freq):
        self.plot_y = np.sin(2*np.pi*freq*self.plot_x)
        # draws plot
        self.plot.points = [(x, self.plot_y[x]) for x in range(self.samples)]

    def update_zoom(self, value):
        if value == '+' and self.zoom < 8:
            self.zoom *= 2
            self.graph.x_ticks_major /= 2
        elif value == '-' and self.zoom > 1:
            self.zoom /= 2
            self.graph.x_ticks_major *= 2

    def play_result(self):
        if self.ids.play.state == 'down':
            self.ids.play.text = '[b]STOP[/b]'
            App.get_running_app().init_thread()
        else:
            self.ids.play.text = '[b]PLAY[/b]'
            self.player.stop()
            App.get_running_app().exit_thread()


MainApp().run()
