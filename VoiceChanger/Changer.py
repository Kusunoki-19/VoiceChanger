import threading
import queue
import sys
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from test.test_buffer import numpy_array

class Changer():

    T_s = 1.0/4000 # サンプリング周期[s]
    F_s = 1 / T_s # サンプリング周波数[s^-1]
    N = 4000 #fftごとのデータ数
    T_fft = T_s * N #fft を行う周期[s]

    CHANNEL = 1 # チャンネル数（1固定）

    inVoiceQ = queue.Queue()
    outVoiceQ = queue.Queue()

    inSpects = np.fft.fft(inVoiceQ)
    outSpects = np.fft.fft(outVoiceQ)

    nowQCount = 0; #今のデータがT_fftの中の何のデータかします

    def __init__(self):


        self.inSpects = np.fft.fft(self.inVoiceQ)
        self.OutSpects = np.fft.fft(self.inVoiceQ)

        self.stream = sd.Stream(
            channels=self.CHANNEL,
            samplerate=self.F_s,
            callback=self.audioCallback
            )

        self.figInVoiceQ = plt.figure(0)
        aniInVoiceQ = FuncAnimation(
            self.figInVoiceQ,
            self.plotInVoiceQ,
            interval=self.T_fft,
            )


        with self.stream:
            plt.show()

    def plotInVoiceQ(self, frame):
        """ボイス波形を時間領域のグラフをプロット"""
        while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break

    def convertVoiceToSpects(self):
        """入ってきたマイクのデータを周波数解析して、返す"""
        self.inSpects = np.fft.fft(self.inVoiceQ)

    def filterSpects(self):
        """周波数特性を変換して、output(周波数領域)のデータ配列に入れる"""
        self.outSpects = self.inputSpects

    def convertSpectsToVoice(self):
        """周波数領域で変換された波形を時間領域に変換する"""

    def audioCallback2(self):
        """T_fftごとに呼ばれるコールバック関数"""

    def audioCallback(self, inVoice, outVoice, frames, time, status):
        """サンプリングごとに呼ばれるコールバック関数"""
        if status:
            print(status, file=sys.stderr) #error status

        self.inVoiceQ.put(inVoice)

        #T_fftのタイミング=T_sが一定回数のタイミングで、audioCallback2を呼び出す
        if int(time % self.T_fft) == 0:
            threadConvert = threading.Thread(target=self.audioCallback2)
            threadConvert.start()
        
        outVoice[:] = self.outVoiceQ[self.nowQCount]

if __name__ == '__main__':
    Changer()