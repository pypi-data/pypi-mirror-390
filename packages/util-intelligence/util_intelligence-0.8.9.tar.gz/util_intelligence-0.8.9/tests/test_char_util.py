import unicodedata

from util_intelligence.char_util import convert_to_simplified_chinese


def test_traditional_to_simplified():
    # 繁体 -> 简体
    traditional = "繁體中文測試：學習、電腦、資訊、國際、歷史、傳統"
    simplified = convert_to_simplified_chinese(traditional)
    assert "繁体中文测试" in simplified
    assert "学习" in simplified
    assert "电脑" in simplified
    assert "信息" in simplified or "资讯" not in simplified  # 根据词库可能为“信息”或“资讯”


def test_already_simplified_is_idempotent():
    # 已经是简体，转换应保持语义不变
    text = "简体中文测试：学习、电脑、信息、国际、历史、传统"
    out = convert_to_simplified_chinese(text)
    # OpenCC 转换后字符应仍为简体（允许全角/兼容规范化差异）
    assert unicodedata.normalize("NFC", out) == unicodedata.normalize("NFC", text)


