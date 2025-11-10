#!/usr/bin/env python
"""
bit_exp命令行工具统一入口

提供各个实验模块的命令行接口：
- bit_radar: 雷达信号处理工具
"""

import sys
import argparse


def radar_main():
    """雷达信号处理命令行工具入口"""
    from bit_exp.radar import process_folder
    
    parser = argparse.ArgumentParser(
        description='雷达信号处理工具 - 将雷达原始数据转换为处理后的图像',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个文件
  bit_radar input.bin output_folder
  
  # 处理整个文件夹
  bit_radar raw_data/ output_folder
  
  # 指定输出模式
  bit_radar raw_data/ output_folder --mode eval
        """
    )
    
    parser.add_argument('input', help='输入文件(.bin)或文件夹路径')
    parser.add_argument('output', help='输出文件夹路径')
    parser.add_argument(
        '--mode', 
        choices=['eval', 'predict', 'train'],
        default='eval',
        help='输出模式: eval(评估), predict(预测), train(训练) (默认: eval)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='bit_exp 0.1.0'
    )
    
    args = parser.parse_args()
    
    try:
        print(f"开始处理雷达数据...")
        print(f"输入: {args.input}")
        print(f"输出: {args.output}")
        print(f"模式: {args.mode}")
        
        process_folder(args.input, args.output, args.mode)
        
        print("处理完成!")
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


# 未来可以添加更多实验的命令行工具
# def exp2_main():
#     """其他实验的命令行工具入口"""
#     pass


if __name__ == '__main__':
    # 当直接运行cli.py时，显示帮助信息
    print("请使用以下命令:")
    print("  bit_radar - 雷达信号处理工具")
    print("\n使用 'bit_radar --help' 查看详细帮助")
