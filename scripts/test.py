import json
import lightgbm as lgb
from matplotlib import pyplot as plt

with open("/home/test/test/liweihao/ember-optimize/data/test_features.jsonl",mode='r') as f:
    max_len = 0
    for line in f:
        length = 0
        data = json.loads(line)
        print(data["histogram"])
        if len(data["histogram"]) > max_len:
            max_len = len(data["histogram"])

print("Max Length:", max_len)

# 训练模型
model = lgb.Booster(model_file="/home/test/test/liweihao/ember-optimize/data/model.txt")

# 获取特征重要性
feature_importance = model.feature_importance()

# 打印特征重要性
print("Feature Importance:", feature_importance)

# 绘制特征重要性条形图
lgb.plot_importance(model, figsize=(20, 40),max_num_features=200)
feature_name = model.feature_name()

plt.savefig("feature_importance.png")
plt.show()