import json

# document 1
with open(f"./MQueryParser1.json", "r", encoding="utf-8") as f1:
    content1 = json.load(f1, strict=False)

# document 2
with open(f"./MQueryParser2.json", "r", encoding="utf-8") as f2:
    content2 = json.load(f2, strict=False)

    # for line2 in content2:
    #     print(line)
with open(f"CQueryParser.txt", "w") as f:
    f.write("")
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
    # with open(f"CQueryParser.txt", "a+") as f:
    #         f.write(f"{line1} \n")
    #         f.write(f"{line2} \n")
    print(line1, line2)
new_dict = {key: dic[key] for key in sorted(dic.keys(), reverse=True)}
for k,v in new_dict.items():
    for k1, v1 in v.items():
        with open(f"CQueryParser.txt", "a+") as f:
            f.write(f"===={k}\n")
            f.write(f"{k1}\n")
            f.write(f"{v1}\n")

print("dif")












