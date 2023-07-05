import json

# document 1
with open(f"./MTemplateDebugger1.json", "r", encoding="utf-8") as f1:
    content1 = json.load(f1, strict=False)

# document 2
with open(f"./MTemplateDebugger2.json", "r", encoding="utf-8") as f2:
    content2 = json.load(f2, strict=False)

    # for line2 in content2:
    #     print(line)
dic = {}
with open(f"CTemplateDebugger.txt", "w") as f:
    f.write("")
if len(content1) > len(content2):
    for method_name, method_body in content1.items():
        # line1 = line1.replace("@Override", "").strip()
        method_body = method_body.replace("@Override", "").strip()
        # 如果method_name存在于content2，则比对change_num
        if method_name in content2.keys():
            line1_1 = method_body.replace("@Override", "").strip().split('\n')
            line2_2 = content2[method_name].replace("@Override", "").strip().split('\n')
            if method_body == content2[method_name]:
                print("same")
                dic[0] = {method_body: content2[method_name]}
            else:
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
                dic[change_num] = {content2[method_name]: method_body}

        # else:
        #     # method_name不存在于content2
        #     dic[len(method_body.split('\n'))] = {'': method_body}
else:
    for method_name, method_body in content2.items():
        # line1 = line1.replace("@Override", "").strip()
        method_body = method_body.replace("@Override", "").strip()
        # 如果method_name存在于content1，则比对change_num
        if method_name in content1.keys():
            line1_1 = method_body.replace("@Override", "").strip().split('\n')
            line2_2 = content1[method_name].replace("@Override", "").strip().split('\n')
            if method_body == content1[method_name]:
                print("same")
                dic[0] = {method_body: content1[method_name]}
            else:
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
                dic[change_num] = {content1[method_name]: method_body}

        # else:
        #     # method_name不存在于content1
        #     dic[len(method_body.split('\n'))] = {'': method_body}




new_dict = {key: dic[key] for key in sorted(dic.keys(), reverse=True)}
for k,v in new_dict.items():
    for k1, v1 in v.items():
        with open(f"CTemplateDebugger.txt", "a+") as f:
            f.write(f"===={k}\n")
            f.write(f"{k1}\n")
            f.write(f"{v1}\n")

print("dif")












