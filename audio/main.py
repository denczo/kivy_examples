import threading
from kivy.app import App
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, LinePlot
import numpy as np

from tools import AudioPlayer

audio_data = []
audio_pos = 0


class MainApp(App):

    def build(self):
        self.app = MainGrid()
        return self.app

    def init_thread(self):
        self.playback_thread = threading.Thread(target=self.app.play_result)
        self.playback_thread.setDaemon(True)
        self.playback_thread.start()


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
        # Mono, Sampling Rate, Chunksize, Fade Sequence
        self.player = AudioPlayer(1, 44100, 512, 512)
        self.ids.modulation.add_widget(self.graph)
        self.plot_x = np.linspace(0, 1, self.samples)
        self.plot_y = np.zeros(self.samples)
        self.plot = LinePlot(color=[1, 1, 0, 1], line_width=1.5)
        self.graph.add_plot(self.plot)
        self.update_plot(1)

    def update_plot(self, freq):
        self.plot_y = np.sin(2*np.pi*freq*self.plot_x)
        self.plot.points = [(x, self.plot_y[x]) for x in range(self.samples)]

    def plot_audio(self):
        self.graph.xmax = self.player.audio_pos
        self.graph.x_ticks_major = 0
        print(self.player.audio_pos, self.player.audio_data.size)
        self.plot_y = self.player.audio_data
        self.plot.points = [(x, self.plot_y[x])
                            for x in range(self.player.audio_pos)]

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
            self.player.run()
        else:
            self.ids.play.text = '[b]PLAY[/b]'
            self.player.stop()
            print(audio_data)
            # self.plot_y = self.player.chunk_visible
            # print("SIZE", self.player.chunk_visible.size)
            # print(self.player.chunk_visible)
            # self.plot.points = [(x, self.plot_y[x])
            #                     for x in range(self.samples)]


MainApp().run()
