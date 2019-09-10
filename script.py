import pandas
import time
import numpy as np
from numpy import arange
import math
import statistics

EUT = context.connection.EUT
EUT2 = context.connection.EUT2

logger.info("電流制御・周波数特性")

measuring_time = 30      #測定時間
#電流制御用_目標周波数
'''
target_freq_list = [20, 25, 40, 50, 80, 100, 125, 200, 250, 400, 500, 625, 1000]
'''
#速度制御用_目標周波数

target_freq_list = [2, 4, 5, 8, 10, 16, 20, 25, 40, 50, 80, 100, 125, 200, 250, 400, 500, 625, 1000]

#start_freq = 2.0         #開始周波数
#stop_freq = 50.0         #終了周波数
#step_freq = 2.0          #周波数のステップ間隔
target_amp = 1.0        #振幅
sampling_rate = 10000    #サンプリング周波数
num_data = 100000 - 5000 #サンプル数
freq = sampling_rate / num_data * np.arange(0, num_data)

def getdata(): #UNINET経由でデータをとる
    import urllib
    import json

    HOST_URL = "192.168.0.218"
    HOST_PORT = 8080

    with urllib.request.urlopen("http://%s:%d/data"%(HOST_URL, HOST_PORT)) as res:
        data = res.read().decode("utf-8")
        return json.loads(data)

def getparam(): #UNINET経由のデータを項目ごとに分ける
    global getdata

    data = getdata()
    CUT_OFF = -5000

    index = data["WriteIndex"]
    aRef = data["ARef"][0]
    aRef = (aRef[index:]+aRef[:index])[:CUT_OFF]

    pos = data["Positions"][0]
    pos = (pos[index:]+pos[:index])[:CUT_OFF]

    acc = data["Acc"][0]
    acc = (acc[index:]+acc[:index])[:CUT_OFF]

    posH = data["PosH"][0]
    posH = (posH[index:]+posH[:index])[:CUT_OFF]

    posL = data["PosL"][0]
    posL = (posL[index:]+posL[:index])[:CUT_OFF]

    trq = data["Torques"][0]
    trq = (trq[index:]+trq[:index])[:CUT_OFF]

    gen = data["General"][0]
    gen = (gen[index:]+gen[:index])[:CUT_OFF]

    speed = data["Speeds"][0]
    speed = (speed[index:]+speed[:index])[:CUT_OFF]

    return posL, speed
    #return gen

def e_notation(num): #指数表記に変換
    i = 0

    if num > 0:
        while ((num < 1) or (num >= 10)):
            if num >= 10:
                num /= 10
                i += 1
            else:
                num *=10
                i -= 1
        #while (not num.is_integer()):
        #    num *= 10
        #    i -= 1
    else:
        num = 0
    return num, i      

def sendparam(com, span, freq, amp): #測定用のパラメータを送る
    global e_notation

    logger.info(f"測定時間 = {span}")
    uniservo.usv_command(com, f"CHIRPT1 {span}") #時間設定

    logger.info(f"周波数 = {freq}")
    e_freq = e_notation(freq)
    uniservo.usv_command(com, f"CHIRPF0 {e_freq[0]} {e_freq[1]}") #開始周波数
    uniservo.usv_command(com, f"CHIRPF1 {e_freq[0]} {e_freq[1]}") #終了周波数

    logger.info(f"振幅 = {amp}")
    e_amp = e_notation(amp)
    uniservo.usv_command(com, f"CHIRPGA {e_amp[0]} {e_amp[1]}") #振幅

freq_list = []
amp_list = []

