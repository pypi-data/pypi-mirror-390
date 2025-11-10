import uuid
import os
import numpy as np

def ffmpeg_load(audio_path:str, target_sr:int, target_channels=-1, seg_start=0, seg_dur=-1):
    import subprocess
    import io
    import wave
    command = [
        'ffmpeg',
        '-i', audio_path,           # 输入文件
        '-ar', str(target_sr),      # 设置目标采样率
    ]

    if target_channels > 0:
        command += ['-ac', str(target_channels)]     # 设置单声道
    if seg_start > 0:
        command += ['-ss', str(seg_start)]           # 音频截取开始位置(s)
    if seg_dur > 0:
        command += ['-t', str(seg_dur)]              # 音频截取结束位置(s)
        
    command += ['-f', 'wav',                # 设置输出格式
        'pipe:1'                            # 输出到标准输出
    ]
    # 运行 FFmpeg 命令
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 获取输出和错误信息
    output, error = process.communicate()

    resample_audio = []
    if process.returncode != 0:
        print(f"Error: {error.decode()}")
        return resample_audio
    else:
        with io.BytesIO(output) as wav_io:
            with wave.open(wav_io, 'rb') as wav_file:
                # 获取音频参数
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                frame_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()

                # 分块读取音频数据，避免内存溢出
                audio_data = bytearray()
                chunk_size = 1024 * 1024  # 每次读取1MB数据
                remaining_frames = n_frames
                
                while remaining_frames > 0:
                    frames_to_read = min(remaining_frames, chunk_size // wav_file.getsampwidth() // n_channels)
                    chunk = wav_file.readframes(frames_to_read)
                    if not chunk:
                        break
                    audio_data.extend(chunk)
                    remaining_frames -= frames_to_read
                
                # 转换为 NumPy 数组
                audio_array = np.frombuffer(audio_data, dtype=np.int16) / 32768.0

                # 如果是多通道，重塑数组形状为 [channels, samples]
                if n_channels > 1:
                    audio_array = audio_array.reshape(-1, n_channels).T
    return audio_array,target_sr

def get_audio_info(in_audio_file):
    try:     
        import subprocess
        import json
        # 通过ffprobe命令获取完整元数据
        cmd = ['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', in_audio_file]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            return None
            
        info = json.loads(result.stdout)
        stream = info['streams']

        # 找到音频流
        audio_stream = None
        for stream in stream:
            if stream['codec_type'] == 'audio':
                audio_stream = stream
                break
        if audio_stream is None:
            return None
        
        return {
            'codec_name': audio_stream.get('codec_name'),
            'sample_rate': audio_stream.get('sample_rate'),
            'channels': audio_stream.get('channels'),
            'duration': audio_stream.get('duration')
        }
    
    except Exception as e:
        print(f"Error getting audio info: {str(e)}")
        return None

def get_audio_duration(in_audio_file):
    audio_info = get_audio_info(in_audio_file)
    if audio_info is None:
        return None
    if 'duration' not in audio_info:
        return None
    return float(audio_info['duration'])

def check_duration(file_path, expect_min_dur):
    cur_dur = get_audio_duration(file_path)

    if cur_dur is None:
        return False
    
    return cur_dur >= expect_min_dur

def convert_to_wav(file_path, tmp_path, seg_start, seg_dur, tgt_nchannels=None, tgt_sr=None):
    out_wav_path = os.path.join(tmp_path, f'{uuid.uuid4().hex}.wav')

    ss = f'-ss {seg_start}' if seg_start is not None else ''
    t = f'-t {seg_dur}' if seg_dur is not None else ''
    ac = '' if tgt_nchannels is None else f'-ac {tgt_nchannels}'
    ar = '' if tgt_sr is None else f'-ar {tgt_sr}'

    convert_cmd = f'ffmpeg -loglevel panic -y -i {file_path} {ss} {t} {ac} {ar} {out_wav_path}'
    os.system(convert_cmd)
    assert os.path.exists(out_wav_path), f'Error: failed to convert {file_path} to wav'

    return out_wav_path

def torch_audio_to_spec(audio_data, srate, fft_size=2048, hop_size=1024, fmin=None, fmax=None):
    import torch
    import torchaudio
    
    window = torch.hann_window(fft_size)
    spec = torch.stft(torch.from_numpy(audio_data), n_fft=fft_size, hop_length=hop_size, win_length=fft_size, window=window, pad_mode='constant', return_complex=True)

    # stft to melspec
    audio_data = torch.from_numpy(audio_data).to(torch.float64)
    mel_spec = torchaudio.transforms.MelSpectrogram(n_fft=fft_size, hop_length=hop_size, win_length=fft_size, n_mels=256)(audio_data)
    
    spec = torch.abs(spec).numpy()

    spec = np.abs(spec)
    spec = np.log10(spec + 1e-6)

    start_bin = 0 if fmin is None else int(fmin * fft_size / srate)
    end_bin = spec.shape[0] if fmax is None else int(fmax * fft_size / srate)

    spec = spec[start_bin:end_bin, :]

    spec -= spec.mean(axis=(-2,-1), keepdims=True)

    return spec
    
import sys
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python audio_utils.py <audio_file>")
        sys.exit(1)
    in_audio_file = sys.argv[1]
    audio_info = get_audio_info(in_audio_file)
    if audio_info is None:
        print("Failed to get audio info")
        sys.exit(1)
    print(audio_info)

