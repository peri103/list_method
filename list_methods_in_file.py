# 我一般处理一个github repo的步骤：
# 0. 下载source code: https://github.com/google/guava/releases
# 1. build project，guava用的是nvm，下载源码以后在命令行mvn clean install -DskipTests=true
# 2. 拿到所有的.class 文件 find . -name "*.class" &> jl_class_file_lists.txt
# 3. 给java class分类，很多都是guava他自己的testlib，只考虑不是test的源文件 （然后发现他们都在路径guava/src/com/google/common 底下)
# 4. 用get_id_code_map_of_functions_from_source_code获得一个java 文件里的所有function

import re
import os
import subprocess
import logging
# from parser import DFG_java
from tree_sitter import Language, Parser
root_dir = os.path.dirname(__file__)

# 这个my-languages.so 是python tree_sitter用来parse语法树的，可以自己生成
# 记得更新一下my-languages.so的位置
JAVA_LANGUAGE = Language(root_dir + '/my-languages.so', 'java')
parser = Parser()
parser.set_language(JAVA_LANGUAGE)

base_v30_dir = "/Users/yunruipei/Desktop/Archive/commons-jexl3.2"
# list_file_v30 = base_v30_dir+"/Users/yunruipei/Desktop/Archive/js1.txt"
base_v31_dir = "/Users/yunruipei/Desktop/Archive/commons-jexl3.2.1"
# list_file_v31 = base_v31_dir+"/Users/yunruipei/Desktop/Archive/js2.txt"

# logging，设置不同level可以很方便控制console log

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s')

# file_folder = "utils/class_stats"

evosuite_sys_var_set = False

def add_to_dict(dict, key, v):
    if key in dict:
        dict[key].append(v)
    else:
        dict[key] = [v]

# 只是看看stats
def stat_from_lines_list(lines_list, target_dict):
    tester_c = 0
    for line in lines_list:
        if "Tester" in line:
            tester_c+=1
        big_dir = line.split("/")[1]
        add_to_dict(target_dict, big_dir, line.split("/")[-1][:-6])
    print(" number of class files are {}".format(tester_c))
    for k,v in target_dict.items():
        print("dir {}: file n: {}".format(k, len(target_dict[k])))

def remove_bad_char(s):
    bad_chars = [';', ':', '!', "*", " "]
    for i in bad_chars:
        s = s.replace(i, "")
    return s


# 从一个java文件，比如/jsoup14/src/main/java/org/jsoup/nodes/Attribute.java, 拿到这个文件具体是什么package
# java -jar $EVOSUITE -class /Users/yunruipei/Desktop/Archive/jsoup14/src/main/java/org/jsoup/nodes/Attribute -projectCP jsoup/target/classes

# 从一个java文件，比如/guava/src/com/google/common/collect/AbstractMapBasedMultiset.java, 拿到这个文件具体是什么package
# 那这个是因为之后生成evosuite 的时候，package必须放在-class param里面：  java -jar $EVOSUITE -class com.google.common.collect.SortedMultisets-projectCP guava/target/classes
def get_java_package(v1_dir=base_v30_dir+"/src", pkg="main/java/org/apache/commons/jexl3/internal", class_file="InterpreterBase.java"):
    file_path = v1_dir+"/"+pkg+"/"+class_file
    with open(file_path) as f:
        file_context = f.read()
        # print("the file context is {}".format(file_context))
    if not file_path:
        return
    file_tree = parser.parse(bytes(file_context, 'utf8')).root_node
    for i in file_tree.children:
        # logger.debug(i.text) #if should be something like b'package com.google.common.collect;'
        if i.type == "package_declaration":
            # logger.debug(i.sexp())
            pkg_name = i.text.split()[1].decode("utf-8")
            return remove_bad_char(pkg_name)

# 给一个ast树node，返回树里所有node_type的node
def DFS_tree_get_type(root_node, node_type="method_declaration"):
    # do a DFS for the ast tree
    node_stack = []
    depth = 1
    node_stack.append([root_node, depth])
    methods_nodes_list = []
    while len(node_stack) != 0:
        cur_node, cur_depth = node_stack.pop()
        if cur_node.type == node_type:
            methods_nodes_list.append(cur_node)
        for child_node in cur_node.children:
            if len(child_node.children) != 0:
                depth = cur_depth + 1
                node_stack.append([child_node, depth])

    logger.debug("===N of {}: {}".format(node_type, len(methods_nodes_list)))
    methods_nodes_list.reverse()
    for i in methods_nodes_list:
        logger.debug("----")
        logger.debug(i.text.decode('utf-8'))
    return methods_nodes_list

