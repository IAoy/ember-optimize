import os
import sys
import json
import argparse
import pandas as pd
import math

def main():
    prog = "generate_train_test"
    desc = "generate jsonl files based on train/test split from CSV"
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument("benignjsonl", metavar="Benign_Path", type=str, help="Path of benign jsonl file")
    parser.add_argument("maljsonl", metavar="Mal_Path", type=str, help="Path of malicious jsonl file")
    parser.add_argument("traincsv", metavar="Train_CSV", type=str, help="CSV file with training set info")
    parser.add_argument("testcsv", metavar="Test_CSV", type=str, help="CSV file with test set info")
    parser.add_argument("outputpath", metavar="Output_Path", type=str, help="Path to save generated jsonl files")
    parser.add_argument("-n", "--numfiles", type=int, default=6, help="Number of files to split train data into")

    args = parser.parse_args()

    if not os.path.exists(args.benignjsonl) or not os.path.isfile(args.benignjsonl):
        parser.error(f"{args.benignjsonl} is not a benign jsonl file")
    
    if not os.path.exists(args.maljsonl) or not os.path.isfile(args.maljsonl):
        parser.error(f"{args.maljsonl} is not a malicious jsonl file")
        
    if not os.path.exists(args.traincsv) or not os.path.isfile(args.traincsv):
        parser.error(f"{args.traincsv} is not a valid train CSV file")
        
    if not os.path.exists(args.testcsv) or not os.path.isfile(args.testcsv):
        parser.error(f"{args.testcsv} is not a valid test CSV file")

    # 加载 train 和 test 集的文件名
    train_sha256 = load_sha256_from_csv(args.traincsv)
    test_sha256 = load_sha256_from_csv(args.testcsv)

    # 加载 benign 和 malicious jsonl 数据
    benign_data = load_jsonl(args.benignjsonl)
    mal_data = load_jsonl(args.maljsonl)

    # 根据文件名划分训练集和测试集
    train_data, test_data = split_by_sha256(benign_data + mal_data, train_sha256, test_sha256)

    # 保存训练集，分成多个文件
    save_train_data_in_batches(train_data, args.outputpath, args.numfiles)

    # 保存测试集
    save_jsonl(test_data, os.path.join(args.outputpath, "test_features.jsonl"))


def load_sha256_from_csv(csv_path):
    """从 CSV 文件加载 sha256 文件名列表"""
    df = pd.read_csv(csv_path)
    return set(df['sha256'])  # 返回一个文件名的集合


def load_jsonl(file_path):
    """加载 jsonl 文件"""
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data


def split_by_sha256(data, train_sha256, test_sha256):
    """根据 sha256 将数据划分为训练集和测试集"""
    train_data = []
    test_data = []
    
    for entry in data:
        sha256 = entry.get("sha256")  # 假设 jsonl 文件中有 sha256 字段
        if sha256 in train_sha256:
            train_data.append(entry)
        elif sha256 in test_sha256:
            test_data.append(entry)

    return train_data, test_data


def save_train_data_in_batches(train_data, output_dir, num_files):
    """将训练集分成多个文件并保存"""
    os.makedirs(output_dir, exist_ok=True)  # 创建输出目录
    batch_size = math.ceil(len(train_data) / num_files)  # 每个文件的批量大小
    
    for i in range(num_files):
        batch_data = train_data[i * batch_size: (i + 1) * batch_size]
        train_file_path = os.path.join(output_dir, f"train_features_{i}.jsonl")
        save_jsonl(batch_data, train_file_path)


def save_jsonl(data, file_path):
    """保存数据到 jsonl 文件"""
    with open(file_path, 'w') as file:
        for entry in data:
            json.dump(entry, file)
            file.write('\n')


if __name__ == "__main__":
    main()
    print("数据集划分完毕")


