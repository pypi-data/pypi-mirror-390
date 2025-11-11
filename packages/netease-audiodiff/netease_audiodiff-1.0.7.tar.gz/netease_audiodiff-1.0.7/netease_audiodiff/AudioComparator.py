import numpy as np
import os
from typing import List, Tuple
from .audio_processor import AudioProcessor
from .fp_processor import FingerprintExtractor,FingerprintComparator
from .afp_config import AudioConfig
from .audio_utils import ffmpeg_load, get_audio_info
from scipy.signal import butter, lfilter
import time

""" 对比两个音频的内容差异 """
class AudioComparator:
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

    def check_head(self, audio1, audio2, align_pos):
        msg = ""
        diff_segs = []
        # 开头位置检测
        if align_pos > 0:
            check_seg = audio1[0:align_pos*self.config.HOP_SIZE]
            check_seg_energy = self.audio_processor.compute_frame_max_energy(check_seg)
            if check_seg_energy > self.config.SIL_ENERGY_THRES:
                diff_segs.append((0,int(align_pos*self.config.FRM_DUR_MS),int(align_pos*self.config.FRM_DUR_MS)))
                msg += f'头部内容缺失:{align_pos*self.config.FRM_DUR_MS}ms'
        elif align_pos < 0:
            check_seg = audio2[0:-align_pos*self.config.HOP_SIZE]
            check_seg_energy = self.audio_processor.compute_frame_max_energy(check_seg)
            if check_seg_energy > self.config.SIL_ENERGY_THRES:
                diff_segs.append((0,0,int(-align_pos*self.config.FRM_DUR_MS)))
                msg += f'头部内容多余:{-align_pos*self.config.FRM_DUR_MS}ms'
        return msg,diff_segs

    def check_middle(self, fp1, fp2, mask1, mask2, align_pos):
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
        #fp2_idx = max(0, -align_pos)
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
        
        # # 位置退移一个ALIGN_SEG_FRMS，方便尾部校验
        # fp2_idx -= self.config.ALIGN_SEG_FRMS
        
        if have_diff_mid:
            msg = f'|中间内容有差异'
            
        return msg, diff_segs, fp1_idx, fp2_idx, fragments 

    def check_tail(self, audio1, audio2, fp1, fp2, m1, m2, fp1_idx, fp2_idx, min_diff_frames):
        msg = ""
        diff_segs = []
        # print(f'fp1_idx:{fp1_idx} fp2_idx:{fp2_idx} fp1.shape[0]:{fp1.shape[0]} fp2.shape[0]:{fp2.shape[0]}')
        # print(f'fp1_rest:{fp1.shape[0]-fp1_idx} fp2_rest:{fp2.shape[0]-fp2_idx} ')
        # 结尾位置检测
        fp1_end_seg,fp2_end_seg,m1_end_seg,m2_end_seg = self.comparator.fetch_compare_seg(np.copy(fp1[fp1_idx:fp1_idx+self.config.ALIGN_SEG_FRMS]), np.copy(fp2[fp2_idx:]), 0, np.copy(m1[:,fp1_idx:fp1_idx+self.config.ALIGN_SEG_FRMS]), np.copy(m2[:,fp2_idx:]))
        fp_check_len = len(fp1_end_seg)
        # print(f'fp_check_len:{fp_check_len}')
        # check_middle已经覆盖了这一段的检测，这里不再重复
        cur_diff_segs = self.comparator.find_diff_segments_ber(fp1_end_seg, fp2_end_seg, m1_end_seg,m2_end_seg, min_diff_frames, min_diff_frames)
        for start, end in cur_diff_segs:
            msg = "|结尾内容不一致"
            diff_segs.append(((start+fp1_idx)*self.config.FRM_DUR_MS,
                            (start+fp2_idx)*self.config.FRM_DUR_MS, 
                            (end-start)*self.config.FRM_DUR_MS))
        if (fp1.shape[0]-fp1_idx) < (fp2.shape[0]-fp2_idx):
            check_seg = np.copy(audio2[(fp2_idx+fp_check_len)*self.config.HOP_SIZE:])
            check_seg_energy = self.audio_processor.compute_frame_max_energy(check_seg)
            #print(f'seg_len:{len(check_seg)} check_seg_energy:{check_seg_energy}')
            if check_seg_energy > self.config.SIL_ENERGY_THRES:
                # 检测尾音淡出
                is_fade_out = self.detect_fade_out(check_seg)
                if is_fade_out and len(check_seg) < self.config.FADE_MAX_SAMPLES:
                    msg += f'|结尾多余淡出效果:{int(len(check_seg)*1000/self.config.OBJ_SR)}ms'
                else:
                    diff_segs.append((fp1.shape[0]*self.config.FRM_DUR_MS, 
                                    (fp2_idx+fp_check_len)*self.config.FRM_DUR_MS, 
                                    (fp2.shape[0]-fp2_idx-fp_check_len)*self.config.FRM_DUR_MS))
                    msg += f'|结尾内容多余:{int(len(check_seg)*1000/self.config.OBJ_SR)}ms'
        elif (fp1.shape[0]-fp1_idx) > (fp2.shape[0]-fp2_idx):
            check_seg = np.copy(audio1[(fp1_idx+fp_check_len)*self.config.HOP_SIZE:])
            check_seg_energy = self.audio_processor.compute_frame_max_energy(check_seg)
            calc_activate_frms = self.audio_processor.compute_active_frms(check_seg, self.config.SIL_ENERGY_THRES)
            #print(f'check_pos:{(fp1_idx+fp_check_len)*self.config.FRM_DUR} check_seg_energy:{check_seg_energy} calc_activate_frms:{calc_activate_frms}')
            if check_seg_energy > self.config.SIL_ENERGY_THRES:
                # 检测尾音淡出
                is_fade_out = self.detect_fade_out(check_seg)
                if is_fade_out and calc_activate_frms < self.config.FADE_LOST_FRMS:
                    msg += f'|结尾缺少淡出效果:{int(len(check_seg)*1000/self.config.OBJ_SR)}ms'
                else:
                    diff_segs.append(((fp1_idx+fp_check_len)*self.config.FRM_DUR_MS, 
                                    fp2.shape[0]*self.config.FRM_DUR_MS, 
                                    (fp1.shape[0]-fp1_idx-fp_check_len)*self.config.FRM_DUR_MS))
                    msg += f'|结尾内容缺失:{int(len(check_seg)*1000/self.config.OBJ_SR)}ms'
        
        return msg, diff_segs
        
    def detect_fade_out(self, audio_segment):
        """检测音频片段是否存在淡出效果
        
        Args:
            audio_segment: 音频片段数据
            
        Returns:
            bool: 是否存在淡出效果
        """
        if len(audio_segment) < self.config.OBJ_SR * self.config.FADE_DETECT_DUR:  # 至少需要0.5秒才能检测淡出
            return False
            
        # 将音频分成若干帧
        frame_size = self.config.FFT_SIZE #int(0.05 * self.config.OBJ_SR)  # 50ms帧
        hop_size = self.config.HOP_SIZE #int(0.025 * self.config.OBJ_SR)   # 25ms步长
        
        frames = []
        for i in range(0, len(audio_segment) - frame_size, hop_size):
            frames.append(audio_segment[i:i+frame_size])
            
        if len(frames) < 5:  # 至少需要5帧才能检测淡出
            return False
            
        # 计算每帧的能量
        energies = [np.sum(np.abs(frame)**2) for frame in frames]

        # 根据能量检测是否存在多段有声段
        sound_segments = []
        current_segment = []
        for i, energy in enumerate(energies):
            if energy > 1e-6:  # 能量超过阈值，认为有声段
                current_segment.append(i)
            elif current_segment and (i - current_segment[-1]) > 5:  # 能量低于阈值，认为有声段结束
                sound_segments.append(current_segment)
                current_segment = []
        
        if current_segment:
            sound_segments.append(current_segment)

        #print(f'sound_segments:{sound_segments}')
        # 检测是否存在多段有声段
        if len(sound_segments) != 1:
            return False

        # 取最后一段检测淡出
        last_segment = sound_segments[-1]
        if len(last_segment) < 5:  # 最后一段有声段太短
            return False

        # 取最后一段的能量
        last_energies = [energies[i] for i in last_segment]
        # # 去除尾部能量为0的帧
        # while energies and energies[-1] == 0:
        #     energies.pop()
        
        # 计算能量的下降趋势
        if np.std(last_energies) < 1e-6:  # 能量几乎不变
            return False
            
        # 归一化能量
        last_energies = np.array(last_energies) / np.max(last_energies)
        #print(f'energies:{last_energies}')
        
        # 计算后半部分能量的下降趋势
        x_last = np.arange(len(last_energies))
        
        # 使用多项式拟合
        try:
            coeffs = np.polyfit(x_last, last_energies, 1)
            half_pos = len(last_energies) // 2
            left_energies = np.mean(last_energies[0:half_pos])
            right_energies = np.mean(last_energies[half_pos:])
            #print(f'coeffs:{coeffs}')
            slope = coeffs[0]
                
            # 检查是否存在明显的能量下降
            energy_ratio = right_energies / left_energies
            #print(f'energy_ratio:{energy_ratio}')
            if slope < 0 and energy_ratio < self.config.FADE_ENERGY_RATIO_THRES:  # 能量下降超过70%
                return True
        except:
            return False
            
        return False

    # 多通道结果的合并
    def combina_channel_res(self, channels_res):
        # 若多个通道都有对齐位置，仅返回通道1的对齐位置
        # 若多个通道都有异常段，返回异常最多的通道
        align_pos = None
        diff_segs = []
        message = ""
        fragments = []
        for align,diffs,msg,frags in channels_res:
            if align != None and align_pos == None:
                align_pos = align
                fragments = frags
            if align == None and msg != "":
                message = msg
            if len(diffs) > len(diff_segs):
                diff_segs = diffs
                message = msg
        return align_pos, diff_segs, message, fragments

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

    def compare_mono_audio_diff(self, audio1: str, audio2: str) -> Tuple[float, List[Tuple[float, float]], str]:
        """比较两个音频的差异"""        
        # st = time.time()
        # 计算指纹
        fp1, mask1 = self.fingerprint.compute_fingerprint(audio1)
        fp2, mask2 = self.fingerprint.compute_fingerprint(audio2)
        
        # ct = time.time()
        
        # 寻找全局最佳对齐位置
        align_pos, hit_counts = self.comparator.find_best_alignment(fp1, fp2[:self.config.GLOBAL_ALIGN_USE_FRMS], self.config.GLOBAL_MAX_SHIFT)
        #self.log(f'Best alignment time ({align_pos*self.config.FRM_DUR:.3f}s) hit_counts:{hit_counts}')
        
        # at = time.time()
        
        if hit_counts < self.config.ALIGNED_HIT_THRES:
            self.log(f'hit_counts:{hit_counts}, can not alignment!')
            return None, [{'msg': '无法对齐'}]
            
        # 能够对齐，则寻找差异段
        all_diffs = []
        diff_segs = []
        msg = ""
        
        # 开头位置检测
        msg, diff_segs = self.check_head(audio1, audio2, align_pos)

        # 中间段检测
        mid_msg, mid_diff_segs, fp1_idx, fp2_idx, fragments = self.check_middle(fp1, fp2, mask1, mask2, align_pos)
        msg += mid_msg
        diff_segs += mid_diff_segs

        # 结尾位置检测
        tail_msg, tail_diff_segs = self.check_tail(audio1, audio2, fp1, fp2, mask1, mask2, fp1_idx, fp2_idx, self.config.MIN_SEG_FRMS)
        msg += tail_msg
        diff_segs += tail_diff_segs

        all_diffs.append({'msg': msg, 'diff_segs': diff_segs})
        
        # dt = time.time()
        # self.log(f'cost:{(dt-st):.3f} afp_time={(ct-st):.3f} align_time={(at-ct):.3f} find_diff_time={(dt-at):.3f}')
        
        return -align_pos*self.config.FRM_DUR_MS, all_diffs