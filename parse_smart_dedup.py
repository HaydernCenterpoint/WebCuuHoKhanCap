import re
import json
from difflib import SequenceMatcher

def normalize_text(text):
    """Chuẩn hóa text để so sánh"""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def normalize_phone(phone):
    """Chuẩn hóa số điện thoại"""
    return re.sub(r'\D', '', phone)

def similarity(a, b):
    """Tính độ tương đồng giữa 2 chuỗi"""
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()

def extract_address_core(content):
    """Trích xuất phần địa chỉ cốt lõi từ content"""
    # Loại bỏ phần mô tả tình trạng
    address = re.split(r'[–\-—:]\s*', content)[0]
    # Loại bỏ số lượng người
    address = re.sub(r'\d+\s*(người|em|bé|cháu|đứa|con)', '', address)
    # Lấy phần đầu (thường là địa chỉ)
    words = address.split()
    if len(words) > 10:
        address = ' '.join(words[:10])
    return normalize_text(address)

def is_duplicate(case1, case2, phone_threshold=0.5, address_threshold=0.7):
    """Kiểm tra 2 case có trùng lặp không"""
    # Check phone numbers
    phones1 = set([normalize_phone(p) for p in case1['phones']])
    phones2 = set([normalize_phone(p) for p in case2['phones']])
    
    if phones1 and phones2:
        common_phones = phones1.intersection(phones2)
        if len(common_phones) > 0:
            return True
    
    # Check address similarity
    addr1 = extract_address_core(case1['content'])
    addr2 = extract_address_core(case2['content'])
    
    if addr1 and addr2 and len(addr1) > 5 and len(addr2) > 5:
        sim = similarity(addr1, addr2)
        if sim >= address_threshold:
            return True
    
    return False

def merge_duplicates(cases):
    """Gộp các case trùng lặp, giữ lại case có priority cao nhất"""
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    
    unique_cases = []
    skip_indices = set()
    
    for i, case in enumerate(cases):
        if i in skip_indices:
            continue
        
        # Find all duplicates of this case
        duplicates = [case]
        for j in range(i + 1, len(cases)):
            if j in skip_indices:
                continue
            if is_duplicate(case, cases[j]):
                duplicates.append(cases[j])
                skip_indices.add(j)
        
        # Merge duplicates: keep the one with highest priority
        if len(duplicates) > 1:
            best = min(duplicates, key=lambda c: priority_order.get(c['priority'], 99))
            
            # Merge phone numbers
            all_phones = set()
            for dup in duplicates:
                all_phones.update(dup['phones'])
            best['phones'] = sorted(list(all_phones))[:5]  # Keep max 5 phones
            
            unique_cases.append(best)
        else:
            unique_cases.append(case)
    
    return unique_cases

def parse_priority_from_line(line):
    """Trích xuất mức độ ưu tiên từ dòng"""
    line_lower = line.lower()
    if 'khẩn cấp' in line_lower:
        return 'CRITICAL'
    elif 'ưu tiên cao' in line_lower:
        return 'HIGH'
    elif 'thường' in line_lower:
        return 'MEDIUM'
    return None

