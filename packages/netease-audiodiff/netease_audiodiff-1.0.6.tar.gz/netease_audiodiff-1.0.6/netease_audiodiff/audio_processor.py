import scipy.signal
import numpy as np

class AudioProcessor:
    """音频处理类"""
    def __init__(self, audio_sr: int, fft_size: int, hop_size: int):
        self.audio_sr = audio_sr
        self.fft_size = fft_size
        self.hop_size = hop_size
        
    def high_pass_filter(self, audio: np.ndarray, cutoff_freq: float = 100.0) -> np.ndarray:
        """对音频进行高通滤波"""
        nyquist = self.audio_sr / 2
        normal_cutoff = cutoff_freq / nyquist
        b, a = scipy.signal.butter(6, normal_cutoff, btype='high', analog=False)
        return scipy.signal.filtfilt(b, a, audio)
    
    def compute_frame_max_energy(self, audio: np.ndarray) -> float:
        """计算音频的帧最大能量（时域）"""
        if len(audio) < self.fft_size:
            return 0
            
        audio = self.high_pass_filter(audio)
        n_frames = 1 + (len(audio) - self.fft_size) // self.hop_size
        if n_frames <= 0:
            return 0
        
        frame_energy = np.zeros(n_frames)
        for i in range(n_frames):
            start = i * self.hop_size
            end = start + self.fft_size
            frame = audio[start:end]
            frame_energy[i] = np.sum(frame * frame)
        
        return np.max(frame_energy)

    def compute_active_frms(self, audio: np.ndarray, threshold: float) -> float:
        """计算音频中的活动帧"""
        activate_frames = 0

        if len(audio) < self.fft_size:
            return 0
            
        audio = self.high_pass_filter(audio)
        n_frames = 1 + (len(audio) - self.fft_size) // self.hop_size
        if n_frames <= 0:
            return 0

        for i in range(n_frames):
            start = i * self.hop_size
            end = start + self.fft_size
            frame = audio[start:end]
            cur_frame_energy = np.sum(frame * frame)
            if cur_frame_energy > threshold:
                activate_frames += 1

        return activate_frames
