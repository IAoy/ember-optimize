import sys
sys.path.append('/media/liweihao/ember-optimize')
from ember.features import PEFeatureExtractor
import argparse
import json
import csv
import os

def main():
    prog = "extract_features"
    descr = "Extract features from raw files to generate jsonl files"
    parser = argparse.ArgumentParser(prog=prog, description=descr)
    parser.add_argument("-v", "--featureversion", type=int, default=2, help="EMBER feature version")
    parser.add_argument("rawdatadir", metavar="RAWDATADIR", type=str, help="Directory containing the raw files")
    parser.add_argument("outputdir", metavar="OUTPUTDIR", type=str, help="Directory to save the jsonl and csv files")
    parser.add_argument("-l", "--label", type=int, required=True, choices=[0, 1], help="Label for the file (0 for benign, 1 for malware)")

    args = parser.parse_args()

    if not os.path.exists(args.rawdatadir) or not os.path.isdir(args.rawdatadir):
        parser.error(f"{args.rawdatadir} is not a valid path with raw files")
    
    if not os.path.exists(args.outputdir):
        os.makedirs(args.outputdir)  # 创建 outputdir 目录（如果不存在）
    
    # 根据-l的值动态设置jsonl和csv文件路径
    if args.label == 0:
        jsonl_path = os.path.join(args.outputdir, "benign.jsonl")
        csv_path = os.path.join(args.outputdir, "benign_mapping.csv")
    elif args.label == 1:
        jsonl_path = os.path.join(args.outputdir, "malware.jsonl")
        csv_path = os.path.join(args.outputdir, "malware_mapping.csv")
    
    extractor = PEFeatureExtractor(feature_version=args.featureversion)
    
    # 打开 CSV 文件，以便将每个文件的 key_sha256 和 value_sha256 写入
    with open(csv_path, mode='a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # 检查 CSV 文件是否为空，如果为空，写入表头
        if csvfile.tell() == 0:
            csv_writer.writerow(["key_sha256", "value_sha256"])
        
        # 遍历目录中的文件并提取特征
        for root, dirs, files in os.walk(args.rawdatadir):
            for file in files:
                # 跳过 CSV 和 JSONL 文件
                if file.endswith('.csv') or file.endswith('.jsonl'):
                    continue
                
                print(f"Now is Processing file:{file}")
                with open(os.path.join(root, file), mode='rb') as f:
                    features = extractor.raw_features(f.read())
                    features["label"] = args.label
                    key_sha256 = file
                    value_sha256 = features["sha256"]
                    print(features)
                
                # 写入 JSONL 文件
                with open(jsonl_path, mode='a') as f:
                    json_line = json.dumps(features)
                    f.write(json_line + '\n')
                
                # 写入 CSV 文件
                csv_writer.writerow([key_sha256, value_sha256])

if __name__ == "__main__":
    main()
