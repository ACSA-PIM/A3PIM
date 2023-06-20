
import re
import json

def abstractBBLfromAssembly(assembly):
    bblFile = assembly[:-2] + ".bbl"
    bblJsonFile = assembly[:-2] + "_bbl.json"
    tmpbblFile = assembly[:-2] + ".tmp"
    ic(bblFile)
    
    # 打开x86汇编代码文件
    with open(assembly) as f:
        # 读取文件内容
        content = f.read()
    
    # 使用正则表达式匹配所有汇编指令
    pattern = r' 	(\b[a-zA-Z0-9]{2,7}\b.*)'
    matches = re.findall(pattern, content)
    with open(tmpbblFile, 'w') as f:
        # 输出匹配结果
        for match in matches:
            f.write(match + '\n')
    
    bblHashDict = dict()
    matchStep = "none"
    tmpHigherHash='0'
    tmpLowerHash='0'
    tmpBBL = []
    with open(bblFile, 'w') as f:
        for match in matches:
            if match == "mov    $0x400,%rax":
                matchStep="bbl start"
            elif matchStep=="bbl start":
                matchhigher = re.match(r"movabs \$0x(.*),%rbx",match)
                # ic(matchhigher.groups(1))
                if matchhigher is not None:
                    matchStep="bbl higher hash"
                    tmpHigherHash=str(matchhigher.groups(1))[2:-3]
                else:
                    matchStep="none"
            elif matchStep=="bbl higher hash":
                matchLower = re.match(r"movabs \$0x([a-f0-9]*),%rcx",match)
                if matchLower is not None:
                    matchStep="bbl Lower hash"
                    tmpLowerHash=str(matchLower.groups(1))[2:-3]
                else:
                    matchStep="none"
            elif matchStep=="bbl Lower hash":
                if match == "xchg   %bx,%bx":
                    matchStep="record"
                    tmpBBL = []
                else:
                    matchStep="none"
            elif matchStep=="record":
                if match == "mov    $0x401,%rax":
                    matchStep="bblend start"
                else:
                    matchStep="record"
                    tmpBBL.append(match)
                    # ic(tmpBBL)
            elif matchStep=="bblend start":
                matchhigher = re.match(r"movabs \$0x([a-f0-9]*),%rbx",match)
                if matchhigher is not None :
                    toMatchHigherHash=str(matchhigher.groups(1))[2:-3]
                    if toMatchHigherHash==tmpHigherHash:
                        matchStep="bblend higher hash"
                else:
                    matchStep="none"
            elif matchStep=="bblend higher hash":
                matchLower = re.match(r"movabs \$0x([a-f0-9]*),%rcx",match)
                if matchLower is not None:
                    toMatchLowerHash=str(matchLower.groups(1))[2:-3]
                    if toMatchLowerHash==tmpLowerHash:
                        matchStep="bblend Lower hash"
                else:
                    matchStep="none"
            # ic(match, matchStep)    
            if matchStep=="bblend Lower hash":
                # bblHashDict[(tmpHigherHash,tmpLowerHash)]=tmpBBL
                bblHashDict[tmpHigherHash + "  " + tmpLowerHash]=tmpBBL
                # ic(tmpHigherHash)
                f.write('Hash ' + tmpHigherHash + '  ' + tmpLowerHash+'\n')
                for inst in tmpBBL:
                    f.write(inst+'\n')
                f.write('\n')
                # ic(bblHashDict)
                tmpBBL = []
                matchStep="none"
    
    # json.dump()` 无法序列化 Python 中元组(tuple)作为字典的 key，这会导致 `json.dump()` 函数在写入此类字典数据时会进入死循环或陷入卡住状态，
    # 因为无法完全处理输入的数据。通常情况下，使用元组作为字典键值是一种不常见的做法，因为字典的键值必须是可散列对象，也即是说必须是不可变的对象。
    with open(bblJsonFile, 'w') as f:
        json.dump(bblHashDict, f)
    
    return bblHashDict

    # # 加载 dict
    # with open('data.json', 'r') as f:
    #     data = json.load(f)

    # # 将键从列表转换为元组
    # bbl_dict = {tuple(k): v for k, v in data.items()}

