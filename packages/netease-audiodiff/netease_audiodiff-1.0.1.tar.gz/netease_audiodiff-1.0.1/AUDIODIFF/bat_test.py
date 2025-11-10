import sys
from AudioSearchComparator import AudioSearchComparator
from afp_config import AudioConfig
import json

# 加载音频pair列表，并调用compare_audio_fingerprints函数，收集运行结果统计存在对齐的比例和存在差异段的比例
def bat_run(pair_list_path):
    res_lst = []
    with open(pair_list_path, 'r', encoding='utf-8') as f:
        pair_list = f.readlines()
    pair_list = [pair.strip().split('\t') for pair in pair_list]

    comparator = AudioSearchComparator(AudioConfig())

    for pair in pair_list:
        if len(pair) != 2:
            continue
        
        try:
            print(pair[0], pair[1])
            diff_segments = comparator.compare_audio_diff(pair[0], pair[1])
        except Exception as e:
            print(e)
            continue
        res_lst.append((pair[0], pair[1], diff_segments))

    return res_lst

# 统计对齐率和差异率
def stat_res(res_lst):
    align_cnt = 0
    diff_cnt = 0
    for res in res_lst:
        if res[2] is not None:
            align_cnt += 1
        else:
            diff_cnt += 1
        if len(res[3]) > 0:
            diff_cnt += 1
    print('对齐率：', align_cnt/len(res_lst))
    print('不通过率：', diff_cnt/len(res_lst))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python bat_run.py pair_list_path res.txt')
        sys.exit(1)
    res_lst = bat_run(sys.argv[1])
    #stat_res(res_lst)
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        for res in res_lst:
            f.write(res[0]+'\t'+res[1]+'\t'+json.dumps(res[2], ensure_ascii=False)+'\n')
