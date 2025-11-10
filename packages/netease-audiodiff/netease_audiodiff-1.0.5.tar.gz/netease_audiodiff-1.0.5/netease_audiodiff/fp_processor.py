import numpy as np
from typing import List, Tuple
from .afp_config import AudioConfig
import librosa

class FingerprintExtractor:
    """音频指纹提取类"""
    def __init__(self, config: AudioConfig):
        self.config = config
        
    def compute_fingerprint(self, audio: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """计算音频指纹"""
        frame_size = self.config.FFT_SIZE
        hop_length = self.config.HOP_SIZE
        
        #padded_audio = np.pad(audio, (frame_size, frame_size), mode='constant')
        window = np.hamming(frame_size)
        stft = librosa.stft(audio, n_fft=frame_size, hop_length=hop_length, window=window)
        mag = np.abs(stft)
        mag = mag / np.max(mag)
        
        freq_bins = np.floor(np.array(self.config.BARK_FREQS) * frame_size / self.config.OBJ_SR).astype(int)
        freq_bins = np.clip(freq_bins, 0, frame_size // 2)
        
        subbands = np.array([
            mag[freq_bins[i]:freq_bins[i+1]].sum(axis=0) 
            for i in range(len(freq_bins)-1)
        ])
        
        subband_diffs = subbands[:-1] - subbands[1:]
        time_diffs = subband_diffs[:, 1:] - subband_diffs[:, :-1]
        
        # pad_frames = frame_size // hop_length
        # time_diffs = time_diffs[:, pad_frames:-pad_frames]
        
        binary_fp = (time_diffs > self.config.FP_QUANT_THRES).astype(np.int8)
        powers = 1 << np.arange(binary_fp.shape[0], dtype=np.int64)

        # 计算特征状态mask
        abs_time_diffs = np.abs(time_diffs)
        binary_fp_ex = np.zeros_like(time_diffs, dtype=np.int8)
        binary_fp_ex[(abs_time_diffs < self.config.FP_QUANT_THRES_UPPER) & (abs_time_diffs > self.config.FP_QUANT_THRES_LOWER)] = -1  # 小于阈值的绝对值为特殊状态-1
        valid_mask = (binary_fp_ex != -1)

        return (binary_fp * powers[:, None]).sum(axis=0), valid_mask

class FingerprintComparator:
    """指纹比较类"""
    def __init__(self, config: AudioConfig):
        self.config = config
        
    def calc_ber(self, fp1: np.ndarray, fp2: np.ndarray, mask1: np.ndarray = None, mask2: np.ndarray = None) -> np.ndarray:
        """
        计算整数指纹的bit error rate
        
        Args:
            fp1: 第一个指纹序列
            fp2: 第二个指纹序列
            mask1: 第一个指纹的掩码，True表示有效位
            mask2: 第二个指纹的掩码，True表示有效位
            
        Returns:
            每帧的比特错误率
        """
        xor_result = fp1 ^ fp2
        
        # 如果没有提供掩码，则所有位都参与计算
        if mask1 is None or mask2 is None:
            bit_errors = np.array([bin(x).count('1') for x in xor_result])
            return bit_errors / self.config.BIT_NUM
        
        # 计算有效位掩码（两个掩码的交集）
        valid_mask = mask1 & mask2
        
        # 使用向量化操作计算每帧的有效位数
        valid_bits_count = np.sum(valid_mask, axis=0)
        
        # 避免除以零
        valid_bits_count = np.maximum(valid_bits_count, 1)
        
        # 预分配结果数组
        bit_errors = np.zeros(len(xor_result), dtype=np.int64)
        
        # 使用位操作和查表法计算错误位数
        for i, x in enumerate(xor_result):
            # 获取当前帧的有效位掩码
            frame_mask = valid_mask[:, i]
            
            # 如果没有有效位，跳过计算
            if np.sum(frame_mask) == 0:
                continue
                
            # 使用位操作计算错误位
            error_count = 0
            for j in range(self.config.BIT_NUM):
                # 检查第j位是否为1（错误）且在掩码中为True（有效）
                if (x & (1 << j)) and j < len(frame_mask) and frame_mask[j]:
                    error_count += 1
            
            bit_errors[i] = error_count
        
        # 返回每帧的比特错误率
        return bit_errors / valid_bits_count
    
    def fetch_compare_seg(self, fp1: np.ndarray, fp2: np.ndarray, shift: int, mask1: np.ndarray, mask2: np.ndarray):
        """获取对比片段"""
        if shift > 0:
            fp1 = fp1[shift:]
            fp2 = fp2[:fp1.shape[0]]
            if mask1 is not None and mask2 is not None:
                mask1 = mask1[:, shift:]
                mask2 = mask2[:, :fp1.shape[0]]
        else:
            fp2 = fp2[-shift:]
            fp1 = fp1[:fp2.shape[0]]
            if mask1 is not None and mask2 is not None:
                mask2 = mask2[:, -shift:]
                mask1 = mask1[:, :fp2.shape[0]]
        
        compare_fp_len = min(fp1.shape[0], fp2.shape[0])

        if mask1 is not None and mask2 is not None:
            return fp1[:compare_fp_len], fp2[:compare_fp_len], mask1[:,:compare_fp_len], mask2[:,:compare_fp_len]
        else:
            return fp1[:compare_fp_len], fp2[:compare_fp_len], None, None
    
    # fp2 对齐到 fp1的最佳对齐位置
    def find_best_alignment(self, fp1_int: np.ndarray, fp2_int: np.ndarray, max_shift: int) -> int:
        """找到两个指纹序列的最佳对齐位置"""
        # 使用numpy的unique和searchsorted进行快速匹配
        unique_patterns, fp1_positions = np.unique(fp1_int, return_inverse=True)
        #print(f'fp1_int:{fp1_int.shape} unique_patterns:{unique_patterns} fp1_positions:{fp1_positions}')
        pattern_positions = [[] for _ in range(len(unique_patterns))]
        for pos, pattern_idx in enumerate(fp1_positions):
            pattern_positions[pattern_idx].append(pos)
        
        # 统计时间差（使用字典的get方法避免重复检查）
        shift_counts = {}
        for t2, pattern in enumerate(fp2_int):
            idx = np.searchsorted(unique_patterns, pattern)
            if idx < len(unique_patterns) and unique_patterns[idx] == pattern:
                for t1 in pattern_positions[idx]:
                    shift = t1 - t2
                    if abs(shift) <= max_shift:
                        shift_counts[shift] = shift_counts.get(shift, 0) + 1
        
        # 找到最佳shift
        if not shift_counts:
            return 0, 1.0
        
        best_shift,best_counts = max(shift_counts.items(), key=lambda x: x[1])
        #print(f'best_shift:{best_shift} best_counts:{best_counts}')
        
        return best_shift, best_counts

    def find_best_alignment_by_ber(self, fp1: np.ndarray, fp2: np.ndarray, mask1: np.ndarray, mask2: np.ndarray, max_shift: int = 200) -> Tuple[int, float]:
        """使用BER均值找到最佳对齐位置"""
        if len(fp1) == 0 or len(fp2) == 0:
            return 0, 0
            
        min_ber = float('inf')
        best_shift = 0
        
        for shift in range(-max_shift, max_shift + 1):
            fp1_aligned, fp2_aligned, m1_aligned, m2_aligned = self.fetch_compare_seg(fp1, fp2, shift, mask1, mask2)
            if len(fp1_aligned) < 10:
                continue
                
            cur_ber = self.calc_ber(fp1_aligned, fp2_aligned, m1_aligned, m2_aligned).mean()
            
            if cur_ber < min_ber:
                min_ber = cur_ber
                best_shift = shift
                
        return best_shift, min_ber
    
    def find_diff_segments_ber(self, fp1: np.ndarray, fp2: np.ndarray,
                          mask1: np.ndarray, mask2: np.ndarray,
                          min_diff_frames: int = 5,
                          window_size: int = 10) -> List[Tuple[float, float]]:
        """查找指纹差异段"""
        ber = self.calc_ber(fp1, fp2, mask1, mask2)
        segments = []
        start_frame = None
        half_win_size = window_size//2
        
        for i in range(0, len(ber)-half_win_size):
            window_ber = np.mean(ber[max(0,i-half_win_size):i+half_win_size+1])
            
            if window_ber > self.config.BER_SEG_THRES:
                if start_frame is None:
                    start_frame = i
            elif start_frame is not None:
                if i - start_frame > min_diff_frames:
                    segments.append((start_frame, i))
                    #print(f'{start_frame} {i} ber:{ber[start_frame:i]}')
                start_frame = None
        
        if start_frame is not None and len(ber) - start_frame > min_diff_frames:
            segments.append((start_frame, len(ber)))
        
        return segments
