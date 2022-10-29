#! /usr/bin/env python3
import rospy
from ti_mmwave_rospkg.msg import RadarScan
import numpy as np
import glob
import os
# sub_dirs = ['boxing', 'jack', 'jump', 'squats', 'walk']
sub_dirs = ['walk']

one_hot = {}
for i, name in enumerate(sub_dirs):
    one_hot[name] = i
# txt文件夹
parent_dir = './to_txt/train/'

def get_data(file_path):
    if not rospy.is_shutdown():
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
            if not rospy.is_shutdown():
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
                if wordlist[i] == "intensity:":
                    # intensity.append(wordlist[i+1])
                    ret.intensity = float(wordlist[i+1])
                    pub.publish(ret)
                    ret = RadarScan()
                    rate.sleep()
            else:
                break


# parse the data file


def parse_RF_files(parent_dir, sub_dirs, file_ext='*.txt'):
    rospy.loginfo("class is : %s", str(sub_dirs))
    for sub_dir in sub_dirs:
        files = sorted(glob.glob(os.path.join(parent_dir, sub_dir, file_ext)))
        for fn in files:
            get_data(fn)

if __name__ == "__main__":
    # 1.初始化 ROS 节点
    rospy.init_node('advise')
    pub = rospy.Publisher(
        '/ti_mmwave/radar_scan', RadarScan, queue_size=10)
    rate = rospy.Rate(1000)
    for sub_dir in sub_dirs:
        parse_RF_files(parent_dir, [sub_dir])
