import numpy as np
from audiostream import get_output, AudioSample


class AudioPlayer:
    def __init__(self, channels, rate, buffer_size, fade_seq):
        super().__init__()
        self.rate = rate
        self.chunk_size = buffer_size
        self.fade_seq = fade_seq
        self.stream = get_output(
            channels=channels, rate=rate, buffersize=buffer_size, encoding=16)
        self.sample = AudioSample()
        print("AudioPlayer Chunksize ", self.chunk_size)
        print("Sampling Rate ", self.rate)
        self.chunk = None
        self.audio_data = np.zeros(0)
        self.audio_pos = 0
        self.pos = 0
        self.playing = False
        # self.smoother = Smoother(self.fade_seq)
        self.freq = 20

    def set_freq(self, freq):
        self.freq = freq

    def end(self):
        self.stop()
        del self.stream
        del self.sample

    @staticmethod
    def get_bytes(chunk):
        # chunk is scaled and converted from float32 to int16 bytes
        return (chunk * 32767).astype('int16').tobytes()
        # return (chunk * 32767).astype('int8').tobytes()

    def render_audio(self, pos):
        start = pos
        end = pos + self.chunk_size
        x_audio = np.arange(start, end) / self.rate
        return np.sin(2*np.pi*self.freq*x_audio)

    def fade_out(self, signal, length):
        amp_decrease = np.linspace(1, 0, length)
        return signal[-length:]*amp_decrease

    def run(self):
        self.sample = AudioSample()
        self.stream.add_sample(self.sample)
        self.sample.play()
        self.playing = True

        while self.playing:
            # smoothing
            # chunk = self.smoother.smooth_transition(
            # self.render_audio(self.pos))
            # self.smoother.buffer = chunk[-self.fade_seq:]
            self.chunk = self.render_audio(self.pos)
            np.concatenate(
                (self.audio_data, self.chunk),  axis=0)
            self.chunk = self.get_bytes(self.chunk)
            self.sample.write(self.chunk)
            self.pos += self.chunk_size

        # self.chunk = self.fade_out(self.render_audio(self.pos), 256)
        self.chunk = self.render_audio(self.pos)
        self.chunk_visible = self.chunk
        self.chunk = self.get_bytes(self.chunk)
        self.sample.write(self.chunk)
        self.sample.stop()
        self.audio_pos = self.pos
        self.pos = 0

    def stop(self):
        self.playing = False


class Smoother:
    def __init__(self, fade_seq):
        self.fade_seq = fade_seq
        self._buffer = np.zeros(fade_seq)
        self.coefficients = np.linspace(0, 1, fade_seq)
        self.coefficientsR = self.coefficients[::-1]

    @property
    def buffer(self):
        return self._buffer

    @buffer.setter
    def buffer(self, value):
        size_value = len(value)
        if size_value == self.fade_seq:
            self._buffer = value
        else:
            raise AttributeError("size of parameter {} doesn't fit size of buffer {}".format(
                size_value, self.fade_seq))

    def smooth_start(self, signal):
        start = signal[:self.fade_seq]
        smoothed_start = [a * b for a, b in zip(self.coefficients, start)]
        signal[:self.fade_seq] = smoothed_start
        return signal

    def smooth_end(self, signal):
        end = signal[-self.fade_seq:]
        smoothed_end = [a * b for a, b in zip(self.coefficientsR, end)]
        signal[-self.fade_seq:] = smoothed_end
        return signal

    # smooths transition between chunks to prevent discontinuities

    def smooth_transition(self, signal):
        buffer = [a * b for a, b in zip(self.coefficientsR, self.buffer)]
        # fade in
        signal[:self.fade_seq] = [a * b for a,
                                  b in zip(self.coefficients, signal[:self.fade_seq])]
        # add part from previous chunk
        signal[:self.fade_seq] += buffer
        return signal
