import os
import sys
sys.path.append('/home/test/test/liweihao/ember-optimize')
import json
import argparse
import multiprocessing
import numpy as np
import lightgbm as lgb
import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.metrics import roc_auc_score, roc_curve
from ember import PEFeatureExtractor

def main():
    prog = "generate_auc"
    desc = "generate auc score for the model"
    parser = argparse.ArgumentParser(prog = prog,description = desc)
    parser.add_argument("modelpath", metavar = "Model_Path", type = str, help = "Path of the model")
    parser.add_argument("testpath", metavar = "Test_Path", type = str, help = "Path of the test data")
    parser.add_argument("savapath",metavar = "ROC_Path",type = str,help = "Path to save the image of ROC curve")
    args = parser.parse_args()
    
    if(not os.path.exists(args.modelpath) or not os.path.isfile(args.modelpath)):
        parser.error("{} is not a model file".format(args.modelpath))
        
    if(not os.path.exists(args.testpath) or not os.path.isdir(args.testpath)):
        parser.error("{} is not a right test path".format(args.testpath))
    
    
    # 加载测试数据集
    extractor = PEFeatureExtractor(feature_version=2)
    X_test = np.memmap(os.path.join(args.testpath, "X_test.dat"), dtype=np.float32, mode="r")
    y_test = np.memmap(os.path.join(args.testpath, "y_test.dat"), dtype=np.float32, mode="r")
    # 将 X_test 转换为二维数组
    X_test = np.reshape(X_test, (-1, extractor.dim))
        
    # 加载训练好的LightGBM模型
    model = lgb.Booster(model_file=args.modelpath)
    # 使用模型进行预测
    y_pred_proba = model.predict(X_test, num_iteration=model.best_iteration) 
    # 计算AUC值
    auc = roc_auc_score(y_test, y_pred_proba)
    print("AUC Score:", auc)
    
    # 绘制ROC曲线
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    plt.plot(fpr, tpr, label='ROC Curve (AUC = {:.2f})'.format(auc))
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Random Guess')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend()
    plt.grid(True)
    plt.text(0.6, 0.4, 'AUC = {:.2f}'.format(auc), fontsize=12)
    
    # 保存ROC曲线图
    plt.savefig(os.path.join(args.savapath,'roc_curve.png'))
    plt.close()
    
    
if __name__ == "__main__":
    main()