import numpy as np
import os
from typing import List, Tuple
from audio_processor import AudioProcessor
from fp_processor import FingerprintExtractor,FingerprintComparator
from afp_config import AudioConfig
from audio_utils import ffmpeg_load, get_audio_info
from scipy.signal import butter, lfilter
import time

class AudioSearchComparator:
    """音频比较类"""
    def __init__(self, audio_cfg=AudioConfig(), verbose=True):
        self.config = audio_cfg
        self.config.VERBOSE = verbose  # 添加打印控制开关
        self.audio_processor = AudioProcessor(self.config.OBJ_SR, self.config.FFT_SIZE, self.config.HOP_SIZE)
        self.fingerprint = FingerprintExtractor(self.config)
        self.comparator = FingerprintComparator(self.config)
    
    def log(self, message):
        """控制日志输出的辅助方法"""
        if self.config.VERBOSE:
            print(message)

    # 检测音量是否忽大忽小
    def check_vol_diff(self, audio1, audio2, align_pos, 
                         threshold_db=-20, frame_length_ms=500, 
                         hop_length_ms=250):
        """
        比较两个音频的音量波动差异
        
        参数:
        audio1 -- 参考音频 (numpy数组)
        audio2 -- 待比较音频 (numpy数组)
        align_pos -- audio2中的对齐位置 (样本数)
        sr -- 采样率 (Hz)
        threshold_db -- 音量差异阈值 (dB)
        frame_length_ms -- 帧长度 (毫秒)
        hop_length_ms -- 帧移 (毫秒)
        
        返回:
        differences -- 超过阈值的帧信息列表，每个元素为元组(时间位置, 音量差异dB)
        """
        
        # 1. 根据对齐位置截取audio2的对比段
        start_index = max(0, align_pos)
        end_index = min(len(audio2), align_pos + len(audio1))
        audio2_segment = audio2[start_index:end_index]
        
        # 确保两个音频长度相同
        min_length = min(len(audio1), len(audio2_segment))
        audio1 = audio1[:min_length]
        audio2_segment = audio2_segment[:min_length]
        
        # 2. 去除直流偏置
        audio1 = audio1 - np.mean(audio1)
        audio2_segment = audio2_segment - np.mean(audio2_segment)
        
        # 3. 音量规整
        rms1 = np.sqrt(np.mean(audio1 ** 2))
        rms2 = np.sqrt(np.mean(audio2_segment ** 2))
        scaling_factor = rms1 / (rms2 + 1e-8)  # 防止除以零
        audio2_segment = audio2_segment * scaling_factor
          
        # 4. 分帧处理并计算音量差异
        frame_length = int(frame_length_ms * self.config.OBJ_SR / 1000)
        hop_length = int(hop_length_ms * self.config.OBJ_SR / 1000)
        n_frames = int((min_length - frame_length) / hop_length) + 1
        
        differences = []
        
        for i in range(n_frames):
            start = i * hop_length
            end = start + frame_length
            
            # 提取当前帧
            frame1 = audio1[start:end]
            frame2 = audio2_segment[start:end]
            
            # 计算帧的RMS值
            rms_frame1 = np.sqrt(np.mean(frame1 ** 2))
            rms_frame2 = np.sqrt(np.mean(frame2 ** 2))
            
            rms_diff = abs(rms_frame1 - rms_frame2)

            # 转换为分贝值差异
            db_diff = 20 * np.log10(rms_diff + 1e-8)  # 防止log(0)
            
            # 记录超过阈值的差异
            if db_diff > threshold_db:
                #time_position = (start + end) / (2 * self.config.OBJ_SR)  # 帧中心时间位置
                differences.append((start, end))

        
        # 5. 合并相邻的differences段
        merged_diffs = []
        if differences:
            prev_start, prev_end = differences[0]
            for current_start, current_end in differences[1:]:
                if current_start - prev_end <= hop_length:
                    # 合并当前差异与前一个差异
                    prev_end = current_end
                else:
                    # 前一个差异不连续，保留
                    merged_diffs.append((int(prev_start*self.config.SAMPLE_TO_MS), 
                                        int((prev_start+align_pos)*self.config.SAMPLE_TO_MS), 
                                        int((prev_end - prev_start)*self.config.SAMPLE_TO_MS)))
                    prev_start, prev_end = current_start, current_end
            # 处理最后一个差异
            merged_diffs.append((int(prev_start*self.config.SAMPLE_TO_MS), 
                                int((prev_start+align_pos)*self.config.SAMPLE_TO_MS), 
                                int((prev_end - prev_start)*self.config.SAMPLE_TO_MS)))
        
        return merged_diffs
        
    def check_content_diff(self, fp1, fp2, mask1, mask2, align_pos):
        """检测中间段差异
        Args:
            fp1: 第一个音频指纹
            fp2: 第二个音频指纹
            mask1: 第一个音频有效比特位mask
            mask2: 第二个音频有效比特位mask
            align_pos: 全局对齐位置
        Returns:
            msg: 差异信息
            diff_segs: 差异段列表
            fp2_idx: 更新后的fp2索引位置
            fp1_idx: 更新后的fp1索引位置
        """
        diff_segs = []
        fragments = []
        msg = ""
        
        # 中间段检测，分段重新对齐并校验出中间差异段
        have_diff_mid = False
        #fp1_idx = 0
        if align_pos > 0:
            fp2_idx = 0
            fp1_idx = align_pos
        else:
            fp2_idx = -align_pos
            fp1_idx = 0
        
        while fp1_idx < (fp1.shape[0]-self.config.ALIGN_SEG_FRMS) and fp2_idx < (fp2.shape[0]-self.config.ALIGN_SEG_FRMS):
            # 分段对齐:
            fp1_seg = np.copy(fp1[fp1_idx:fp1_idx+self.config.ALIGN_SEG_FRMS])
            mask1_seg = np.copy(mask1[:,fp1_idx:fp1_idx+self.config.ALIGN_SEG_FRMS])

            fp2_seg = np.copy(fp2[fp2_idx:fp2_idx+self.config.ALIGN_SEG_FRMS])
            mask2_seg = np.copy(mask2[:, fp2_idx:fp2_idx+self.config.ALIGN_SEG_FRMS])

            cur_align_pos,seg_ber = self.comparator.find_best_alignment_by_ber(fp1_seg, fp2_seg, None, None, self.config.SEG_MAX_SHIFT)
            fragments.append({'refPos':int(fp1_idx*self.config.FRM_DUR_MS), 'pos':int(fp2_idx*self.config.FRM_DUR_MS),'cons':int((1-seg_ber)*1000)/1000})
            # self.log(f'f1_pos:{fp1_idx*self.config.FRM_DUR} f2_pos:{fp2_idx*self.config.FRM_DUR} cur_align_pos:{cur_align_pos} seg_ber:{seg_ber}')
            
            # 仅检测中间段f2是否有缺失，首尾单独检测
            if fp1_idx > 0 and fp1_idx < (fp1.shape[0]-self.config.ALIGN_SEG_FRMS):
                if cur_align_pos > self.config.MIN_SEG_FRMS:
                    have_diff_mid = True
                    diff_segs.append((int(fp1_idx*self.config.FRM_DUR_MS),
                                    int(fp2_idx*self.config.FRM_DUR_MS), 
                                    int(cur_align_pos*self.config.FRM_DUR_MS)))

            # 根据片段对齐结果对比指纹差异
            fp1_aligned_seg, fp2_aligned_seg, m1_aligned_seg, m2_aligned_seg = self.comparator.fetch_compare_seg(fp1_seg, fp2_seg, cur_align_pos, mask1_seg, mask2_seg)
            cur_diff_segs = self.comparator.find_diff_segments_ber(fp1_aligned_seg, fp2_aligned_seg, m1_aligned_seg, m2_aligned_seg, min_diff_frames=self.config.MIN_SEG_FRMS, window_size=self.config.SMOOTH_FRMS)
            for start, end in cur_diff_segs:
                have_diff_mid = True
                diff_segs.append((int((start+fp1_idx)*self.config.FRM_DUR_MS), 
                                int((start+fp2_idx)*self.config.FRM_DUR_MS), 
                                int((end-start)*self.config.FRM_DUR_MS))) 

            if fp1_idx == 0 and align_pos > 0 and align_pos < self.config.ALIGN_SEG_FRMS:
                fp2_idx += self.config.ALIGN_SEG_FRMS - align_pos - cur_align_pos
            else:
                fp2_idx += self.config.ALIGN_SEG_FRMS - cur_align_pos

            fp1_idx += self.config.ALIGN_SEG_FRMS
        
        if have_diff_mid:
            msg = f'|音频内容有差异'
            
        return msg, diff_segs, fp1_idx, fp2_idx, fragments 

    # 多通道音频差异对比
    def compare_audio_diff(self, ref_audio_path: str, com_audio_path: str):
        # 检测音频是否存在
        if not os.path.exists(ref_audio_path) or not os.path.exists(com_audio_path):
            self.log('input file is not exists!')
            return None

        # 对比通道数是否一致
        audio1_info = get_audio_info(ref_audio_path)
        audio2_info = get_audio_info(com_audio_path)

        if audio1_info['channels'] != audio2_info['channels']:
            self.log('channels mismatch:{}!={}'.format(audio1_info['channels'],audio2_info['channels']))
            return None

        compare_channels = audio1_info['channels']
        # 每个通道分别对比
        # 加载音频
        audio1, _ = ffmpeg_load(audio_path=ref_audio_path,
                                target_sr=self.config.OBJ_SR,
                                seg_start=self.config.START_DURATION,
                                seg_dur=self.config.MAX_DURATION)
        audio2, _ = ffmpeg_load(audio_path=com_audio_path, 
                                target_sr=self.config.OBJ_SR,
                                seg_start=self.config.START_DURATION,
                                seg_dur=self.config.MAX_DURATION)
        
        if compare_channels > 1:
            channels_res = []
            for channel in range(compare_channels):
                cur_res = self.compare_mono_audio_diff(audio1[channel], audio2[channel])
                cur_chan_res = {"channel": channel, "align_pos": cur_res[0], "result": cur_res[1]}
                #self.log(f'compare channel {channel}, result:{cur_res}')
                channels_res.append(cur_chan_res)
                if self.config.CHECK_MONO:
                    break
            return channels_res
        else:
            cur_res = self.compare_mono_audio_diff(audio1[channel], audio2[channel])
            return [{"channel": 1, "align_pos": cur_res[0], "result": cur_res[1]}]

    def compare_mono_audio_diff(self, ref_audio: str, com_audio: str) -> Tuple[float, List[Tuple[float, float]], str]:
        """比较两个音频的差异"""        

        # 计算指纹
        fp1, mask1 = self.fingerprint.compute_fingerprint(ref_audio)
        fp2, mask2 = self.fingerprint.compute_fingerprint(com_audio)
        
        # 寻找全局最佳对齐位置
        align_pos, hit_counts = self.comparator.find_best_alignment(fp2, fp1[:self.config.GLOBAL_ALIGN_USE_FRMS], self.config.GLOBAL_MAX_SHIFT)
        #self.log(f'Best alignment time ({align_pos*self.config.FRM_DUR:.3f}s) hit_counts:{hit_counts}')
        
        if hit_counts < self.config.ALIGNED_HIT_THRES:
            self.log(f'hit_counts:{hit_counts}, can not alignment!')
            return None, [{'msg': '无法对齐'}]

            
        # 能够对齐，则寻找差异段
        all_diffs = []
        
        # 目标段 - 内容一致性检测
        mid_msg, mid_diff_segs, fp1_idx, fp2_idx, fragments = self.check_content_diff(fp1, fp2, mask1, mask2, -align_pos)
        if mid_diff_segs:
            all_diffs.append({'msg': '内容一致性存在差异', 'diff_segs': mid_diff_segs})

        
        # 目标段 - 音量一致性检测
        vol_diff_segs = self.check_vol_diff(ref_audio, com_audio, align_pos*self.config.HOP_SIZE, self.config.VOL_DB_DIFF_THRES)
        if vol_diff_segs:
            all_diffs.append({'msg': '音量存在忽大忽小', 'diff_segs': vol_diff_segs})

        
        return align_pos*self.config.FRM_DUR_MS, all_diffs
