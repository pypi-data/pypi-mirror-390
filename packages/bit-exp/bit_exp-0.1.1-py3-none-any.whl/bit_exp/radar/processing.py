import os
from . import bin2mat
from . import ATimaging
from . import RDimaging
import multiprocessing


def process_data(input_bin, output_dir, id=0):
    """
    处理单个雷达数据文件
    
    Args:
        input_bin: 输入的.bin文件路径
        output_dir: 输出目录
        id: 文件标识符
    
    Returns:
        (RT_path, VT_path, AT_FW_path, AT_FY_path): 输出文件路径元组
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Create subdirectories for each output type
    os.makedirs(os.path.join(output_dir, 'RT'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'VT'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'AT_FW'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'AT_FY'), exist_ok=True)

    mat_path = os.path.join(output_dir, f'{id}_adc_data.mat')
    bin2mat_output = bin2mat(input_bin, mat_path)
    RT_path = os.path.join(output_dir, f'RT/{id}RT.jpg')
    VT_path = os.path.join(output_dir, f'VT/{id}VT.jpg')
    RDimaging.run(bin2mat_output, RT_path, VT_path)
    AT_FW_path = os.path.join(output_dir, f'AT_FW/{id}AT_FW.jpg')
    AT_FY_path = os.path.join(output_dir, f'AT_FY/{id}AT_FY.jpg')
    ATimaging.run(bin2mat_output, AT_FY_path, AT_FW_path)
    # 删除mat
    os.remove(mat_path)
    return RT_path, VT_path, AT_FW_path, AT_FY_path


def process_folder(input_path, output_folder, output_mode="eval"):
    """
    批量处理文件夹中的雷达数据
    
    Args:
        input_path: 输入路径（文件或文件夹）
        output_folder: 输出文件夹
        output_mode: 输出模式，可选 "eval", "predict", "train"
    """
    if output_mode not in ["eval", "predict", "train"]:
        raise ValueError("Invalid output_mode. Choose from 'eval', 'predict', 'train'.")
    
    if os.path.isdir(input_path):
        processes = []
        for filename in os.listdir(input_path):
            if filename.endswith('.bin'):
                try:
                    direction = filename[:2]
                    id = filename.split('_')[0][2:]
                    if not id:
                        id = '0'
                    id = int(id)
                    input_bin = os.path.join(input_path, filename)
                    if output_mode in ["eval", "train"]:
                        output_dir = os.path.join(output_folder, direction)
                    else:
                        output_dir = output_folder
                    p = multiprocessing.Process(target=process_data, args=(input_bin, output_dir, direction+'_'+str(id)))
                    p.daemon = True
                    p.start()
                    processes.append(p)
                except Exception as e:
                    print("Error processing", filename, ":", e)
        for p in processes:
            p.join()
    else:
        process_data(input_path, output_folder)
