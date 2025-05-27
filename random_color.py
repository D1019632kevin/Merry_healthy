# random_color.py
import random

_colors = {} # 用於存儲為每個類別生成的顏色，以便顏色保持一致

def get_random_color(key):
    """
    為給定的 'key'（通常是類別名稱）生成或返回一個隨機的 RGB 顏色。
    如果 'key' 已經有顏色，則返回該顏色；否則生成一個新顏色並存儲。
    """
    if key not in _colors:
        # 生成一個隨機的 BGR 顏色元組 (OpenCV 使用 BGR 格式)
        _colors[key] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return _colors[key]