# 这个print一个java file里的method
# def get_id_code_map_of_functions_from_source_code(dir_part1=base_v30_dir, dir_part2="src", pkg="/main/java/org/jsoup/select", class_file="Collector.java"):
def get_id_code_map_of_functions_from_source_code(dir_part1=base_v30_dir, dir_part2="src", pkg="main/java/org/apache/commons/jexl3/internal", class_file="InterpreterBase.java"):
    file_path = dir_part1+"/"+dir_part2 + "/" + pkg + "/" + class_file
    with open(file_path) as f:
        file_context = f.read()
        # print("the file context is {}".format(file_context))
    if not file_path:
        logger.error("file doesn't exist, pass")
        return
    file_tree = parser.parse(bytes(file_context, 'utf8')).root_node
    functions_list = DFS_tree_get_type(file_tree, "method_declaration")

    result = {}
    # 这里没有完全想好，result 作为一个dictionary，key是函数名字，value是list of method bodys, 因为一个文件里可能有好几个class，然后有重名的
    for i in functions_list:
        # get function name. e.g: iterator
        function_identifier = get_child_of_type_first_return(i, "identifier")
        function_identifier_in_text = function_identifier.text.decode('utf-8')
        if function_identifier_in_text in result:
            result[function_identifier_in_text].append(i)
            continue
        else:
            result[function_identifier_in_text] = [i]
    return result

# 只是用evosuite list所有的classes。 java -jar $EVOSUITE -listClasses -target guava/target/classes/com/google/common/collect
def evosuite_list_classes(project_dir=base_v31_dir,
        evo_jar_loc = "/Users/yunruipei/Desktop/list_method/evosuite-1.2.0.jar",
        target = "/Users/yunruipei/Desktop/Archive/commons-jexl3.2/target/classes/org/apache/commons/jexl3"):
    gen_class_cmd = "java -jar "+evo_jar_loc+" -listClasses -target "+target
    p = subprocess.Popen(gen_class_cmd.split(), cwd=project_dir, stdout=subprocess.PIPE)
    out, err = p.communicate()
    out_lists = out.decode("utf-8").splitlines()

    return out_lists
# 给一个ast树node，返回child里第一个符合node_type的node
def get_child_of_type_first_return(root_node, target_child_type):
    for i in root_node.children:
        if i.type == target_child_type:
            return i
    return None
# 给一个ast树node，返回child里所有符合node_type的node
def get_all_children_of_type(root_node, target_child_type):
    output = []
    for i in root_node.children:
        if i.type == target_child_type:
            output.append(i)
    return output
# breakdown一个method invocation AST node. 返回结果应该是[id, dot, id, argument list]
def break_method_invocation_node(method_invo_node):
    if method_invo_node.type != "method_invocation":
        logger.error("break_method_invocation_node, input passed in is not method_invo_node type.")
        return
    # it should be list of 4: id, dot, id, argument list
    output = []
    return method_invo_node.children
