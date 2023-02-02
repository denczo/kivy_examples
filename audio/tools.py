import numpy as np
from audiostream import get_output, AudioSample


class AudioPlayer:
    def __init__(self, channels, rate, chunk_size):
        super().__init__()
        self.rate = rate
        self.chunk_size = chunk_size
        # initialize the engine and get an output device; can be initialized only once
        self.stream = get_output(
            channels=channels, rate=rate, buffersize=chunk_size, encoding=16)
        # create instance of AudioSample to handle the audio stream (output) e.g. play and stop
        self.sample = AudioSample()
        self.chunk = np.zeros(chunk_size)
        # indicator
        self.pos = 0
        self.playing = False
        self.freq = 20
        self.old_freq = self.freq

    def set_freq(self, freq):
        self.old_freq = self.freq
        self.freq = freq
   
    def render_audio(self, pos, freq):
        start = pos
        end = pos + self.chunk_size
        x_audio = np.arange(start, end) / self.rate
        return np.sin(2*np.pi*freq*x_audio)

    def fade_out(self, signal, length):
        amp_decrease = np.linspace(1, 0, length)
        signal[-length:] *= amp_decrease
        return signal

    @staticmethod
    def get_bytes(chunk):
        # chunk is scaled and converted from float32 to int16 bytes
        return (chunk * 32767).astype('int16').tobytes()
    
    def write_audio_data(self):
        self.chunk = self.get_bytes(self.chunk)
        # write bytes of chunk to internal ring buffer
        self.sample.write(self.chunk)

    def run(self):
        self.stream.add_sample(self.sample)
        self.sample.play()
        self.playing = True
        self.pos = 0
        self.freq_change = False

        while self.playing:
            self.chunk = self.render_audio(self.pos, self.old_freq)
            self.pos += self.chunk_size
            
            if self.freq != self.old_freq:
                self.chunk = self.fade_out(self.chunk, 256)
                self.pos = 0
                self.old_freq = self.freq
                
            self.write_audio_data()

        # self.chunk = self.fade_out(
        #     self.render_audio(self.pos, self.old_freq), 256)
        # self.write_audio_data()
        # important for threading otherwise a new thread cannot be initialized
        self.sample.stop()

    def stop(self):
        self.playing = False