def parse_rescue_data_smart(input_file):
    """Parse dữ liệu cứu hộ với lọc trùng lặp thông minh"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    raw_cases = []
    current_id = 1
    
    # Phone pattern
    phone_pattern = r'0[\d\s\.]{8,}'
    
    # Danh sách khu vực đầy đủ
    area_keywords = {
        'Bàn Thạch': 'Bàn Thạch',
        'Bắc Nha Trang': 'Bắc Nha Trang',
        'Bệnh Viện Đường Sắt': 'BV Đường Sắt',
        'Bệnh viện đường sắt': 'BV Đường Sắt',
        'Bình Khánh': 'Bình Khánh',
        'Cầu Bè': 'Cầu Bè',
        'Cầu Dứa': 'Cầu Dứa',
        'Cầu Gỗ': 'Cầu Gỗ',
        'Cầu Ké': 'Cầu Ké',
        'Cây Dầu Đôi': 'Cây Dầu Đôi',
        'Diên Điền': 'Diên Điền',
        'Diên Hòa': 'Diên Hòa',
        'Diên Khánh': 'Diên Khánh',
        'Diên Phú': 'Diên Phú',
        'Gò Cây Sung': 'Gò Cây Sung',
        'Lương Định Của': 'Vĩnh Ngọc',
        'Phú Nông': 'Phú Nông',
        'Tây Nha Trang': 'Vĩnh Ngọc',
        'Vĩnh Châu': 'Vĩnh Châu',
        'Vĩnh Hiệp': 'Vĩnh Hiệp',
        'Vĩnh Ngọc': 'Vĩnh Ngọc',
        'Vĩnh Phương': 'Vĩnh Phương',
        'Vĩnh Thái': 'Vĩnh Thái',
        'Vĩnh Thạnh': 'Vĩnh Thạnh',
        'Vĩnh Trung': 'Vĩnh Trung',
        'Võ Cạnh': 'Võ Cạnh',
        'Võ Dõng': 'Võ Dõng',
        'Xuân Sơn': 'Xuân Sơn',
        '23/10': 'Đường 23/10',
        'đường 23': 'Đường 23/10',
    }
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip header và dòng trống
        if not line or 'Mức độ ưu tiên' in line or 'CHỖ NÀO' in line:
            continue
        
        # Parse priority
        priority = parse_priority_from_line(line)
        if not priority:
            priority = 'MEDIUM'
        
        # Extract phones
        phones = []
        phone_matches = re.findall(phone_pattern, line)
        
        for phone in phone_matches:
            clean_phone = re.sub(r'[^\d]', '', phone)
            if 9 <= len(clean_phone) <= 11:
                if len(clean_phone) == 10:
                    formatted = f"{clean_phone[:4]} {clean_phone[4:7]} {clean_phone[7:]}"
                elif len(clean_phone) == 9:
                    formatted = f"{clean_phone[:3]} {clean_phone[3:6]} {clean_phone[6:]}"
                else:
                    formatted = clean_phone
                phones.append(formatted)
        
        # Remove phones and priority keywords from content
        content = line
        for phone_match in phone_matches:
            content = content.replace(phone_match, '')
        content = re.sub(r'(Khẩn cấp|Ưu tiên cao|Thường)', '', content, flags=re.IGNORECASE)
        
        # Clean content
        content = re.sub(r'\s+', ' ', content).strip()
        content = re.sub(r'^[^\w]+', '', content)
        
        if not content or len(content) < 10:
            continue
        
        # Determine area
        area = 'Khác'
        for keyword, area_name in area_keywords.items():
            if keyword.lower() in content.lower():
                area = area_name
                break
        
        # Create case
        case = {
            "id": current_id,
            "content": content,
            "phones": phones,
            "area": area,
            "priority": priority,
            "isRescued": False
        }
        
        raw_cases.append(case)
        current_id += 1
    
    print(f"📝 Parsed {len(raw_cases)} cases from PDF")
    
    # Deduplicate
    print("🔍 Removing duplicates...")
    unique_cases = merge_duplicates(raw_cases)
    
    duplicates_removed = len(raw_cases) - len(unique_cases)
    print(f"✅ Removed {duplicates_removed} duplicate cases")
    
    # Re-assign IDs
    for i, case in enumerate(unique_cases, 1):
        case['id'] = i
    
    return unique_cases

# Parse dữ liệu
print("=" * 60)
print("🚨 RESCUE DATA PARSER - SMART DEDUPLICATION")
print("=" * 60)

data = parse_rescue_data_smart('pdf_content.txt')

# Statistics
priority_counts = {}
area_counts = {}

for case in data:
    priority = case['priority']
    priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    area = case['area']
    area_counts[area] = area_counts.get(area, 0) + 1

print(f"\n✅ Total unique cases: {len(data)}")

print(f"\n📊 Priority Distribution:")
for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    count = priority_counts.get(priority, 0)
    if count > 0:
        emoji = '🚨' if priority == 'CRITICAL' else '⚠️' if priority == 'HIGH' else '📝' if priority == 'MEDIUM' else 'ℹ️'
        print(f"  {emoji} {priority}: {count} cases ({count/len(data)*100:.1f}%)")

print(f"\n🗺️  Area Distribution (All {len(area_counts)} areas):")
for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {area}: {count} cases")

# Save to JSON
output_file = 'rescue-app/src/data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Saved {len(data)} unique cases to {output_file}")

# Show top CRITICAL cases
print(f"\n🚨 Top 5 CRITICAL cases:")
critical_cases = [c for c in data if c['priority'] == 'CRITICAL'][:5]
for i, case in enumerate(critical_cases, 1):
    phones_str = ', '.join(case['phones'][:2]) if case['phones'] else '(No phone)'
    print(f"\n{i}. [{case['area']}] {case['content'][:100]}...")
    print(f"   📞 {phones_str}")
