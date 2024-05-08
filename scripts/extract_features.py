import sys
sys.path.append('/home/test/test/liweihao/ember-optimize')
from ember.features import PEFeatureExtractor
import argparse
import json
import os

def main():
    prog = "extract_features"
    descr = "Extract features from raw files to generate jsonl files"
    parser = argparse.ArgumentParser(prog=prog, description=descr)
    parser.add_argument("-v", "--featureversion", type=int, default=2, help="EMBER feature version")
    parser.add_argument("datadir", metavar="DATADIR", type=str, help="files to extract features from")
    parser.add_argument("csvdir",metavar="CSVDIR",type=str,help="directory to save the jsonl files")
    parser.add_argument("-l", "--label", type=str, required=True, help="label for the file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.datadir) or not os.path.isdir(args.datadir):
        parser.error(f"{args.datadir} is not a valid path with raw files")
        
    extractor = PEFeatureExtractor(feature_version=args.featureversion)
    
    for root,dirs,files in os.walk(args.datadir):
        for file in files:
            with open(os.path.join(root,file),mode='rb') as f:
                features = extractor.raw_features(f.read())
                features["label"] = args.label
                print(features)
                
            with open(args.csvdir,mode='a') as f:
                json_line = json.dumps(features)
                f.write(json_line+'\n')

if __name__ == "__main__":
    main()
        