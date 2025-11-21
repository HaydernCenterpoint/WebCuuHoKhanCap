import re
import json

def parse_rescue_data_new_format(input_file):
    """Parse dữ liệu cứu hộ từ file text với format mới có cột mức độ ưu tiên"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    rescue_cases = []
    current_id = 1
    
    # Phone pattern
    phone_pattern = r'0[\d\s\.]{8,}'
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Bỏ qua các dòng tiêu đề hoặc dòng trống
        if not line or 'Mức độ ưu tiên' in line or 'CHỖ NÀO CHƯA ỔN' in line:
            continue
        
        # Parse theo format: Mức độ | Khu vực | Số người | Địa chỉ/Tình hình | SĐT
        parts = line.split('\t') if '\t' in line else [line]
        
        # Xác định priority từ dòng
        priority = 'MEDIUM'
        if 'khẩn cấp' in line.lower():
            priority = 'CRITICAL'
        elif 'ưu tiên cao' in line.lower():
            priority = 'HIGH'
        elif 'thường' in line.lower():
            priority = 'MEDIUM'
        
        # Tách số điện thoại
        phones = []
        phone_matches = re.findall(phone_pattern, line)
        
        for phone in phone_matches:
            clean_phone = re.sub(r'[^\d]', '', phone)
            if len(clean_phone) >= 9 and len(clean_phone) <= 11:
                if len(clean_phone) == 10:
                    formatted = f"{clean_phone[:4]} {clean_phone[4:7]} {clean_phone[7:]}"
                elif len(clean_phone) == 9:
                    formatted = f"{clean_phone[:3]} {clean_phone[3:6]} {clean_phone[6:]}"
                else:
                    formatted = clean_phone
                phones.append(formatted)
        
        # Loại bỏ số điện thoại và priority keywords để lấy content
        content = line
        for phone_match in phone_matches:
            content = content.replace(phone_match, '')
        content = re.sub(r'(Khẩn cấp|Ưu tiên cao|Thường)', '', content, flags=re.IGNORECASE)
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content).strip()
        content = re.sub(r'^[^\w]+', '', content)
        
        if not content or len(content) < 10:
            continue
        
        # Xác định khu vực
        area = 'Khác'
        area_keywords = {
            'Bàn Thạch': 'Bàn Thạch',
            'Bắc Nha Trang': 'Bắc Nha Trang',
            'Bệnh Viện Đường Sắt': 'Bệnh Viện Đường Sắt',
            'Bình Khánh': 'Bình Khánh',
            'Cầu Bè': 'Cầu Bè',
            'Cầu Dứa': 'Cầu Dứa',
            'Cầu Gỗ': 'Cầu Gỗ',
            'Cầu Ké': 'Cầu Ké',
            'Cây Dầu Đôi': 'Cây Dầu Đôi',
            'Diên Điền': 'Diên Điền',
            'Diên Khánh': 'Diên Khánh',
            'Diên Phú': 'Diên Phú',
            'Gò Cây Sung': 'Gò Cây Sung',
            'Lương Định Của': 'Vĩnh Ngọc',
            'Phú Nông': 'Phú Nông',
            'Tây Nha Trang': 'Vĩnh Ngọc',
            'Vĩnh Hiệp': 'Vĩnh Hiệp',
            'Vĩnh Ngọc': 'Vĩnh Ngọc',
            'Vĩnh Phương': 'Vĩnh Phương',
            'Vĩnh Thái': 'Vĩnh Thái',
            'Vĩnh Thạnh': 'Vĩnh Thạnh',
            'Vĩnh Trung': 'Vĩnh Trung',
        }
        
        for keyword, area_name in area_keywords.items():
            if keyword.lower() in content.lower():
                area = area_name
                break
        
        # Tạo case
        case = {
            "id": current_id,
            "content": content,
            "phones": phones,
            "area": area,
            "priority": priority,
            "isRescued": False
        }
        
        rescue_cases.append(case)
        current_id += 1
    
    return rescue_cases

# Parse dữ liệu
data = parse_rescue_data_new_format('pdf_content.txt')

# Thống kê
priority_counts = {}
area_counts = {}

for case in data:
    priority = case['priority']
    priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    area = case['area']
    area_counts[area] = area_counts.get(area, 0) + 1

print(f"✅ Tổng số ca: {len(data)}")
print(f"\n📊 Thống kê theo mức độ ưu tiên:")
for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    count = priority_counts.get(priority, 0)
    if count > 0:
        print(f"  {'🚨' if priority == 'CRITICAL' else '⚠️' if priority == 'HIGH' else '📝'} {priority}: {count} ca ({count/len(data)*100:.1f}%)")

print(f"\n🗺️ Thống kê theo khu vực (Top 10):")
for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {area}: {count} ca")

# Lưu vào file JSON
output_file = 'rescue-app/src/data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Đã lưu {len(data)} ca vào {output_file}")

# Hiển thị 5 ca CRITICAL đầu tiên
print(f"\n🚨 Top 5 ca CRITICAL:")
critical_cases = [c for c in data if c['priority'] == 'CRITICAL'][:5]
for i, case in enumerate(critical_cases, 1):
    phones_str = ', '.join(case['phones'][:2]) if case['phones'] else '(Không có SĐT)'
    print(f"\n{i}. [{case['area']}] {case['content'][:100]}...")
    print(f"   📞 {phones_str}")
