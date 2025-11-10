import numpy as np
import os
from typing import List, Tuple
from .audio_processor import AudioProcessor
from .fp_processor import FingerprintExtractor,FingerprintComparator
from .afp_config import AudioConfig
from .audio_utils import ffmpeg_load, get_audio_info
from scipy.signal import butter, lfilter
import time

''' 搜索一个音频在另一个音频中出现的位置'''
class AudioSearcher:
    """音频搜索类"""
    def __init__(self, audio_cfg=AudioConfig(), verbose=True):
        self.config = audio_cfg
        self.config.VERBOSE = verbose  # 添加打印控制开关
        self.max_duration = 36000 # 支持的最大音频时长,单位：秒
        self.config.GLOBAL_MAX_SHIFT = int(self.max_duration / self.config.FRM_DUR)
        self.audio_processor = AudioProcessor(self.config.OBJ_SR, self.config.FFT_SIZE, self.config.HOP_SIZE)
        self.fingerprint = FingerprintExtractor(self.config)
        self.comparator = FingerprintComparator(self.config)
    
    def log(self, message):
        """控制日志输出的辅助方法"""
        if self.config.VERBOSE:
            print(message)
            
    def search_audio(self, audio1_path: str, audio2_path: str) -> Tuple[float, bool]:
        """比较两个音频的指纹"""
        # 加载音频, 音频对齐只需要单通道音频
        audio1, _ = ffmpeg_load(audio_path=audio1_path, 
                                target_sr=self.config.OBJ_SR,
                                target_channels=1,
                                seg_start=self.config.START_DURATION,
                                seg_dur=self.config.MAX_DURATION)
        audio2, _ = ffmpeg_load(audio_path=audio2_path, 
                                target_sr=self.config.OBJ_SR,
                                target_channels=1,
                                seg_start=self.config.START_DURATION,
                                seg_dur=self.config.MAX_DURATION)

        st = time.time()

        # 计算指纹
        fp1, valid_mask1 = self.fingerprint.compute_fingerprint(audio1)
        fp2, valid_mask2 = self.fingerprint.compute_fingerprint(audio2)
        ct = time.time()
        # 寻找全局最佳对齐位置
        align_pos, hit_counts = self.comparator.find_best_alignment(fp1, fp2, self.config.GLOBAL_MAX_SHIFT)
        #self.log(f'Best alignment time ({-align_pos*self.config.FRM_DUR:.3f}s) hit_counts:{hit_counts}')
        at = time.time()

        if hit_counts < self.config.ALIGNED_HIT_THRES:
            self.log(f'hit_counts:{hit_counts}, can not alignment!')
            return [{"channel": 1, "align_pos": None}]
        else:
            return [{"channel": 1, "align_pos": -align_pos*self.config.FRM_DUR}]