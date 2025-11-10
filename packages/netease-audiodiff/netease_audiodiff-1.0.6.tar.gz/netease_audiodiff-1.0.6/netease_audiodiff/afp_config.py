class AudioConfig:
    """音频处理相关配置"""
    def __init__(self, config_dict=None):
        """
        初始化音频配置
        
        Args:
            config_dict: 配置字典，可选
        """
        # 默认配置
        # 音频时长限制
        self.MAX_DURATION = -1
        self.START_DURATION = 0
        self.CHECK_MONO = True
        
        # 目标采样率
        self.OBJ_SR = 8000
        self.SAMPLE_TO_MS = 1000 / self.OBJ_SR

        # FFT参数
        self.FFT_SIZE = 1024
        self.HOP_SIZE = 160
        self.FRM_DUR = self.HOP_SIZE / self.OBJ_SR
        self.FRM_DUR_MS = int(self.FRM_DUR * 1000)

        # 最小检测时长
        self.MIN_SEG_DUR = 0.15
        self.MIN_SEG_FRMS = int(self.MIN_SEG_DUR * self.OBJ_SR / self.HOP_SIZE)
        self.SMOOTH_FRMS = 5

        # 全局对齐最大偏差
        self.GLOBAL_MAX_SHIFT = 1800000
        self.GLOBAL_ALIGN_USE_DUR = 60
        self.GLOBAL_ALIGN_USE_FRMS = int(self.GLOBAL_ALIGN_USE_DUR * self.OBJ_SR / self.HOP_SIZE)
        # 对齐命中阈值
        self.ALIGNED_HIT_THRES = 100
        
        # 片段对齐参数
        # 允许最大偏差
        self.SEG_MAX_SHIFT = 30
        # 片段对齐使用时长
        self.ALIGN_SEG_DUR = 8
        self.ALIGN_SEG_FRMS = int(self.ALIGN_SEG_DUR * self.OBJ_SR / self.HOP_SIZE)
        # 段差异阈值
        self.BER_SEG_THRES = 0.35
        
        # 指纹量化阈值
        self.FP_QUANT_THRES_LOWER = 0.0005
        self.FP_QUANT_THRES_UPPER = 0.003
        self.FP_QUANT_THRES = 0.003
        
        # 帧能量阈值
        self.SIL_ENERGY_THRES = 0.004

        # 尾部淡出检测
        self.FADE_DETECT_DUR = 0.2
        self.FADE_ENERGY_RATIO_THRES = 0.5
        self.FADE_MAX_DUR = 10.0  # 10s
        self.FADE_MAX_SAMPLES = int(self.FADE_MAX_DUR * self.OBJ_SR)
        self.FADE_LOST_DUR = 1  # 替换音频允许缺少的最大淡出时长
        self.FADE_LOST_FRMS = int(self.FADE_LOST_DUR * self.OBJ_SR / self.HOP_SIZE)

        # bark子带频率边界
        #self.BARK_FREQS = [100, 770, 1080, 1480, 2000, 4000, 12000, 15500, 22050] # 6个子带
        # self.BARK_FREQS = [100, 200, 300, 510, 770, 1080, 1480, 2000, 2700, 4000] # 9个子带
        self.BARK_FREQS = [100, 200, 300, 400, 510, 630, 770, 920, 1080, 1270, 1480, 1720,
                      2000, 2320, 2700, 3150, 3700, 4000]  # 17个子带
        # self.BARK_FREQS = [100, 200, 300, 400, 510, 630, 770, 920, 1080, 1270, 1480, 1720,
        #              2000, 2320, 2700, 3150, 3700, 4000, 5300, 6400, 7700, 9500, 11000] # 24个子带
        self.BIT_NUM = len(self.BARK_FREQS) - 1

        # 音量检测阈值
        self.VOL_DB_DIFF_THRES = -16
        
        # 如果提供了配置字典，则更新配置
        if config_dict:
            self.update_config(config_dict)
    
    def update_config(self, config_dict):
        """
        更新配置
        
        Args:
            config_dict: 配置字典
        """
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # 更新依赖参数
        self._update_dependent_params()
    
    def _update_dependent_params(self):
        """更新依赖计算的参数"""
        self.FRM_DUR = self.HOP_SIZE / self.OBJ_SR
        self.FRM_DUR_MS = int(self.FRM_DUR * 1000)
        self.MIN_SEG_FRMS = int(self.MIN_SEG_DUR * self.OBJ_SR / self.HOP_SIZE)
        self.GLOBAL_ALIGN_USE_FRMS = int(self.GLOBAL_ALIGN_USE_DUR * self.OBJ_SR / self.HOP_SIZE)
        self.ALIGN_SEG_FRMS = int(self.ALIGN_SEG_DUR * self.OBJ_SR / self.HOP_SIZE)
        self.FADE_MAX_SAMPLES = int(self.FADE_MAX_DUR * self.OBJ_SR)
        self.FADE_LOST_FRMS = int(self.FADE_LOST_DUR * self.OBJ_SR / self.HOP_SIZE)
        self.BIT_NUM = len(self.BARK_FREQS) - 1
    
    def __str__(self):
        """返回配置的字符串表示"""
        config_str = "音频配置:\n"
        for key, value in self.__dict__.items():
            if not key.startswith('_'):  # 跳过私有属性
                config_str += f"  {key} = {value}\n"
        return config_str
    
    @classmethod
    def default_config(cls):
        """返回默认配置"""
        return cls()
    
    @classmethod
    def from_dict(cls, config_dict):
        """从字典创建配置"""
        return cls(**config_dict)
    
    def to_dict(self):
        """将配置转换为字典"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    
