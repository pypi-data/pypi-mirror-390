import numpy as np
import scipy.io as io
import matplotlib.pyplot as plt
import cv2

def run(input, output_FY, output_FW):
    """
    雷达角度-时间成像处理
    
    Args:
        input: 输入的.mat文件路径
        output_FY: Angle-Time俯仰角输出图像路径
        output_FW: Angle-Time方位角输出图像路径
    
    Returns:
        (output_FW, output_FY): 输出文件路径元组
    """
    adcData = io.loadmat(input)
    adcData = adcData['adcData']
    c = 3e8
    f0 = 77e9
    lamda = c / f0

    num_ADCSamples = 256
    num_chirps = 64
    num_frame = 32
    num_RX = 8

    data = np.zeros((num_RX, num_ADCSamples, num_chirps, num_frame), dtype=complex)
    for nn in range(num_RX):
        index = 0
        for ii in range(num_frame):
            for jj in range(num_chirps):
                data[nn, :, jj, ii] = adcData[nn, (index * num_ADCSamples):(index + 1) * num_ADCSamples]
                index += 1

    interval = 3
    num_MTI = num_chirps - interval  # 双脉冲对消间隔2
    data_MTI = np.zeros((num_RX, num_ADCSamples, num_MTI, num_frame), dtype=complex)
    for nn in range(num_RX):
        for ii in range(num_frame):
            for jj in range(num_MTI):
                data_MTI[nn, :, jj, ii] = data[nn, :, jj, ii] - data[nn, :, jj + interval, ii]

    d_base = 0.5 * lamda  # 基线长度

    # 方位角
    d = np.arange(0, 3 * d_base, d_base)
    space_num = 101
    angle = np.linspace(-50, 50, space_num)  # 用于存放幅度-角度曲线横轴
    Pmusic1 = np.zeros(space_num)  # 用于存放幅度-角度曲线
    Pmusic2 = np.zeros(space_num)  # 用于存放幅度-角度曲线
    Pmusic_mn = np.zeros((space_num, num_frame * num_MTI))  # 用于存放AT图

    index = 0  # 脉冲计数
    for ii in range(num_frame):  # 遍历32帧，分别求取每帧中间一个PRT的AT图
        for jj in range(num_MTI):
            Rxx = data_MTI[2:7:2, :, jj, ii] @ data_MTI[2:7:2, :, jj, ii].conj().T / num_ADCSamples  # 特征值分解
            D, EV = np.linalg.eig(Rxx)  # 特征值分解
            I = D.argsort()  # 将特征值排序从小到大
            EV = np.fliplr(EV[:, I])  # 对应特征矢量排序

            # 遍历每个角度，计算空间谱
            for iang in range(space_num):
                phim = np.deg2rad(angle[iang])
                a = np.exp(-1j * 2 * np.pi * d / lamda * np.sin(phim))
                En = EV[:, 1:]  # 取矩阵的第M+1到N列组成噪声子空间
                Pmusic1[iang] = 1 / abs(a.conj().T @ (En @ En.conj().T) @ a)

            Rxx = data_MTI[3:8:2, :, jj, ii] @ data_MTI[3:8:2, :, jj, ii].conj().T / num_ADCSamples  # 特征值分解
            D, EV = np.linalg.eig(Rxx)  # 特征值分解
            I = D.argsort()  # 将特征值排序从小到大
            EV = np.fliplr(EV[:, I])  # 对应特征矢量排序

            # 遍历每个角度，计算空间谱
            for iang in range(space_num):
                phim = np.deg2rad(angle[iang])
                a = np.exp(-1j * 2 * np.pi * d / lamda * np.sin(phim))
                En = EV[:, 1:]  # 取矩阵的第M+1到N列组成噪声子空间
                Pmusic2[iang] = 1 / abs(a.conj().T @ (En @ En.conj().T) @ a)
            index = index + 1
            Pmusic_abs = abs(Pmusic1 + Pmusic2)
            Pmmax = max(Pmusic_abs)
            Pmusic_mn[:, index-1] = ((Pmusic_abs / Pmmax)) # 归一化处理

    # 俯仰角
    d = np.arange(0, 4 * d_base, d_base)
    space_num = 91
    angle = np.linspace(-45, 45, space_num)  # 用于存放幅度-角度曲线横轴
    Pmusic = np.zeros(space_num)  # 用于存放幅度-角度曲线
    Pmusic_mmn = np.zeros((space_num, num_frame * num_MTI))  # 用于存放AT图

    index = 0  # 脉冲计数
    for ii in range(num_frame):  # 遍历32帧，分别求取每帧中间一个PRT的AT图
        for jj in range(num_MTI):
            Rxx = data_MTI[0:4, :, jj, ii] @ data_MTI[0:4, :, jj, ii].conj().T / num_ADCSamples  # 特征值分解
            D, EV = np.linalg.eig(Rxx)  # 特征值分解
            I = D.argsort()  # 将特征值排序从小到大
            EV = np.fliplr(EV[:, I])  # 对应特征矢量排序

            # 遍历每个角度，计算空间谱
            for iang in range(space_num):
                phim = np.deg2rad(angle[iang])
                a = np.exp(-1j * 2 * np.pi * d / lamda * np.sin(phim))
                En = EV[:, 1:]  # 取矩阵的第M+1到N列组成噪声子空间
                Pmusic[iang] = 1 / abs(a.conj().T @ (En @ En.conj().T) @ a)

            index = index + 1
            Pmusic_abs = abs(Pmusic)
            Pmmax = max(Pmusic_abs)
            Pmusic_mmn[:, index-1] = ((Pmusic_abs / Pmmax)) # 归一化处理

    AT_FW = cv2.resize(abs(Pmusic_mn), (32, 32))
    # 将数据归一化到 0-255 范围并保存为灰度图
    AT_FW_normalized = ((AT_FW - AT_FW.min()) / (AT_FW.max() - AT_FW.min()) * 255).astype(np.uint8)
    cv2.imwrite(output_FW, AT_FW_normalized)

    AT_FY = cv2.resize(abs(Pmusic_mmn), (32, 32))
    # 将数据归一化到 0-255 范围并保存为灰度图
    AT_FY_normalized = ((AT_FY - AT_FY.min()) / (AT_FY.max() - AT_FY.min()) * 255).astype(np.uint8)
    cv2.imwrite(output_FY, AT_FY_normalized)
    return output_FW, output_FY
