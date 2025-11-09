import unittest
from hachi64 import hachi64, Hachi64

class TestHachi64(unittest.TestCase):

    def test_encode_decode_consistency(self):
        """测试编码和解码的一致性"""
        test_cases = [
            b"Hello, World!",
            b"rust", 
            b"a",
            b"ab", 
            b"abc",
            b"Python",
            b"Hachi64",
            b"",  # 空字符串
            b"The quick brown fox jumps over the lazy dog"
        ]
        
        for test_data in test_cases:
            with self.subTest(data=test_data):
                # 测试新的 hachi64.encode/decode 格式
                encoded = hachi64.encode(test_data)
                decoded = hachi64.decode(encoded)
                self.assertEqual(decoded, test_data, 
                               f"编码解码不一致: {test_data} -> {encoded} -> {decoded}")

    def test_class_methods(self):
        """测试类方法调用"""
        test_data = b"Hello, World!"
        
        # 测试类静态方法
        encoded_static = Hachi64.encode(test_data)
        decoded_static = Hachi64.decode(encoded_static)
        
        # 测试实例方法
        encoded_instance = hachi64.encode(test_data)
        decoded_instance = hachi64.decode(encoded_instance)
        
        # 两种方式应该得到相同结果
        self.assertEqual(encoded_static, encoded_instance)
        self.assertEqual(decoded_static, decoded_instance)
        self.assertEqual(decoded_static, test_data)

    def test_specific_encodings(self):
        """测试特定的编码结果，确保使用中文字母表"""
        # 这些是使用中文字母表的预期结果
        test_cases = [
            (b"Hello", "豆米啊拢嘎米多="),
            (b"abc", "西阿南呀"),
            (b"a", "西律=="),
            (b"ab", "西阿迷=")
        ]
        
        for test_data, expected in test_cases:
            with self.subTest(data=test_data):
                # 使用新的 hachi64.encode 格式
                encoded = hachi64.encode(test_data)
                self.assertEqual(encoded, expected, 
                               f"编码结果不匹配: {test_data} -> 期望 {expected}, 实际 {encoded}")

    def test_binary_data(self):
        """测试二进制数据的编码解码"""
        test_data = bytes(range(256))  # 0-255的所有字节值
        encoded = hachi64.encode(test_data)
        decoded = hachi64.decode(encoded)
        self.assertEqual(decoded, test_data, "二进制数据编码解码失败")

    def test_no_padding_encode_decode(self):
        """测试无填充编码解码"""
        test_cases = [b"a", b"ab", b"abc", b"Hello"]
        
        for test_data in test_cases:
            with self.subTest(data=test_data):
                encoded_no_pad = hachi64.encode(test_data, padding=False)
                decoded = hachi64.decode(encoded_no_pad, padding=False)
                self.assertEqual(decoded, test_data, 
                               f"无填充编码解码不一致: {test_data} -> {encoded_no_pad} -> {decoded}")

    def test_padding_behavior(self):
        """测试填充行为"""
        # 测试有填充和无填充的区别
        test_data = b"a"
        
        encoded_with_padding = hachi64.encode(test_data, padding=True)
        encoded_without_padding = hachi64.encode(test_data, padding=False)
        
        # 有填充的应该有 == 结尾
        self.assertTrue(encoded_with_padding.endswith("=="), 
                       f"有填充编码应该以==结尾: {encoded_with_padding}")
        
        # 无填充的不应该有 = 
        self.assertNotIn("=", encoded_without_padding,
                        f"无填充编码不应该包含=: {encoded_without_padding}")
        
        # 两种方式解码应该都能得到原始数据
        decoded_with_padding = hachi64.decode(encoded_with_padding, padding=True)
        decoded_without_padding = hachi64.decode(encoded_without_padding, padding=False)
        
        self.assertEqual(decoded_with_padding, test_data)
        self.assertEqual(decoded_without_padding, test_data)

    def test_decode_invalid_input(self):
        """测试解码无效输入"""
        # 测试包含不在字母表中的字符
        with self.assertRaises(ValueError):
            hachi64.decode("包含无效字符X的字符串")
        
        # 测试空字符串
        result = hachi64.decode("")
        self.assertEqual(result, b"", "空字符串应该解码为空字节")

    def test_alphabet_coverage(self):
        """测试字母表的覆盖率 - 确保所有64个字符都能被使用"""
        from hachi64 import HACHI_ALPHABET
        
        # 验证字母表长度
        self.assertEqual(len(HACHI_ALPHABET), 64, "字母表长度应该为64")
        
        # 验证字母表无重复字符
        self.assertEqual(len(set(HACHI_ALPHABET)), 64, "字母表应该包含64个唯一字符")
        
        # 测试长数据以确保所有字符都可能被使用
        long_data = bytes(range(256)) * 3  # 较长的测试数据
        encoded = hachi64.encode(long_data)
        decoded = hachi64.decode(encoded)
        self.assertEqual(decoded, long_data, "长数据编码解码应该一致")

if __name__ == '__main__':
    unittest.main()
