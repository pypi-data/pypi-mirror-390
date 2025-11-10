import os
import sys
import json
from .afp_config import AudioConfig
from .AudioSearcher import AudioSearcher
from .AudioComparator import AudioComparator
from .AudioSearchComparator import AudioSearchComparator
from pkg_resources import resource_filename  # 新增：用于获取包内文件路径

def compare_audio(ref_audio, com_audio, op_type=3, config_path=None, out_path='result.json', verbose=False):
    """
    音频差异比较函数

    参数:
        ref_audio (str): 参考音频文件路径
        com_audio (str): 对比音频文件路径
        op_type (int): 操作类型: 1=音频搜索, 2=音频内容差异对比, 3=音频内容+音量对比
        config_path (str): 配置文件路径
        out_path (str): 结果输出文件路径
        verbose (bool): 是否显示详细日志

    返回:
        dict: 比较结果字典，如果失败则返回None
    """
    # 加载配置文件
    audio_cfg = AudioConfig()
    if config_path is None:
        try:
            # 获取包内 config.json 的路径
            config_path = resource_filename('netease_audiodiff', 'config.json')
        except Exception as e:
            print(f"Error getting default config path: {e}")
            return None

    if os.path.exists(config_path):
        try:
            with open(config_path, 'rt', encoding='utf-8') as f:
                config = json.load(f)
            audio_cfg.update_config(config)
        except Exception as e:
            print(f"Error loading config file: {e}")
            print(f"Config path: {config_path}")  # 新增：打印实际读取的路径，方便排查
            return None
    else:
        print(f"Config file not found: {config_path}")
        return None

    print(f'参考音频:{ref_audio}')
    print(f'对比音频:{com_audio}')

    diff_res = None
    if op_type == 2:
        comparator = AudioComparator(audio_cfg, verbose=verbose)
        diff_res = comparator.compare_audio_diff(ref_audio, com_audio)
        if not diff_res:
            print(f"AudioComparator failed!")

    elif op_type == 1:
        searcher = AudioSearcher(audio_cfg, verbose=verbose)
        diff_res = searcher.search_audio(ref_audio, com_audio)
        if not diff_res:
            print(f"AudioSearcher failed!")
    elif op_type == 3:
        comparator = AudioSearchComparator(audio_cfg, verbose=verbose)
        diff_res = comparator.compare_audio_diff(ref_audio, com_audio)
        if not diff_res:
            print(f"AudioSearchComparator failed!")
    else:
        print("Invalid type")
        return None

    # 结果输出到json
    try:
        with open(out_path, 'wt', encoding='utf-8') as f:
            json.dump(diff_res, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error writing result file: {e}")
        return None

    return diff_res


# 保留命令行调用方式（可选）
def main():
    import argparse
    parser = argparse.ArgumentParser(description='音频差异比较工具')
    parser.add_argument('ref_audio', help='参考音频文件路径')
    parser.add_argument('com_audio', help='对比音频文件路径')
    parser.add_argument('--type', '-t', type=int, default=1,
                        help='操作类型: 1=音频搜索, 2=音频内容差异对比 3=音频内容+音量对比')
    parser.add_argument('--config', '-c', default='config.json', help='配置文件路径')
    parser.add_argument('--out', '-o', default='result.json', help='结果输出文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')

    args = parser.parse_args()
    compare_audio(
        ref_audio=args.ref_audio,
        com_audio=args.com_audio,
        op_type=args.type,
        config_path=args.config,
        out_path=args.out,
        verbose=args.verbose
    )


if __name__ == "__main__":
    #main()
    compare_audio('recorded_audio.wav', 'recorded_audio2.wav', op_type=3, config_path='config.json', out_path='result.json', verbose=False)

