import json
import re
from collections import Counter

def analyze_others():
    with open('rescue-app/src/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    others = [item for item in data if item['area'] == 'Khác']
    print(f"Tổng số ca 'Khác': {len(others)}")
    
    # Phân tích từ khóa trong content của 'Khác'
    words = []
    for item in others:
        # Lấy 10 từ đầu tiên của content (thường là địa chỉ)
        content = item['content'].lower()
        # Loại bỏ các từ thông thường
        content = re.sub(r'khẩn cấp|ưu tiên|cần|cứu|hộ|người|nhà|bị|ngập|nước|lên|cao|số|điện|thoại|liên|hệ', '', content)
        tokens = re.findall(r'\b\w+\b', content)
        words.extend(tokens)
    
    # Đếm các từ xuất hiện nhiều nhất (gợi ý tên đường/thôn/xã)
    common_words = Counter(words).most_common(50)
    print("\nTop từ khóa xuất hiện trong 'Khác':")
    for word, count in common_words:
        if len(word) > 2: # Bỏ từ quá ngắn
            print(f"{word}: {count}")

    # Kiểm tra Priority của 'Khác'
    priorities = Counter([item['priority'] for item in others])
    print(f"\nPhân bố Priority trong 'Khác': {priorities}")

    # In mẫu 10 ca 'Khác' đầu tiên
    print("\nMẫu 10 ca 'Khác':")
    for item in others[:10]:
        print(f"- [{item['priority']}] {item['content'][:100]}...")

if __name__ == "__main__":
    analyze_others()
