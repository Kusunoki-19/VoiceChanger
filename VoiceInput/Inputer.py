import queue
import sys
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from test.test_buffer import numpy_array

class VoiceChanger():

    T_s = 1.0/4000 # サンプリング周期[s]
    DATA_LEN_BY_A_fft = 100 #fftごとのデータ数
    T_fft = T_s * DATA_LEN_BY_A_fft #fft を行う感覚[s]

    F_s = 1 / T_s # サンプリング周波数[s^-1]
    CHANNEL = 1 # チャンネル数（1固定）

    inVoiceQ = np.zeros(DATA_LEN_BY_A_fft)
    outVoiceQ = np.zeros(DATA_LEN_BY_A_fft)

    inputSpects = np.fft.fft(inVoiceQ)
    outSpects = np.fft.fft(outVoiceQ)

    nowQCount = int(0); #今のデータがT_fftの中の何のデータかします

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

        #self.figInSpects = plt.figure(1)
        #self.figOutVoiceQ = plt.figure(3)
        #self.figOutSpects = plt.figure(4)
#         aniInSpects = FuncAnimation(
#             self.figInSpects,
#             self.plotInSpects,
#             interval=self.T_fft
#             )
#
#         aniOutVoiceQ = FuncAnimation(
#             self.figOutVoiceQ,
#             self.plotOutVoiceQ,
#             interval=self.T_fft
#             )
#
#         aniOutSpects = FuncAnimation(
#             self.figOutSpects,
#             self.plotOutSpects,
#             interval=self.T_fft
#             )


        with self.stream:
            plt.show()

    def plotInVoiceQ(self, frame):
        """ボイス波形を時間領域のグラフをプロット"""
        plt.cla()
        plt.plot(np.arange(self.DATA_LEN_BY_A_fft),self.inVoiceQ)

#     def plotInSpects(self ,frame):
#         """周波数解析した振幅特性と、位相特性のグラフをプロット"""
#         plt.plot(np.arange(self.DATA_LEN_BY_A_fft),self.inSpects)
#
#     def plotOutVoiceQ(self ,frame):
#         """ボイス波形を時間領域のグラフをプロット"""
#         plt.plot(np.arange(self.DATA_LEN_BY_A_fft),self.outVoiceQ)
#
#     def plotOutSpects(self ,frame):
#         """周波数解析した振幅特性と、位相特性のグラフをプロット"""
#         plt.plot(np.arange(self.DATA_LEN_BY_A_fft),self.outSpects)


    def convertVoiceToSpects(self):
        """入ってきたマイクのデータを周波数解析して、返す"""
        self.inSpects = np.fft.fft(self.inVoiceQ)

    def filterSpects(self):
        """周波数特性を変換して、output(周波数領域)のデータ配列に入れる"""
        self.outSpects = self.inputSpects

    def convertSpectsToVoice(self):
        """周波数領域で変換された波形を時間領域に変換する"""

    def audioCallback2(self,inVoice):
        """T_fftごとに呼ばれるコールバック関数"""
        #fft -> filter -> fft^-1
        #self.convertVoiceToSpects()
        #self.filterSpects()
        #self.convertSpectsToVoice()

        #データプロット
#         self.plotInSpects()
#         self.plotOutVoiceQ()
#         self.plotOutSpects()


    def audioCallback(self, inVoice, outVoice, frames, time, status):
        """サンプリングごとに呼ばれるコールバック関数"""
        if status:
            print(status, file=sys.stderr) #error status

        self.inVoiceQ[self.nowQCount] = inVoice[0]
        self.nowQCount += 1

        #T_fftのタイミング=T_sが一定回数のタイミングで、audioCallback2を呼び出す
        if (self.nowQCount >= self.DATA_LEN_BY_A_fft):
            self.audioCallback2(inVoice)
            self.nowQCount = 0

        outVoice[:] = self.outVoiceQ[self.nowQCount]

if __name__ == '__main__':
    VoiceChanger()