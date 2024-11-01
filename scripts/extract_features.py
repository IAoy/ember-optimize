import sys
sys.path.append('/home/test/test/liweihao/ember-optimize')
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
    parser.add_argument("datadir", metavar="DATADIR", type=str, help="files to extract features from")
    parser.add_argument("jsonldir", metavar="JSONLDIR", type=str, help="directory to save the jsonl files")
    parser.add_argument("sha256csv", metavar="SHA256CSV", type=str, help="path to save the sha256 CSV file")
    parser.add_argument("-l", "--label", type=str, required=True, help="label for the file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.datadir) or not os.path.isdir(args.datadir):
        parser.error(f"{args.datadir} is not a valid path with raw files")
    
    extractor = PEFeatureExtractor(feature_version=args.featureversion)
    
    # 打开 CSV 文件，以便将每个文件的 key_sha256 和 value_sha256 写入
    with open(args.sha256csv, mode='a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # 检查 CSV 文件是否为空，如果为空，写入表头
        if csvfile.tell() == 0:
            csv_writer.writerow(["key_sha256", "value_sha256"])
        
        for root, dirs, files in os.walk(args.datadir):
            for file in files:
                with open(os.path.join(root, file), mode='rb') as f:
                    features = extractor.raw_features(f.read())
                    features["label"] = args.label
                    key_sha256 = file
                    value_sha256 = features["sha256"]
                    print(features)
                
                # 写入 JSONL 文件
                with open(args.jsonldir, mode='a') as f:
                    json_line = json.dumps(features)
                    f.write(json_line + '\n')
                
                # 写入 CSV 文件
                csv_writer.writerow([key_sha256, value_sha256])

if __name__ == "__main__":
    main()
