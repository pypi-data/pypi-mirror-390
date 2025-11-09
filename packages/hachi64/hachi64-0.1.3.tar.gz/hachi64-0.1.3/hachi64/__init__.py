"""
Hachi64: 哈吉米64 Encoding and Decoding
"""

# HACHI_ALPHABET="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
HACHI_ALPHABET="哈蛤呵吉急集米咪迷南男难北背杯绿律虑豆斗抖啊阿额西希息嘎咖伽花华哗压鸭呀库酷苦奶乃耐龙隆拢曼慢漫波播玻叮丁订咚东冬囊路陆多都弥济"


class Hachi64:
    """Hachi64 编解码器类"""
    
    @staticmethod
    def encode(data: bytes, padding: bool = True) -> str:
        """
        Encodes a byte string into a Hachi64 string using the specified alphabet.

        :param data: The bytes to encode.
        :param padding: Whether to use '=' for padding.
        :return: The encoded string.
        """
        alphabet: str = HACHI_ALPHABET
        result = []
        data_len = len(data)
        i = 0

        while i < data_len:
            chunk = data[i:i+3]
            i += 3

            byte1 = chunk[0]
            byte2 = chunk[1] if len(chunk) > 1 else 0
            byte3 = chunk[2] if len(chunk) > 2 else 0

            idx1 = byte1 >> 2
            idx2 = ((byte1 & 0x03) << 4) | (byte2 >> 4)
            idx3 = ((byte2 & 0x0F) << 2) | (byte3 >> 6)
            idx4 = byte3 & 0x3F

            result.append(alphabet[idx1])
            result.append(alphabet[idx2])

            if len(chunk) > 1:
                result.append(alphabet[idx3])
            elif padding:
                result.append('=')

            if len(chunk) > 2:
                result.append(alphabet[idx4])
            elif padding:
                result.append('=')
        
        return "".join(result)

    @staticmethod
    def decode(encoded_str: str, padding: bool = True) -> bytes:
        """
        Decodes a Hachi64 string into bytes using the specified alphabet.

        :param encoded_str: The string to decode.
        :param padding: Whether the input string uses '=' for padding.
        :return: The decoded bytes.
        :raises ValueError: If the input string is invalid.
        """
        alphabet: str = HACHI_ALPHABET
        reverse_map = {char: i for i, char in enumerate(alphabet)}

        # 处理空字符串
        if not encoded_str:
            return b""

        pad_count = 0
        if padding:
            pad_count = encoded_str.count('=')
            if pad_count > 0:
                encoded_str = encoded_str[:-pad_count]

        result = bytearray()
        data_len = len(encoded_str)
        i = 0

        while i < data_len:
            chunk = encoded_str[i:i+4]
            i += 4

            try:
                idx1 = reverse_map[chunk[0]]
                idx2 = reverse_map[chunk[1]] if len(chunk) > 1 else 0
                idx3 = reverse_map[chunk[2]] if len(chunk) > 2 else 0
                idx4 = reverse_map[chunk[3]] if len(chunk) > 3 else 0
            except KeyError as e:
                raise ValueError(f"Invalid character in input: {e}") from e

            byte1 = (idx1 << 2) | (idx2 >> 4)
            result.append(byte1)
            
            if len(chunk) > 2:
                byte2 = ((idx2 & 0x0F) << 4) | (idx3 >> 2)
                result.append(byte2)
                
            if len(chunk) > 3:
                byte3 = ((idx3 & 0x03) << 6) | idx4
                result.append(byte3)

        # 根据填充移除多余的字节
        # pad_count = 1 表示原始数据是 3n+2 字节，需要移除 0 字节
        # pad_count = 2 表示原始数据是 3n+1 字节，需要移除 0 字节
        # 实际上，填充不影响解码后的字节数，因为编码过程中的填充处理已经正确
        
        return bytes(result)


# 创建默认实例以支持直接调用
hachi64 = Hachi64()

# 导出所有可用的接口
__all__ = ['Hachi64', 'hachi64', 'HACHI_ALPHABET']