for i in range(3):
    logger.info(f"測定 {i} 回目")
    for target_freq in target_freq_list:
        time.sleep(1)

        #80A_電流制御帯域(500Hz)
        
        uniservo.usv_command(EUT,"KTN 3.183 -1")
        uniservo.usv_command(EUT,"JMN 9.4 -6")
        uniservo.usv_command(EUT,"KPDQ 3.735 1")
        #uniservo.usv_command(EUT,"KPDQ 5.104 1")
        uniservo.usv_command(EUT,"KIDQ 6.708 4")
        #uniservo.usv_command(EUT,"KIDQ 1.237 5")
        
        #200ギアなし_電流制御帯域(500Hz)
        '''
        uniservo.usv_command(EUT,"KTN 5.15 -1")
        uniservo.usv_command(EUT,"JMN 1.75 -5")
        uniservo.usv_command(EUT,"KPDQ 4.715 1")
        uniservo.usv_command(EUT,"KIDQ 7.963 4")
        '''
        #200ギアなし_電流制御帯域(300Hz)
        '''
        uniservo.usv_command(EUT,"KTN 5.15 -1")
        uniservo.usv_command(EUT,"JMN 1.75 -5")
        uniservo.usv_command(EUT,"KPDQ 2.872 1")
        uniservo.usv_command(EUT,"KIDQ 3.049 4")
        '''
        #電流制御用コマンド
        '''
        uniservo.usv_command(EUT,"CTM 5")
        uniservo.usv_command(EUT,"TGTQ 0")
        uniservo.usv_command(EUT,"AOMD A4 0 1.0")
        '''
        #速度制御用コマンド
        
        uniservo.usv_command(EUT,"CTM 1")
        uniservo.usv_command(EUT,"TGTV 0")
        uniservo.usv_command(EUT,"KPSPD 5 4")
        #uniservo.usv_command(EUT,"OBSSPDL 1 -1")
        #uniservo.usv_command(EUT,"OBSSPDU 2 -1")
        #uniservo.usv_command(EUT,"CHIRPOFS 2 0")
        #uniservo.usv_command(EUT,"OBSSEL 1")
        #uniservo.usv_command(EUT,"KFG 1 -1")
        
        #トルク制御用コマンド
        '''
        uniservo.usv_command(EUT,"CTM 3")
        uniservo.usv_command(EUT,"TGTT 0")
        uniservo.usv_command(EUT,"KPTRQ 1 4")    
        '''
        sendparam(EUT, measuring_time, target_freq, target_amp)
        #sendparam(EUT, measuring_time, 2, target_amp)

        uniservo.usv_command(EUT, "SV 1")
        uniservo.usv_command(EUT, "CHIRPEN 1")
        time.sleep(15)
        data = getparam()        
        time.sleep(20)
        uniservo.usv_command(EUT, "SV 0")
        
        #yf = np.fft.fft(data)
        yf = np.fft.fft(data[1])
        for j in range(num_data):
            #if ((freq[j] > 2 + 10) and (freq[j] < sampling_rate - 2 - 10)):
            if ((freq[j] > target_freq + 10) and (freq[j] < sampling_rate - target_freq - 10)):
                yf[j] = 0
        z = np.fft.ifft(yf)
        z_real = z.real
        
        cnt = 0
        cycle_num = int(sampling_rate / target_freq)
        #cycle_num = int(sampling_rate / 2)
        cycle_list = [0] * cycle_num
        qi_max_list = []
        qi_min_list = []
        for k in range(cycle_num * 10):
            if cnt == (cycle_num - 1):
                cycle_list[cnt] = z_real[k]
                qi_max_list.append(max(cycle_list))
                qi_min_list.append(min(cycle_list))
                cnt = 0
            else:
                cycle_list[cnt] = z_real[k]
                cnt += 1
        
        #電流orトルク制御用_振幅
        '''
        data_amp = (statistics.median(qi_max_list) - statistics.median(qi_min_list)) / 2
        '''
        #速度制御用_振幅（rad/s）
        
        data_amp = (statistics.median(qi_max_list) - statistics.median(qi_min_list)) * math.pi / 1048576 * sampling_rate
        

        logger.info(f"data_amp = {data_amp}")
        
        freq_list.append(target_freq)
        amp_list.append(data_amp)
'''
df = pandas.DataFrame({ "posL":data[0],
                        "speed":data[1],
                        #"z_real":z_real,
                        })
'''

df = pandas.DataFrame({ "freq":freq_list,
                        "amplitude":amp_list,
                        })

if context is not None and "output_dir" in context:
    df.to_csv(os.path.join(context.output_dir, "data.csv"))
logger.info(df)