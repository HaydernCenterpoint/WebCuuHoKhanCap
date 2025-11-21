import React, { useState, useMemo, useEffect, useRef } from 'react';
import { Search, MapPin, Phone, AlertCircle, Filter, CheckCircle, Plus, X, List, Archive, Navigation, Upload, Map } from 'lucide-react';
import { read, utils } from 'xlsx';
import initialData from './data.json';
import MapView from './MapView';

function App() {
  const [data, setData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedArea, setSelectedArea] = useState('All');
  const [selectedPriority, setSelectedPriority] = useState('All');
  const [activeTab, setActiveTab] = useState('need_rescue'); // 'need_rescue' or 'rescued'
  const [isModalOpen, setIsModalOpen] = useState(false);
  const fileInputRef = useRef(null);

  // New Case Form State
  const [newCase, setNewCase] = useState({
    content: '',
    phones: '',
    area: 'Khác'
  });

  // Load data from localStorage or initialData
  useEffect(() => {
    const savedData = localStorage.getItem('rescue-data');
    if (savedData) {
      setData(JSON.parse(savedData));
    } else {
      // Add 'isRescued' property to initial data
      const processedData = initialData.map(item => ({ ...item, isRescued: false }));
      setData(processedData);
    }
  }, []);

  // Save to localStorage whenever data changes
  useEffect(() => {
    if (data.length > 0) {
      localStorage.setItem('rescue-data', JSON.stringify(data));
    }
  }, [data]);

  const areas = useMemo(() => {
    const allAreas = data.map(item => item.area);
    return ['All', ...new Set(allAreas)].sort();
  }, [data]);

  const filteredData = useMemo(() => {
    return data.filter(item => {
      const matchesSearch = item.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.phones.some(phone => phone.includes(searchTerm));
      const matchesArea = selectedArea === 'All' || item.area === selectedArea;
      const matchesPriority = selectedPriority === 'All' || item.priority === selectedPriority;

      const matchesTab = activeTab === 'need_rescue' ? !item.isRescued : item.isRescued;

      return matchesSearch && matchesArea && matchesPriority && matchesTab;
    });
  }, [data, searchTerm, selectedArea, selectedPriority, activeTab]);

  const toggleStatus = (id) => {
    setData(prevData => prevData.map(item =>
      item.id === id ? { ...item, isRescued: !item.isRescued } : item
    ));
  };

  const handleAddCase = (e) => {
    e.preventDefault();
    if (!newCase.content) return;

    const phoneList = newCase.phones.split(',').map(p => p.trim()).filter(p => p);

    const newItem = {
      id: Date.now(), // Simple ID generation
      content: newCase.content,
      phones: phoneList,
      area: newCase.area,
      isRescued: false
    };

    setData(prev => [newItem, ...prev]);
    setNewCase({ content: '', phones: '', area: 'Khác' });
    setIsModalOpen(false);
    setActiveTab('need_rescue'); // Switch to need rescue tab to see new item
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      const bstr = evt.target.result;
      const wb = read(bstr, { type: 'binary' });
      const wsname = wb.SheetNames[0];
      const ws = wb.Sheets[wsname];
      const jsonData = utils.sheet_to_json(ws, { header: 1 });

      // Remove header row if it exists (heuristic: check if first row has "content" or "nội dung")
      let startIndex = 0;
      if (jsonData.length > 0) {
        const firstRow = jsonData[0].map(cell => String(cell).toLowerCase());
        if (firstRow.some(cell => cell.includes('nội dung') || cell.includes('content') || cell.includes('địa chỉ'))) {
          startIndex = 1;
        }
      }

      const newItems = [];
      let duplicatesCount = 0;

      for (let i = startIndex; i < jsonData.length; i++) {
        const row = jsonData[i];
        if (!row || row.length === 0) continue;

        // Assume Column A: Content, Column B: Phones, Column C: Area
        // Adjust indices if needed based on your excel structure
        const content = row[0] ? String(row[0]) : '';
        const phonesRaw = row[1] ? String(row[1]) : '';
        const area = row[2] ? String(row[2]) : 'Khác';

        if (!content) continue;

        const phones = phonesRaw.split(/[,;\-]/).map(p => p.trim()).filter(p => p);

        // Check for duplicates
        const isDuplicate = data.some(existingItem => {
          const contentMatch = existingItem.content.trim().toLowerCase() === content.trim().toLowerCase();

          // Normalize phones for comparison (remove non-digits)
          const clean = p => p.replace(/\D/g, '');
          const existingPhones = existingItem.phones.map(clean).filter(p => p.length > 6); // Filter short/invalid
          const newPhones = phones.map(clean).filter(p => p.length > 6);

          const phoneMatch = newPhones.length > 0 && existingPhones.some(p => newPhones.includes(p));

          return contentMatch || phoneMatch;
        });

        if (isDuplicate) {
          duplicatesCount++;
          continue;
        }

        newItems.push({
          id: Date.now() + i, // Ensure unique IDs
          content: content,
          phones: phones,
          area: area,
          isRescued: false
        });
      }

      if (newItems.length > 0) {
        setData(prev => [...newItems, ...prev]);
        alert(`Đã nhập thành công ${newItems.length} ca mới!\n(Đã tự động bỏ qua ${duplicatesCount} ca trùng lặp)`);
        setActiveTab('need_rescue');
      } else if (duplicatesCount > 0) {
        alert(`Tất cả ${duplicatesCount} ca trong file đều đã tồn tại trong hệ thống.`);
      } else {
        alert('Không tìm thấy dữ liệu hợp lệ trong file.');
      }

      // Reset input
      if (fileInputRef.current) fileInputRef.current.value = '';
    };
    reader.readAsBinaryString(file);
  };

  const extractAddress = (content) => {
    // Remove extra whitespace
    let text = content.trim();

    // Keywords that typically indicate the end of address and start of description
    const descriptionKeywords = [
      'liên hệ', 'cần', 'gấp', 'khẩn cấp', 'bị', 'đang', 'có', 'nhờ', 'giúp',
      'mắc kẹt', 'ngập', 'nước', 'lũ', 'người', 'trẻ em', 'già', 'yếu',
      'thiếu', 'hết', 'không', 'sắp', 'vừa', 'đã', 'SOS', 'sos'
    ];

    // Try to find where description starts
    let addressEnd = text.length;

    for (const keyword of descriptionKeywords) {
      const regex = new RegExp(`\\b${keyword}\\b`, 'i');
      const match = text.search(regex);
      if (match !== -1 && match < addressEnd) {
        addressEnd = match;
      }
    }

    // Take the part before description
    let address = text.substring(0, addressEnd).trim();

    // Remove trailing punctuation and clean up
    address = address.replace(/[,.\-;:]+$/, '').trim();

    // If address is too short or empty, use original content
    if (address.length < 10) {
      // Try to get first meaningful part (before common separators)
      const parts = text.split(/[–\-—]/);
      if (parts.length > 0) {
        address = parts[0].trim();
      } else {
        // Fallback: take first 100 characters
        address = text.substring(0, 100);
      }
    }

    return address;
  };

  const openGoogleMaps = (content, area) => {
    // Extract clean address from content
    const cleanAddress = extractAddress(content);
    const query = encodeURIComponent(`${cleanAddress}, ${area}, Khánh Hòa`);
    window.open(`https://www.google.com/maps/search/?api=1&query=${query}`, '_blank');
  };

  const needRescueCount = data.filter(i => !i.isRescued).length;
  const rescuedCount = data.filter(i => i.isRescued).length;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Header */}
      <header className="bg-red-600 text-white shadow-lg sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <AlertCircle size={32} className="text-white" />
              <h1 className="text-2xl font-bold tracking-tight">Cứu Hộ Khẩn Cấp</h1>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept=".xlsx, .xls"
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current.click()}
                className="flex items-center gap-2 bg-white/10 text-white px-4 py-2 rounded-full font-medium hover:bg-white/20 transition-colors"
              >
                <Upload size={18} />
                Nhập Excel
              </button>
              <button
                onClick={() => setIsModalOpen(true)}
                className="flex items-center gap-2 bg-white text-red-600 px-4 py-2 rounded-full font-bold hover:bg-red-50 transition-colors shadow-sm"
              >
                <Plus size={18} />
                Thêm Ca Mới
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">

        {/* Controls & Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 mb-8 overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-slate-200">
            <button
              onClick={() => setActiveTab('need_rescue')}
              className={`flex-1 py-4 text-center font-medium text-sm uppercase tracking-wider transition-colors flex items-center justify-center gap-2 ${activeTab === 'need_rescue'
                ? 'bg-white text-red-600 border-b-2 border-red-600'
                : 'bg-slate-50 text-slate-500 hover:bg-slate-100'
                }`}
            >
              <List size={18} />
              Cần Cứu Hộ ({needRescueCount})
            </button>
            <button
              onClick={() => setActiveTab('rescued')}
              className={`flex-1 py-4 text-center font-medium text-sm uppercase tracking-wider transition-colors flex items-center justify-center gap-2 ${activeTab === 'rescued'
                ? 'bg-white text-green-600 border-b-2 border-green-600'
                : 'bg-slate-50 text-slate-500 hover:bg-slate-100'
                }`}
            >
              <Archive size={18} />
              Đã Cứu ({rescuedCount})
            </button>
          </div>

          {/* Filters */}
          <div className="p-6 flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
              <input
                type="text"
                placeholder="Tìm kiếm..."
                className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-red-500 focus:ring-2 focus:ring-red-200 outline-none transition-all"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Filter Area */}
            <div className="relative min-w-[200px]">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
              <select
                className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-red-500 focus:ring-2 focus:ring-red-200 outline-none appearance-none bg-white transition-all"
                value={selectedArea}
                onChange={(e) => setSelectedArea(e.target.value)}
              >
                {areas.map(area => (
                  <option key={area} value={area}>{area === 'All' ? 'Tất cả khu vực' : area}</option>
                ))}
              </select>
            </div>

            {/* Filter Priority */}
            <div className="relative min-w-[200px]">
              <AlertCircle className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
              <select
                className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 focus:border-red-500 focus:ring-2 focus:ring-red-200 outline-none appearance-none bg-white transition-all"
                value={selectedPriority}
                onChange={(e) => setSelectedPriority(e.target.value)}
              >
                <option value="All">Tất cả mức độ</option>
                <option value="CRITICAL">🚨 Khẩn cấp</option>
                <option value="HIGH">⚠️ Cao</option>
                <option value="MEDIUM">📝 Trung bình</option>
                <option value="LOW">ℹ️ Thấp</option>
              </select>
            </div>
          </div>
        </div>

        {/* Stats for filtered view */}
        <div className="mb-6 text-slate-500 font-medium flex justify-between items-center">
          <span>Hiển thị {filteredData.length} kết quả</span>
          <span className="text-sm bg-slate-100 px-3 py-1 rounded-full">
            {activeTab === 'need_rescue' ? 'Danh sách chờ cứu hộ' : 'Danh sách đã hoàn thành'}
          </span>
        </div>

        {/* Map View - Only show in need_rescue tab */}
        {/* TEMPORARILY DISABLED - Google Maps API key configuration needed */}
        {false && activeTab === 'need_rescue' && (
          <div className="mb-8">
            <MapView
              data={data}
              onCaseClick={(item) => {
                // Optionally scroll to the case card
              }}
            />
          </div>
        )}

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredData.map(item => (
            <div key={item.id} className={`bg-white rounded-xl shadow-sm border transition-all duration-300 overflow-hidden flex flex-col ${item.isRescued ? 'border-green-200 bg-green-50/30' : 'border-slate-200 hover:shadow-md'
              }`}>
              <div className="p-5 flex-1">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${item.area === 'Khác' ? 'bg-slate-100 text-slate-800' : 'bg-blue-50 text-blue-700'
                      }`}>
                      <MapPin size={12} className="mr-1" />
                      {item.area}
                    </span>

                    {/* Priority Badge */}
                    {item.priority && (
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold uppercase ${item.priority === 'CRITICAL' ? 'bg-red-100 text-red-700 ring-1 ring-red-300' :
                        item.priority === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                          item.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-slate-100 text-slate-600'
                        }`}>
                        {item.priority === 'CRITICAL' ? '🚨 Khẩn Cấp' :
                          item.priority === 'HIGH' ? '⚠️ Cao' :
                            item.priority === 'MEDIUM' ? '📝 TB' :
                              '  ℹ️ Thấp'}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => openGoogleMaps(item.content, item.area)}
                      className="text-blue-600 hover:bg-blue-50 p-1.5 rounded-full transition-colors"
                      title="Xem vị trí trên bản đồ"
                    >
                      <Navigation size={16} />
                    </button>

                    {item.isRescued && (
                      <span className="text-green-600 flex items-center text-xs font-bold uppercase tracking-wider">
                        <CheckCircle size={14} className="mr-1" /> Đã cứu
                      </span>
                    )}
                    <span className="text-xs text-slate-400">#{item.id}</span>
                  </div>
                </div>

                <p className={`mb-4 leading-relaxed ${item.isRescued ? 'text-slate-500' : 'text-slate-700'}`}>
                  {item.content}
                </p>
              </div>

              <div className="bg-slate-50 px-5 py-4 border-t border-slate-100 flex flex-col gap-3">
                <div className="flex flex-wrap gap-2">
                  {item.phones.length > 0 ? (
                    item.phones.map((phone, idx) => (
                      <a
                        key={idx}
                        href={`tel:${phone.replace(/\s/g, '')}`}
                        className={`inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${item.isRescued
                          ? 'bg-slate-200 text-slate-500 cursor-not-allowed'
                          : 'bg-green-50 text-green-700 hover:bg-green-100'
                          }`}
                      >
                        <Phone size={14} className="mr-1.5" />
                        {phone}
                      </a>
                    ))
                  ) : (
                    <span className="inline-flex items-center text-slate-400 text-sm italic">
                      Không có SĐT
                    </span>
                  )}
                </div>

                <button
                  onClick={() => toggleStatus(item.id)}
                  className={`w-full py-2 rounded-lg font-medium text-sm transition-colors flex items-center justify-center ${item.isRescued
                    ? 'bg-slate-200 text-slate-600 hover:bg-slate-300'
                    : 'bg-red-600 text-white hover:bg-red-700 shadow-sm'
                    }`}
                >
                  {item.isRescued ? 'Đánh dấu chưa cứu' : 'Xác nhận đã cứu'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {filteredData.length === 0 && (
          <div className="text-center py-12">
            <div className="bg-slate-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              {activeTab === 'need_rescue' ? <Search size={32} className="text-slate-400" /> : <CheckCircle size={32} className="text-green-400" />}
            </div>
            <h3 className="text-lg font-medium text-slate-900">
              {activeTab === 'need_rescue' ? 'Không tìm thấy kết quả cần cứu' : 'Chưa có ca nào trong danh sách đã cứu'}
            </h3>
            <p className="text-slate-500">
              {activeTab === 'need_rescue' ? 'Thử thay đổi từ khóa hoặc bộ lọc khu vực' : 'Hãy xác nhận cứu hộ các ca từ danh sách cần cứu'}
            </p>
          </div>
        )}
      </main>

      {/* Add New Case Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">
            <div className="bg-red-600 px-6 py-4 flex justify-between items-center">
              <h2 className="text-white text-xl font-bold flex items-center gap-2">
                <Plus size={24} /> Thêm Ca Cứu Hộ Mới
              </h2>
              <button onClick={() => setIsModalOpen(false)} className="text-white/80 hover:text-white transition-colors">
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleAddCase} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Nội dung / Địa chỉ / Tình trạng</label>
                <textarea
                  required
                  className="w-full p-3 rounded-lg border border-slate-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 outline-none min-h-[100px]"
                  placeholder="Nhập chi tiết địa chỉ và tình trạng..."
                  value={newCase.content}
                  onChange={e => setNewCase({ ...newCase, content: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Số điện thoại (phân cách bằng dấu phẩy)</label>
                <input
                  type="text"
                  className="w-full p-3 rounded-lg border border-slate-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 outline-none"
                  placeholder="VD: 0901234567, 0987654321"
                  value={newCase.phones}
                  onChange={e => setNewCase({ ...newCase, phones: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Khu vực</label>
                <select
                  className="w-full p-3 rounded-lg border border-slate-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 outline-none bg-white"
                  value={newCase.area}
                  onChange={e => setNewCase({ ...newCase, area: e.target.value })}
                >
                  {areas.filter(a => a !== 'All').map(area => (
                    <option key={area} value={area}>{area}</option>
                  ))}
                  <option value="Khác">Khác</option>
                  <option value="__custom__">➕ Tự nhập khu vực mới</option>
                </select>

                {newCase.area === '__custom__' && (
                  <input
                    type="text"
                    className="w-full p-3 rounded-lg border border-slate-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 outline-none mt-2"
                    placeholder="Nhập tên khu vực mới..."
                    onChange={e => setNewCase({ ...newCase, area: e.target.value || 'Khác' })}
                    autoFocus
                  />
                )}
              </div>

              <div className="pt-4 flex gap-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 py-3 rounded-lg border border-slate-300 text-slate-700 font-medium hover:bg-slate-50 transition-colors"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  className="flex-1 py-3 rounded-lg bg-red-600 text-white font-bold hover:bg-red-700 shadow-md transition-colors"
                >
                  Thêm Mới
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