'''
# 没用，检查一个ast node是否有任何throws
def if_throws_in_method(method_root_node):
    if method_root_node.type != "method_declaration":
        logger.error("obtain_oracle_from_test_code, input passed in is not method type.")
        return
    for i in method_root_node.children:
        if i.type == "throws":
            return True
    return False

# 检查一个ast node是否有任何try catch
def check_contains_try_catch_in_method(method_root_node):
    if method_root_node.type != "method_declaration":
        logger.error("obtain_oracle_from_test_code, input passed in is not method_declaration type.")
        return
    code_block_of_method = get_child_of_type_first_return(method_root_node, "block")
    try_block = get_child_of_type_first_return(code_block_of_method, "try_statement")
    return try_block is not None
'''
'''
# 没用，从evosuite生成的代码ast node里拿到test oracle
def obtain_oracle_from_test_code(method_root_node):
    if method_root_node.type != "method_declaration":
        logger.error("obtain_oracle_from_test_code, input passed in is not method_declaration type.")
        return
    method_body = method_root_node.text.decode("utf-8")
    tgt_method = []
    oracle = ""
    if check_contains_try_catch_in_method(method_root_node):
        code_block_of_method = get_child_of_type_first_return(method_root_node, "block")
        try_block = get_child_of_type_first_return(code_block_of_method, "try_statement")
        # find the method in try?
        try_block_insider_code = get_child_of_type_first_return(try_block, "block")
        try_block_first_func = get_child_of_type_first_return(try_block_insider_code, "expression_statement")
        tgt_method.append(get_child_of_type_first_return(try_block_first_func, "method_invocation").children[2].text.decode("utf-8"))# shich is the identifier

        # find the verify exception in catch block
        catch_block = get_child_of_type_first_return(try_block, "catch_clause")
        catch_block_code = get_child_of_type_first_return(catch_block, "block")
        oracle = get_child_of_type_first_return(catch_block_code, "expression_statement").text.decode("utf-8")
        # logger.info(" --- for method contains try, catch method! \n --- target method: {}\n--- found oracle is: {}".format(tgt_method, oracle))

        pass
    else:
        # type1: the most common case, do multiple functions, and assert in last line:
        code_block_of_method = get_child_of_type_first_return(method_root_node, "block")
        # wjl, print out all the method_invocation in this method
        a = DFS_tree_get_type(code_block_of_method, "method_invocation")
        for i in a:
            if len(i.children)>2:
                tgt_method.append(i.children[2].text.decode("utf-8"))

        oracle_expression = get_all_children_of_type(code_block_of_method, "expression_statement")[-1]
        oracle = oracle_expression.text.decode("utf-8")

        # logger.info(
        #     " --- for method contains NOT try, catch method! \n --- target method: {}\n--- found oracle is: {}".format(
        #         tgt_method, oracle))
    logger.info(" --- for this generated test,\n --- target method: {}\n --- oracle is: {}".format(tgt_method, oracle))
    return [method_body, tgt_method, oracle]

    # pass

# 没用，从evosuite生成的代码ast node里拿到所有的method，一般倒数第二个是被测试的target method.
def get_evosuite_test_body(dir_part1=base_v30_dir, dir_part2="evosuite-tests", pkg="com/google/common/collect", class_name="AbstractMapBasedMultiset"):
    file_path =  dir_part1+"/"+dir_part2 + "/" + pkg + "/" + class_name+"_ESTest.java"
    with open(file_path) as f:
        file_context = f.read()
        # print("the file context is {}".format(file_context))
    if not file_path:
        logger.error("file doesn't exist, pass")
        return
    file_tree = parser.parse(bytes(file_context, 'utf8')).root_node
    return DFS_tree_get_type(file_tree, "method_declaration")
'''


if __name__ == "__main__":
    import json
    out_lists = evosuite_list_classes(project_dir=base_v30_dir,
                                      evo_jar_loc="/Users/yunruipei/Desktop/list_method/evosuite-1.2.0.jar",
                                      target="target/classes/org/apache/commons/jexl3/internal") #记得evosuite_list_classes函数里evosuite.jar的location更新一下
    single_class_list = {}
    cnt = 0
    for single_class in out_lists:
        logger.info("========now checking class: {}=======".format(single_class))

        # 这一段只是拿oracle的，也不需要了
        # a = get_evosuite_test_body(base_v30_dir, pkg="com/google/common/collect", class_name=single_class)
        # for i in a:
        #     obtain_oracle_from_test_code(i) # 不需要

        # dir_part1 = base_v30_dir, dir_part2 = "guava/src", pkg = "com/google/common/collect", class_file = "AbstractMapBasedMultiset.java"
        # v30_method_id_code_list = get_id_code_map_of_functions_from_source_code(base_v30_dir, dir_part2="src", pkg="main/java/org/jsoup/select", class_file=single_class+".java")
        v30_method_id_code_list = get_id_code_map_of_functions_from_source_code(base_v30_dir, dir_part2="src",
                                                                                pkg="main/java/org/apache/commons/jexl3/internal",
                                                                                class_file="TemplateDebugger.java")
        for k, v in v30_method_id_code_list.items():
            logger.info("===method name: {}".format(k))
            # with open(f"method2.txt", "a+") as f:
            #     f.write(f"{k} \n")
            for z in v:
                logger.info("===method body: {}".format(z.text.decode('utf-8')))
                single_class_list[k] = z.text.decode('utf-8')
                cnt += 1
                # with open(f"method2.txt", "a+") as f:
                #     f.write(f"{z.text.decode('utf-8')} \n")
        with open(f"MTemplateDebugger1.json", "w", encoding="utf-8") as f:
            json.dump(single_class_list, f, ensure_ascii=False, indent=4)
        break
