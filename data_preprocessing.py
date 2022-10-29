#! /usr/bin/env python3
'''
此程序根据滑动窗口收集数据
使用方法:
python prepared_data.py
注意:
    sub_dirs 为动作
    parent_dirs为训练集和测试集源文件的位置
    save_paths为保存的位置
'''
import numpy as np
import glob
import os
from ti_mmwave_rospkg import RadarScan
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

sub_dirs = ['boxing', 'wave', 'jack', 'jump', 'walk', 'squats']


parent_dirs = ['./to_txt/train',
               './to_txt/test']
save_paths = ['./har_train_frame',
              './har_test_frame']

#二级窗口中固定点数
points_number = 256
#一级窗口大小
total_frame_cnt = 60
#二级窗口大小
mix_frame_len = 20
#一级窗口滑动系数
window_slid_len = 10
#二级窗口滑动系数
mix_slid_len = 5

class_indexs = {i: 0 for i in sub_dirs}


def doMsg(msg: RadarScan, args):
    #!总之需要256个点以帧为单位结束
    global total_frame_cnt,  mix_frame_len,  mix_slid_len,   points_number
    files,save_path, sub_dir, args[3], args[4], args[5], args[6], args[7] = args
    if(msg.point_id == 0):  # 上一帧的结束，下一帧的开始
        # 如果是start == 1 , 那么代表有上一帧
        if(args[5] == 1):
            # 保存上一帧
            # 去除没有的点
            frame_data_with_nonan = args[4][~args[4]['x'].isna()]
            if(len(args[3]) < total_frame_cnt):  # 如果小于60帧
                # print(frame_data_with_nonan)
                args[3].append(frame_data_with_nonan)  # 添加上一帧数据
                # 清空帧数据
                args[4] = pd.DataFrame({'x': np.nan, 'y': np.nan, 'z': np.nan, 'velocity': np.nan,
                                           'bearing': np.nan, 'intensity': np.nan}, index=range(50))  # 一帧最多50个点
            else:  # 如果超过了total_frame_cnt帧,对数据做处理，保存，并且丢弃前window_slid_len数据长度
                total_data = pd.DataFrame()
                # 在60帧的窗口内滑动采样
                for i in np.arange(0, (total_frame_cnt-mix_frame_len)+1, mix_slid_len):
                    # print(i)
                    mix_frame = args[3][i:i+mix_frame_len]
                    mix_data = pd.DataFrame()
                    for tmpdata in mix_frame:
                        mix_data = mix_data.append(tmpdata)
                    #! 60帧数据够了，那么取固定点数
                    mix_data = mix_data.iloc[:points_number, :]
                    while(mix_data.shape[0] < points_number):
                        mix_data = mix_data.append(mix_data.iloc[0, :])
                    # 保存
                    total_data = total_data.append(mix_data)
                # 保存所有二级窗口滑动数据序列集合
                total_data.iloc[:,:6].to_csv(save_path+'/'+sub_dir + '_'+str(args[7][sub_dir])+'.csv', index=False)
                args[7][sub_dir] += 1  # 记录帧数
                # 完成后，丢弃前slid_len数据长度
                args[3] = args[3][window_slid_len:]
                # print(len(args[3]))
                # 添加上一帧的内容
                args[3].append(frame_data_with_nonan)
                args[4] = pd.DataFrame({'x': np.nan, 'y': np.nan, 'z': np.nan, 'velocity': np.nan,
                                           'bearing': np.nan, 'intensity': np.nan}, index=range(50))  # 一帧最多50个点
            # 保存点的开始
            args[6] = 0
            args[4]['x'][args[6]] = round(msg.x, 6)
            args[4]['y'][args[6]] = round(msg.y, 6)
            args[4]['z'][args[6]] = round(msg.z, 6)
            args[4]['velocity'][args[6]] = round(msg.velocity, 6)
            args[4]['bearing'][args[6]] = round(msg.bearing, 6)
            args[4]['intensity'][args[6]] = round(msg.intensity, 6)
            args[6] += 1
        elif(args[5] == 0):  # 如果是刚开始(没有上一帧)
            args[5] = 1  # 代表开始
            args[4]['x'][args[6]] = round(msg.x, 6)
            args[4]['y'][args[6]] = round(msg.y, 6)
            args[4]['z'][args[6]] = round(msg.z, 6)
            args[4]['velocity'][args[6]] = round(msg.velocity, 6)
            args[4]['bearing'][args[6]] = round(msg.bearing, 6)
            args[4]['intensity'][args[6]] = round(msg.intensity, 6)
            args[6] += 1
    else:
        if(args[6] <= 50):
            args[4]['x'][args[6]] = round(msg.x, 6)
            args[4]['y'][args[6]] = round(msg.y, 6)
            args[4]['z'][args[6]] = round(msg.z, 6)
            args[4]['velocity'][args[6]] = round(msg.velocity, 6)
            args[4]['bearing'][args[6]] = round(msg.bearing, 6)
            args[4]['intensity'][args[6]] = round(msg.intensity, 6)
            if(args[6] > 50):
                print("error2")
                print(args[6])
            args[6] += 1


