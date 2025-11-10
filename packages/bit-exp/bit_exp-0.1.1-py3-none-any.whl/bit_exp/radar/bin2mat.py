import numpy as np
import scipy.io as sio

def run(input, output):
    """
    将雷达原始二进制数据转换为MATLAB格式
    
    Args:
        input: 输入的.bin文件路径
        output: 输出的.mat文件路径
    
    Returns:
        output: 输出文件路径
    """
    num_ADCSamples = 256
    num_RX = 4

    fid = open(input, 'rb')
    adcData = np.fromfile(fid, dtype=np.int16)
    fid.close()
    filesize = adcData.size

    num_chirps = filesize // (2 * num_ADCSamples * num_RX)
    tmp = np.zeros((filesize // 2), dtype=complex)

    counter = 0
    for ii in range(0, filesize - 3, 4):
        tmp[counter] = adcData[ii] + 1j * adcData[ii + 2]
        tmp[counter + 1] = adcData[ii + 1] + 1j * adcData[ii + 3]
        counter += 2

    tmp = tmp.reshape(num_chirps, num_ADCSamples * num_RX)

    adcData = np.zeros((num_chirps * num_ADCSamples, num_RX), dtype=complex)
    for row in range(num_RX):
        for ii in range(num_chirps):
            adcData[(ii * num_ADCSamples):(ii + 1) * num_ADCSamples, row] = tmp[ii, (row * num_ADCSamples):(row + 1) * num_ADCSamples]

    tmp = adcData.T

    adcData = np.zeros((8, num_chirps // 2 * num_ADCSamples), dtype=complex)
    for ii in range(4):
        RxTx = tmp[ii, :].reshape(num_chirps, num_ADCSamples).T
        RxT1 = RxTx[:, :num_chirps:2]
        RxT2 = RxTx[:, 1::2]
        RxT1 = RxT1.T.reshape(1, num_chirps // 2 * num_ADCSamples)
        RxT2 = RxT2.T.reshape(1, num_chirps // 2 * num_ADCSamples)
        adcData[(ii * 2):(ii * 2 + 2), :] = np.vstack((RxT1, RxT2))
    adc_Data = {'adcData':adcData}
    # np.save('adcData', adcData)
    sio.savemat(output, adc_Data)
    return output
