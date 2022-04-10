import numpy as np
from audiostream import get_output, AudioSample


class AudioPlayer:
    def __init__(self, channels=1, rate=22050, buffer_size=1024, fade_seq=256):
        super().__init__()
        self.rate = rate
        self.chunk_size = buffer_size+fade_seq
        self.fade_seq = fade_seq
        self.stream = get_output(
            channels=channels, rate=rate, buffersize=buffer_size, encoding=16)
        self.sample = AudioSample()
        print("AudioPlayer Chunksize ", self.chunk_size)
        print("Sampling Rate ", self.rate)
        self.chunk = None
        self.pos = 0
        self.playing = False
        self.smoother = Smoother(self.fade_seq)
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
        end = pos + (self.chunk_size + self.fade_seq)
        x_audio = np.arange(start, end) / self.rate
        return np.sin(2*np.pi*self.freq*x_audio)

    def run(self):
        self.sample = AudioSample()
        self.stream.add_sample(self.sample)
        self.sample.play()
        self.playing = True

        while self.playing:
            # smoothing
            chunk = self.smoother.smooth_transition(
                self.render_audio(self.pos))
            self.smoother.buffer = chunk[-self.fade_seq:]
            chunk = self.get_bytes(chunk[:self.chunk_size])
            self.sample.write(chunk)
            self.pos += self.chunk_size
            if not self.playing:
                self.sample.stop()

    def stop(self):
        self.playing = False
        self.sample.stop()
        self.pos = 0


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

    # smooths transition between chunks to prevent discontinuities
    def smooth_transition(self, signal):
        buffer = [a * b for a, b in zip(self.coefficientsR, self.buffer)]
        # fade in
        signal[:self.fade_seq] = [a * b for a,
                                  b in zip(self.coefficients, signal[:self.fade_seq])]
        # add part from previous chunk
        signal[:self.fade_seq] += buffer
        return signal
