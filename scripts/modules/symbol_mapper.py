import hashlib

# 39 种图片的真实32位MD5映射表
EXACT_SYMBOL_MAP = {
    # 核心判断符号
    "4f331316478f5068767a82038a5fcfba": {"type": "correct", "char": "✅", "verdict": "correct", "desc": "正确判断"},
    "edbe0ddccc19a98ede6835a5fea465b1": {"type": "wrong", "char": "❌", "verdict": "wrong", "desc": "错误判断"},
    "414e035a249baccee70285e20024042d": {"type": "distinction", "char": "⚠️", "verdict": None, "desc": "辨析标志"},
    
    # 序号
    "6f654c353441134b957e837160ea5548": {"type": "num", "char": "①", "verdict": None, "desc": "序号一"},
    "ab58018ad40da0039698d5e8a56647d9": {"type": "num", "char": "②", "verdict": None, "desc": "序号二"},
    "d9e789d819f4ab475c1331a034145770": {"type": "num", "char": "③", "verdict": None, "desc": "序号三"},
    "3708dab7797c7b32f9c219e000d3e65f": {"type": "num", "char": "④", "verdict": None, "desc": "序号四"},
    "15005b6e949cd24f936215a9a7e93dd4": {"type": "num", "char": "⑤", "verdict": None, "desc": "序号五"},
    
    # 指示与常见符号
    "231ee37262e1e995778b2acfc2852b57": {"type": "arrow", "char": "➔", "verdict": None, "desc": "右箭头指示"},
    "1d4035951a919df5fda380f42ca89be6": {"type": "arrow", "char": "➔", "verdict": None, "desc": "右箭头"},
    "ce2cc459b3fe88771794fe2b464e54af": {"type": "bullet", "char": "•", "verdict": None, "desc": "项目圆点"},
    "720cb05be80e0c904fa77943d0fca8a4": {"type": "arrow_down", "char": "⬇️", "verdict": None, "desc": "向下指示"},
    "f16f36420e3de6c53738616f8d80b3ab": {"type": "arrow_up", "char": "⬆️", "verdict": None, "desc": "向上指示"},
    "cec859d4dfbb2001f7cd37734d035811": {"type": "arrow_curve", "char": "⤴️", "verdict": None, "desc": "换算箭头"},
    "24632bb503eaca8ec160b8633cae6adc": {"type": "exclamation", "char": "❗", "verdict": None, "desc": "感叹标"},
    "11cdfba81bee167871a3b1d09e28f8ba": {"type": "triangle", "char": "▲", "verdict": None, "desc": "三角标"},
    "49aac237900c808033d3e7a0ded9f9c1": {"type": "star", "char": "⭐", "verdict": None, "desc": "重点星标"},
    "45c7a4f6a76afaeaaab83e7b31e35fac": {"type": "circle", "char": "⭕", "verdict": None, "desc": "大圆圈"},
    "0660917c5b7ac5cc065950030302db40": {"type": "flag", "char": "🚩", "verdict": None, "desc": "红旗标"},
    "4bae4bda59f8f5fd5ffcf7e9e3bb6436": {"type": "lightbulb", "char": "💡", "verdict": None, "desc": "灯泡"},
    
    # 助记图案
    "0516485bd1dce29f34fa082d19c8a898": {"type": "mnemonic", "char": "{直升机}", "verdict": None, "desc": "牢二枢纽直升机"},
    "5a9490a12d44beb9e7746e1a94426828": {"type": "mnemonic", "char": "{鸡}", "verdict": None, "desc": "偷鸡心虚虚空鸡"},
    "e380284efa1fbd56310cd5f8f4fcfe1d": {"type": "mnemonic", "char": "{俄国国旗}", "verdict": None, "desc": "十月革命俄国国旗"},
    "168dcc0bc57d714b82bfe6874f43e862": {"type": "mnemonic", "char": "{人像}", "verdict": None, "desc": "历史人物图标"},
    "40aaf32abfc71ea9500e34c32d8d20e5": {"type": "mnemonic", "char": "{帽子人物}", "verdict": None, "desc": "国际寡妇助记"},
    "6cb1e12616262e72dadbc1257ec66830": {"type": "mnemonic", "char": "{生子}", "verdict": None, "desc": "生孩子助记"},
    "940abc17f526e6beac695add820827ae": {"type": "mnemonic", "char": "{机器多了}", "verdict": None, "desc": "技术构成机器多"},
    "fdf97e4e7d1a6bea4fd877d0e40d31c7": {"type": "mnemonic", "char": "{工人少了}", "verdict": None, "desc": "有机构成工人少"},
    "7057fa3e3ce5ecba32cac43eb4565e73": {"type": "mnemonic", "char": "{威海技师}", "verdict": None, "desc": "威海技师洋务"},
    "5f2f87becb22c2ab56431d205ab73ab3": {"type": "symbol", "char": "{工农革命旗}", "verdict": None, "desc": "秋收起义旗帜"},
    "87dd47b6f4ca93850f0130dc659c77a0": {"type": "symbol", "char": "{民主政权标}", "verdict": None, "desc": "赞成抗日民主"},
    "99386d902eb6272b3c82bc3a6e1e022f": {"type": "book", "char": "{著作:书标}", "verdict": None, "desc": "毛泽东著作标志"},
    "12d6fc3c71073f73b549fd983c0c7f88": {"type": "book", "char": "{著作:飞标}", "verdict": None, "desc": "论联合政府标志"},
    "cd54f7c7ed776f063a883f04b9aa270a": {"type": "book", "char": "{著作:章标}", "verdict": None, "desc": "毛泽东著作奖章"},
    "5b175efae41e61ff41f9a7e91b6e8ccb": {"type": "symbol", "char": "{高质量发展标}", "verdict": None, "desc": "高质量发展"},
    "34df7d1a3b49696a8c06d78d0079121c": {"type": "symbol", "char": "{全面依法治国标}", "verdict": None, "desc": "全面依法治国"},
    "b7e1a94be66a6858d0f7db1457cc7ce0": {"type": "symbol", "char": "{变动标}", "verdict": None, "desc": "构成变动"},
    "e4fa63d9756f3f7ae302ec676fabf054": {"type": "symbol", "char": "{发展标}", "verdict": None, "desc": "继续发展"},
    
    # 史纲大图
    "43c4d91bcb98a6796c0cd5ce82b2089b": {"type": "full_diagram", "char": "{史纲整体脉络图}", "verdict": None, "desc": "史纲全景时间线大图"}
}

# 8字符前缀备份索引
PREFIX_MAP = {k[:8]: v for k, v in EXACT_SYMBOL_MAP.items()}

def get_symbol_by_hash(img_bytes):
    """根据图片字节计算MD5并获取对应符号定义"""
    h = hashlib.md5(img_bytes).hexdigest()
    if h in EXACT_SYMBOL_MAP:
        mapping = dict(EXACT_SYMBOL_MAP[h])
        mapping["hash"] = h
        return mapping
    elif h[:8] in PREFIX_MAP:
        mapping = dict(PREFIX_MAP[h[:8]])
        mapping["hash"] = h
        return mapping
    return {
        "hash": h,
        "type": "unknown",
        "char": f"{{unknown_symbol:{h[:8]}}}",
        "verdict": None,
        "desc": "未登记未知符号"
    }
