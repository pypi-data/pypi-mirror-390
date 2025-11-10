import numpy as np
from .cfar import cfar
import matplotlib.pyplot as plt
import scipy.io as io
import cv2
from PIL import Image

def run(input, output_RT, output_VT):
    """
    雷达距离-多普勒成像处理
    
    Args:
        input: 输入的.mat文件路径
        output_RT: Range-Time输出图像路径
        output_VT: Velocity-Time输出图像路径
    """
    adcData = io.loadmat(input)
    adcData = adcData['adcData']
    # adcData = np.load('adcData.mat')
    num_ADCSamples = 256
    num_chirps = 64
    num_frame = 32

    adcData_T0 = adcData[0: 8: 1, :]
    # adcData_T0 = adcData[0 : 7 : 2, :]
    # adcData_T1 = adcData[2 : 8 : 2, :]

    data = np.zeros((1, num_chirps * num_ADCSamples * num_frame), dtype=complex)
    for k in range(4):
        data += adcData_T0[2*k, :]

    data_frame = np.zeros((num_chirps, num_ADCSamples, num_frame), dtype=complex)
    for k in range(num_frame):
        for m in range(num_chirps):
            data_frame[m, :, k] = data[0, num_chirps * num_ADCSamples * k +
                                        m * num_ADCSamples: num_chirps * num_ADCSamples * k + (m + 1) * num_ADCSamples]

    # MTI
    num_mti = num_chirps - 2
    data_mti = np.zeros((num_mti, num_ADCSamples, num_frame), dtype=complex)
    for k in range(num_frame):
        for m in range(num_mti):
            data_mti[m, :, k] = data_frame[m, :, k] - data_frame[m + 2, :, k]

    # 二维FFT
    data_fft = np.zeros((num_mti, num_ADCSamples, num_frame), dtype=complex)
    for k in range(num_frame):
        # for m in range(num_mti):
        data_fft[:, :, k] = np.fft.fftshift(np.fft.fft2(data_mti[:, :, k]))

    # CFAR
    num_R = 32
    num_V = 32
    TH_cfar = np.zeros((num_mti, num_ADCSamples, num_frame), dtype=complex)
    data_RD = np.zeros((num_V, num_R, num_frame), dtype=complex)
    RT = np.zeros((num_R, num_frame), dtype=complex)
    VT = np.zeros((num_V, num_frame), dtype=complex)

    for k in range(num_frame):
        for m in range(num_mti):
            TH_cfar[m, :, k] = cfar(abs(data_fft[m, :, k]))
        data_cfar = (TH_cfar < abs(data_fft)) * abs(data_fft)

        data_RD[:, :, k] = data_cfar[int(32 - num_V / 2): int(32 + num_V / 2), 128: 128 + num_R, k]
        x0, y0 = np.where(data_RD[:, :, k] == np.max(np.max(data_RD[:, :, k])))

        tmp = data_RD[x0[0], :, k].T
        tmp = tmp / (np.max(tmp) + np.finfo(float).eps)
        RT[:, k] = tmp

        tmp = data_RD[:, y0[0], k].T
        tmp = tmp / (np.max(tmp) + np.finfo(float).eps)
        VT[:, k] = tmp

    # RT_32 = cv2.resize(abs(RT), (32, 32))
    RT_resized = cv2.resize(abs(RT), (32, 32))
    # 将数据归一化到 0-255 范围并保存为灰度图
    RT_normalized = ((RT_resized - RT_resized.min()) / (RT_resized.max() - RT_resized.min()) * 255).astype(np.uint8)
    cv2.imwrite(output_RT, RT_normalized)

    # VT_32 = cv2.resize(abs(VT), (32, 32))
    VT_resized = cv2.resize(abs(VT), (32, 32))
    # 将数据归一化到 0-255 范围并保存为灰度图
    VT_normalized = ((VT_resized - VT_resized.min()) / (VT_resized.max() - VT_resized.min()) * 255).astype(np.uint8)
    cv2.imwrite(output_VT, VT_normalized)
