import threading
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
from DataStructures import NumpyRingBaffer

class Changer():
    #帯域制限周波数[s^-1] (この周波数以上はカットという周波数,本来はアナログフィルタでカット),
    #人間の可聴域は20kHzらしいが、処理が重くなったので現段階では2.5kHz
    F_m = 2.5*1000
    #サンプリング周波数[s^-1],
    #サンプリング定理よりT_s > 2 F_sのひつようがあるので、ぎりのサンプリング周波数(ナイキスト周波数)にする
    F_s = 2 * F_m
    #スペクトル周期[ras/s], 周波数特性の周期
    #OMEGA_s = 2 * PI * F_s
    #サンプリング周期[s]
    T_s = 1 / F_s
    #fftごとのデータ数, 現在は2.5kHzの時のindata長になってる(適当)
    N = 144*100
    #チャンネル数（1固定）
    CHANNEL = 1

    samplingCount = 0

    BAFFER_LEN = 10*N

    #リングQの定義。inQはマイク入力、outQは出力
    waveIn  = NumpyRingBaffer.NumpyRingBaffer(BAFFER_LEN, 3*N, 3*N) #dataLen, rear, front
    waveOut = NumpyRingBaffer.NumpyRingBaffer(BAFFER_LEN, 3*N, 1*N)

    #グラフに関する変数
    WAVE_GRAPH_VAL_NUM = waveIn.length
    fig = plt.figure(figsize=(10,6))
    plt.subplots_adjust(wspace=0.6, hspace=0.4) # 余白を設定
    waveX = np.arange(0, WAVE_GRAPH_VAL_NUM , 1)
    freqX = np.fft.fftfreq(N, d=T_s)
    freqIn = np.fft.fft(np.zeros((N, 1)))
    freqOut = np.fft.fft(np.zeros((N, 1)))
    axs = [] #各グラフ
    axs.append(fig.add_subplot(221 + 0)) #波(input)
    axs.append(fig.add_subplot(221 + 2)) #波(output)
    axs.append(fig.add_subplot(221 + 1)) #周波数特性(input)
    axs.append(fig.add_subplot(221 + 3)) #周波数特性(output)
    axs.append(fig.add_subplot(221 + 0)) #inQ front
    axs.append(fig.add_subplot(221 + 2)) #outQ Reqr
    axs.append(fig.add_subplot(221 + 0)) #inQ convert領域
    axs.append(fig.add_subplot(221 + 2)) #outQ converted領域

    lines = [] #各ラインオブジェクト
    for i in [0,1]:#波形
        lines.append(
            axs[i].plot(waveX,[0] * len(waveX),"blue")[0])
    for i in [2,3]:#周波数応答
        lines.append(
            axs[i].plot(freqX[0:int(N/2)],[0] * int(N/2),"blue")[0])
    for i in [4,5]:#indata, outdata
        lines.append(
            axs[i].plot([0,0],[-1,1],"red")[0])
    for i in [6,7]:#convert area
        lines.append(
            axs[i].plot([0,0],[-1,1],"green")[0])


    def __init__(self):

        self.stream = sd.Stream(
            channels=self.CHANNEL,
            samplerate=self.F_s,
            callback=self.audioCallback)

        self.aniInQ = FuncAnimation(
            self.fig,
            self.plotGraphs,
            init_func=self.initGraphs,
            interval=self.T_s,
            blit=True)

        with self.stream:
            plt.show()

    def initGraphs(self):
        #個別グラフ設定
        self.axs[0].set_title("Input Voice Wave")
        self.axs[1].set_title("output Voice Wave")
        self.axs[2].set_title("Input Freqency Response")
        self.axs[3].set_title("output Freqency Response")
        #波形グラフ共通設定
        for i in [0,1]:
            self.axs[i].set_ylim(-1,1)
            self.axs[i].set_xlim(0,self.WAVE_GRAPH_VAL_NUM)
            self.axs[i].set_xlabel("data index[-]")
            self.axs[i].set_ylabel("digital value[-]")
        #周波数特性グラフ共通設定
        for i in [2,3]:
            self.axs[i].set_ylim(-0.1,0.25)
            self.axs[i].set_xlim(0, max(self.freqX))
            self.axs[i].set_xlabel("Freqency[rad/s]")
            self.axs[i].set_ylabel("Amplipude[-]")
        return self.lines

    def plotGraphs(self,count):
        #波(input) inQ
        self.lines[0].set_ydata(self.waveIn.q)
        self.lines[4].set_xdata([self.waveIn.rear]*2)
        self.lines[6].set_xdata([self.waveIn.front]*2)

        #波(output) outQ
        self.lines[1].set_ydata(self.waveOut.q)
        self.lines[5].set_xdata([self.waveOut.front]*2)
        self.lines[7].set_xdata([self.waveOut.rear]*2)

        #周波数特性(input),(output)をプロ ット
        self.lines[2].set_ydata(np.abs(self.freqIn[0:int(self.N/2)]))
        self.lines[3].set_ydata(np.abs(self.freqOut[0:int(self.N/2)]))
        return self.lines


    def convertWave(self, convertData):
        #波(input)        →周波数特性(input)
        self.freqIn = np.fft.fft(convertData)
        #周波数特性(input) →周波数特性(output) : filtering
        self.freqOut = self.freqIn.copy()
#         self.freqOut[((self.freqX < 0)&(self.freqX > self.F_m))] = 0 + 0j
        self.freqOut[((self.freqX < 0)&(self.freqX > 100))] = 0 + 0j
        self.freqOut = self.freqOut * 10
        #周波数特性(output)→波(output)
        convertedData = np.fft.ifft(self.freqOut).real
        return convertedData

    def audioCallback2(self):
        """T_fftごとに呼ばれるコールバック関数"""
        #変換するデータの取り出し
        convertData = self.waveIn.deque(self.N)
        #データの変換
        convertedData = self.convertWave(convertData)
        #変換したデータを出力Qに追加
        self.waveOut.enque(convertedData)

    def audioCallback(self, indata, outdata, frames, time, status):
        """複数のサンプリングごと呼ばれるコールバック関数"""
        """
        indata : np.array, サンプリングの結果を行ベクトルとして保持
        outdata : 出力に使う行ベクトル, indata と同じ長さと思われる
        """
        self.samplingCount += indata.shape[0]
        #リングQに追加
        self.waveIn.enque(indata)
        #リングQから取り出し
        outdata[:] = self.waveOut.deque(indata.shape[0])
        #T_fftのタイミング>=T_sが一定回数のタイミングで、audioCallback2を呼び出す
        if self.samplingCount >= self.N:
            threadConvert = threading.Thread(target=self.audioCallback2)
            threadConvert.start()
            self.samplingCount = self.samplingCount % self.N

#         print("sampling : %d"%(self.samplingCount))
#         print(outdata.reshape((1,208)))
#         print(indata.shape)
#         print(outdata.shape)



if __name__ == '__main__':
    Changer()