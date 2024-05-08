import os
import sys
import math
import json
import random
import argparse

def main():
    prog = "generate_train"
    desc = "generate jsonl files that suit ember api"
    parser  = argparse.ArgumentParser(prog = prog, description = desc)
    parser.add_argument("benignjsonl", metavar = "Benign_Path", type = str, help = "Path of bengin jsonl file")
    parser.add_argument("maljsonl", metavar = "Mal_Path", type = str, help = "Path of  mal jsonl file")
    parser.add_argument("outputpath", metavar = "Output_Path", type = str, help = "Path to save generated jsonl files")
    parser.add_argument("-r","--ratio", type = float, default = 0.8, help = "ratio of trainsets and validsets")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.benignjsonl) or not os.path.isfile(args.benignjsonl):
        parser.error("{} is not a benign jsonl file".format(args.benignjsonl))
    
    if not os.path.exists(args.maljsonl) or not os.path.isfile(args.maljsonl):
        parser.error("{} is not a Malicious jsonl file".format(args.maljsonl))
        
    merged_data = merge_jsonl(args.benignjsonl, args.maljsonl)
    random.shuffle(merged_data)  # 打乱数据
    
    #按照命令行中的比例分割训练集和测试集
    total_samples = len(merged_data)
    train_samples = int(total_samples * args.ratio) 

    
    train_data = merged_data[:train_samples]
    test_data = merged_data[train_samples:]
    
    print(f"Total samples: {total_samples}, Train samples: {len(train_data)}, Test samples: {len(test_data)}")
    # 保存训练集
    train_dir = os.path.join(args.outputpath, "train")
    os.makedirs(train_dir, exist_ok=True)
    num_train_files = 6
    batch_size = math.ceil(len(train_data) / num_train_files)
    print("batch_size: ", batch_size)
    for i in range(num_train_files):
        train_file_path = os.path.join(train_dir, f"train_features_{i}.jsonl")
        save_jsonl(train_data[i*batch_size:(i+1)*batch_size], train_file_path)
    
    # 保存测试集
    test_file_path = os.path.join(args.outputpath, "test_features.jsonl")
    save_jsonl(test_data, test_file_path)



#加载jsonl文件
def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

#将良性和恶意的jsonl文件合并
def merge_jsonl(benign_path, mal_path):
    benign_data = load_jsonl(benign_path)
    mal_data = load_jsonl(mal_path)
    return benign_data + mal_data

#将数据保存到jsonl文件中
def save_jsonl(data, file_path):
    with open(file_path, 'w') as file:
        for entry in data:
            json.dump(entry, file)
            file.write('\n')
   

if __name__ == "__main__":
    main()