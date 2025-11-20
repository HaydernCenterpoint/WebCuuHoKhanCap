# 🚨 Emergency Rescue Management App

Ứng dụng quản lý và điều phối cứu hộ khẩn cấp trong tình huống thiên tai (lũ lụt, bão...).

## ✨ Tính năng

- 🔍 **Tìm kiếm & Lọc**: Tìm kiếm theo địa chỉ, số điện thoại, khu vực
- 📋 **Quản lý danh sách**: Tab "Cần Cứu Hộ" và "Đã Cứu"
- 📞 **Gọi điện trực tiếp**: Bấm số điện thoại để gọi ngay
- 🗺️ **Xem bản đồ**: Mở vị trí trên Google Maps
- ➕ **Thêm ca mới**: Thủ công hoặc nhập hàng loạt từ Excel
- 🔄 **Phát hiện trùng lặp**: Tự động loại bỏ ca trùng khi nhập Excel

## 🚀 Cài đặt

### Yêu cầu
- Node.js 18+ 
- npm hoặc yarn

### Các bước

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/rescue-app.git

# Di chuyển vào thư mục
cd rescue-app

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

Mở trình duyệt tại `http://localhost:5173`

## 📦 Build

```bash
npm run build
```

File build sẽ nằm trong thư mục `dist/`

## 🛠️ Công nghệ sử dụng

- **React** - UI Framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **XLSX** - Excel import/export

## 📖 Hướng dẫn

- [Hướng dẫn sử dụng](./HUONG_DAN_SU_DUNG.md)
- [Hướng dẫn triển khai](./HUONG_DAN_TRIEN_KHAI.md)

## 📊 Định dạng dữ liệu Excel

Khi nhập Excel, file cần có 3 cột:

| Cột A | Cột B | Cột C |
|-------|-------|-------|
| Nội dung/Địa chỉ | Số điện thoại | Khu vực |

## 🤝 Đóng góp

Pull requests luôn được chào đón!

## 📄 License

MIT

---

**Phát triển bởi**: [Tên của bạn]  
**Liên hệ**: [Email/SĐT của bạn]
