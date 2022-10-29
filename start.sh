#!/bin/bash
starttime=$(date)

classed=(boxing wave jack jump walk squats)

savepath=(./har_train_frame ./har_test_frame)

rm -rf ./dataset/*

for j in `seq 0 1`;
do
  rm -rf ${savepath[$j]}/*
done

echo "start processing!"

python3 ./data_preprocessing.py > /dev/null 2>&1

echo trainfile cnt is `ls ${savepath[0]} | wc -l`
echo testfile cnt is  `ls ${savepath[1]} | wc -l`

echo "start move file to correct filedir!"

for i in ${classed[@]}; 
do
    mkdir -p dataset/$i
    for j in ${savepath[@]};
    do
        mv $j/${i}_* dataset/$i
    done
done

mv ./class_name.csv ./dataset
mv ./train_data_names.csv ./dataset
mv ./test_data_names.csv ./dataset
cp ./data_preprocessing.py ./dataset


echo "start zip file!"
zip -r dataset.zip dataset > /dev/null 2>&1


endtime=$(date)

echo "end of processing"

echo ${starttime}-${endtime}
