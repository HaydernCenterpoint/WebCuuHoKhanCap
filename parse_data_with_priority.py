import re
import json

def determine_priority(content, phones_count):
    """
    Xác định mức độ ưu tiên dựa trên các yếu tố:
    - CRITICAL (Khẩn cấp): Có trẻ em nhỏ, người già yếu, bệnh nặng, nước gần/qua đầu, lên mái
    - HIGH (Cao): Có nhiều người, người già, trẻ em, nước cao 
    - MEDIUM (Trung bình): Tình trạng bình thường
    - LOW (Thấp): Không có thông tin chi tiết
    """
    content_lower = content.lower()
    
    # CRITICAL factors
    critical_keywords = [
        'lên mái', 'trên mái', 'leo mái', 'qua đầu', 'gần lút', 'gần mái', 
        'lút nó',
        'mất liên lạc', 'pin hết', 'gần hết pin',
        'bệnh nặng', 'tai biến', 'chạy thận', 'không đi lại',
        'bà bầu', 'mới đẻ', 'sơ sinh',
        'em bé', 'bé nhỏ', 'con nít', 'trẻ nhỏ', 'cháu nhỏ',
        'khẩn cấp', 'khẩn thiết', 'gấp'
    ]
    
    # HIGH factors  
    high_keywords = [
        'người già', 'lớn tuổi', '70t', '80t', '90t', '97 tuổi',
        'trẻ em', '1t', '2t', '3t', '4t', '5t',
        'nước dâng', 'ngập sâu', 'ngang ngực', 'tới ngực',
        'thiếu lương thực', 'thiếu nước', 'hết đồ ăn'
    ]
    
    # Check CRITICAL
    for keyword in critical_keywords:
        if keyword in content_lower:
            return 'CRITICAL'
    
    # Check for specific numbers indicating danger
    if re.search(r'nước.{0,30}(2|3|4) ?m', content_lower):
        return 'CRITICAL'
    
    # Check HIGH
    for keyword in high_keywords:
        if keyword in content_lower:
            return 'HIGH'
    
    # Check number of people
    people_match = re.search(r'(\d+)\s*(người|em|đứa|con)', content_lower)
    if people_match:
        num_people = int(people_match.group(1))
        if num_people >= 5:
            return 'HIGH'
    
    # If has phone number, at least MEDIUM
    if phones_count > 0:
        return 'MEDIUM'
    
    return 'LOW'

def parse_rescue_data(input_file):
    """Parse dữ liệu cứu hộ từ file text"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    rescue_cases = []
    current_id = 1
    
    # Phone pattern - nhiều định dạng
    phone_pattern = r'0[\d\s\.]{8,}'
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Bỏ qua các dòng tiêu đề hoặc dòng trống
        if not line or 'Địa chỉ/Tình hình' in line or 'Số điện thoại' in line:
            continue
        
        # Tách nội dung và số điện thoại
        # Format: Địa chỉ/Tình hình + Số điện thoại (có thể nhiều số)
        
        phones = []
        phone_matches = re.findall(phone_pattern, line)
        
        for phone in phone_matches:
            # Chuẩn hóa số điện thoại
            clean_phone = re.sub(r'[^\d]', '', phone)
            if len(clean_phone) >= 9 and len(clean_phone) <= 11:
                # Format lại: 0xxx xxx xxx
                if len(clean_phone) == 10:
                    formatted = f"{clean_phone[:4]} {clean_phone[4:7]} {clean_phone[7:]}"
                elif len(clean_phone) == 9:
                    formatted = f"{clean_phone[:3]} {clean_phone[3:6]} {clean_phone[6:]}"
                else:
                    formatted = clean_phone
                phones.append(formatted)
        
        # Loại bỏ số điện thoại khỏi content để lấy địa chỉ/tình hình
        content = line
        for phone_match in phone_matches:
            content = content.replace(phone_match, '')
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content).strip()
        content = re.sub(r'^[^\w]+', '', content)  # Remove leading symbols
        content = re.sub(r'[^\w\s,./\-()]+$', '', content)  # Remove trailing symbols
        
        if not content:
            continue
        
        # Xác định khu vực từ nội dung
        area = 'Khác'
        if 'vĩnh thạnh' in content.lower():
            area = 'Vĩnh Thạnh'
        elif 'vĩnh ngọc' in content.lower() or 'tây nha trang' in content.lower():
            area = 'Vĩnh Ngọc'
        elif 'vĩnh thái' in content.lower():
            area = 'Vĩnh Thái'
        elif 'vĩnh trung' in content.lower():
            area = 'Vĩnh Trung'
        elif 'vĩnh hiệp' in content.lower():
            area = 'Vĩnh Hiệp'
        elif 'vĩnh phương' in content.lower():
            area = 'Vĩnh Phương'
        elif 'diên điền' in content.lower() or 'diên phú' in content.lower():
            area = 'Diên Phú'
        elif 'diên khánh' in content.lower():
            area = 'Diên Khánh'
        elif 'phú nông' in content.lower():
            area = 'Phú Nông'
        elif 'cầu bè' in content.lower() or 'cầu ké' in content.lower():
            area = 'Vĩnh Thạnh'
        elif 'lương định của' in content.lower():
            area = 'Vĩnh Ngọc'
        
        # Xác định mức độ ưu tiên
        priority = determine_priority(content, len(phones))
        
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
data = parse_rescue_data('pdf_content.txt')

# Thống kê
priority_counts = {}
area_counts = {}

for case in data:
    # Count priorities
    priority = case['priority']
    priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    # Count areas
    area = case['area']
    area_counts[area] = area_counts.get(area, 0) + 1

print(f"Tổng số ca: {len(data)}")
print(f"\nThống kê theo mức độ ưu tiên:")
for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    count = priority_counts.get(priority, 0)
    print(f"  {priority}: {count} ca ({count/len(data)*100:.1f}%)")

print(f"\nThống kê theo khu vực:")
for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True):
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
    print(f"\n{i}. [{case['area']}] {case['content'][:80]}...")
    print(f"   📞 {', '.join(case['phones'][:2])}")
