import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# document 1
with open(f"./MQueryParser1.json", "r", encoding="utf-8") as f1:
    content1 = json.load(f1, strict=False)

# document 2
with open(f"./MQueryParser2.json", "r", encoding="utf-8") as f2:
    content2 = json.load(f2, strict=False)

# 固定随机种子
np.random.seed(0)

# build model
model = RandomForestClassifier(n_estimators=100)

# count change_num
dic = {}
for line1, line2 in zip(content1.values(), content2.values()):
    line1 = line1.replace("@Override", "").strip()
    line2 = line2.replace("@Override", "").strip()
    if line2 == line1:
        print("same")
        dic[0] = {line1: line2}
    else:
        line1_1 = line1.split('\n')
        line2_2 = line2.split('\n')
        change_num_1 = 0
        change_num_2 = 0
        if len(line2_2) > len(line1_1):
            for i2 in line2_2:
                if i2 in line1_1:
                    pass
                elif "*" in i2:
                    pass
                elif "//" in i2:
                    pass
                else:
                    change_num_2 += 1
        else:
            for i1 in line1_1:
                if i1 in line2_2:
                    pass
                elif "*" in i1:
                    pass
                elif "//" in i1:
                    pass
                else:
                    change_num_1 += 1
        change_num = change_num_1 + change_num_2
        dic[change_num] = {line1: line2}

# 读取数据集
train_features = np.load("train_features.npy")
train_labels = np.load("train_labels.npy")
test_features = np.load("test_features.npy")

# 创建模型
model = RandomForestClassifier(n_estimators=100)

# 训练模型
print('training...')
model.fit(train_features, train_labels)

# 分类预测
print('testing...')
test_predictions = model.predict(test_features)
test_predictions = list(test_predictions)
num_test = len(test_predictions)

# 保存结果
save_file = "random_forest_results.csv"
with open(save_file, "w") as write_file:
    write_file.write("ID,Category\n")

    for i in range(num_test):
        temp = "{},{}\n".format(str(i), str(test_predictions[i]))
        write_file.write(temp)

print('done!')