def get_data(file_path, args):
    print(file_path)
    with open(file_path) as f:
        lines = f.readlines()
    frame_num_count = -1
    frame_num = []
    x = []
    y = []
    z = []
    velocity = []
    intensity = []
    wordlist = []
    for x1 in lines:
        for word in x1.split():
            wordlist.append(word)
    length1 = len(wordlist)
    ret = RadarScan()
    for i in range(0, length1):
        if wordlist[i] == "point_id:" and wordlist[i+1] == "0":
            frame_num_count += 1
            ret.point_id = 0
        if wordlist[i] == "point_id:":
            # frame_num.append(frame_num_count)
            ret.point_id = int(wordlist[i+1])
        if wordlist[i] == "x:":
            # x.append(wordlist[i+1])
            ret.x = float(wordlist[i+1])
        if wordlist[i] == "y:":
            # y.append(wordlist[i+1])
            ret.y = float(wordlist[i+1])
        if wordlist[i] == "z:":
            # z.append(wordlist[i+1])
            ret.z = float(wordlist[i+1])
        if wordlist[i] == "velocity:":
            # velocity.append(wordlist[i+1])
            ret.velocity = float(wordlist[i+1])
        if wordlist[i] == "bearing:":
            # bearing.append(wordlist[i+1])
            ret.bearing = float(wordlist[i+1])
        if wordlist[i] == "intensity:":
            # intensity.append(wordlist[i+1])
            ret.intensity = float(wordlist[i+1])
            doMsg(ret, args)
            ret = RadarScan()

def Files_Parse(args):
    files = args[0]
    for fn in files:
        get_data(fn,args)


# parse the data file
def parse_RF_files(parent_dir, sub_dirs, save_path,  file_ext='*.txt'):
    args = []
    global class_indexs
    for sub_dir in sub_dirs:
        windows_data = []
        frame_data = pd.DataFrame({'x': np.nan, 'y': np.nan, 'z': np.nan, 'velocity': np.nan,
                                'bearing': np.nan, 'intensity': np.nan}, index=range(50))  # 一帧最多50个点
        start = 0
        int_cnt = 0  # 一个类从新开始一帧的计时
        files = sorted(glob.glob(os.path.join(parent_dir, sub_dir+file_ext)))
        # 用arg方式传递
        arg = [files, save_path, sub_dir, windows_data, frame_data, start, int_cnt, dic]
        args.append(arg)
    with ProcessPoolExecutor() as pool: #进程池
        results = pool.map(Files_Parse, args)


if __name__ == "__main__":
    #! dic放在这里让，class_indes续上
    m = Manager()
    dic = m.dict(class_indexs)
    for parent_dir, save_path in zip(parent_dirs, save_paths):
        parse_RF_files(parent_dir, sub_dirs, save_path)
    with open(os.path.join('./', 'train_data_names.csv'), 'w') as f:
        f.write('\n'.join(os.listdir(save_paths[0])))
    with open(os.path.join('./', 'test_data_names.csv'), 'w') as f:
        f.write('\n'.join(os.listdir(save_paths[1])))
    with open(os.path.join('./', 'class_name.csv'), 'w') as f:
        f.write('\n'.join(sub_dirs))
