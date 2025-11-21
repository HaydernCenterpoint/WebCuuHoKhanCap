import React, { useState, useMemo, useCallback } from 'react';
import { GoogleMap, useLoadScript, Marker, InfoWindow } from '@react-google-maps/api';
import { Phone, MapPin, Navigation } from 'lucide-react';

const MapView = ({ data, onCaseClick }) => {
    const [selectedCase, setSelectedCase] = useState(null);
    const [showRainLayer, setShowRainLayer] = useState(false);
    const [map, setMap] = useState(null);

    // Google Maps API Key
    const API_KEY = 'AIzaSyBuh8ZO97x25hsw9qb_NKI15bmMSwEiMYA';

    // Load Google Maps Script
    const { isLoaded, loadError } = useLoadScript({
        googleMapsApiKey: API_KEY,
    });

    // Center of Khánh Hòa (Nha Trang)
    const center = useMemo(() => ({
        lat: 12.2388,
        lng: 109.1967
    }), []);

    const mapContainerStyle = {
        width: '100%',
        height: '600px'
    };

    // Get coordinates from data (using a simple geocoding approximation)
    const markers = useMemo(() => {
        return data
            .filter(item => !item.isRescued) // Only show pending cases
            .map(item => {
                // Simple coordinate assignment based on area
                let lat = 12.2388;
                let lng = 109.1967;

                // Rough area mapping
                if (item.area.includes('Vĩnh Thạnh')) {
                    lat = 12.3000;
                    lng = 109.1800;
                } else if (item.area.includes('Diên Khánh')) {
                    lat = 12.2650;
                    lng = 109.0450;
                } else if (item.area.includes('Diên Phú')) {
                    lat = 12.2700;
                    lng = 109.0500;
                } else if (item.area.includes('Vĩnh Ngọc')) {
                    lat = 12.3100;
                    lng = 109.1700;
                } else if (item.area.includes('Ninh Hòa')) {
                    lat = 12.5000;
                    lng = 109.1200;
                }

                // Add small random offset to avoid overlapping markers
                lat += (Math.random() - 0.5) * 0.02;
                lng += (Math.random() - 0.5) * 0.02;

                return {
                    ...item,
                    position: { lat, lng }
                };
            });
    }, [data]);

    const onLoad = useCallback((map) => {
        setMap(map);
    }, []);

    const toggleRainLayer = () => {
        setShowRainLayer(!showRainLayer);

        if (!showRainLayer && map) {
            // Add RainViewer overlay
            const timestamp = Date.now();
            const overlay = new window.google.maps.ImageMapType({
                getTileUrl: function (coord, zoom) {
                    return `https://tilecache.rainviewer.com/v2/radar/${timestamp}/512/${zoom}/${coord.x}/${coord.y}/2/1_1.png`;
                },
                tileSize: new window.google.maps.Size(512, 512),
                opacity: 0.5,
                name: 'Rain'
            });
            map.overlayMapTypes.push(overlay);
        } else if (map) {
            // Remove rain layer
            map.overlayMapTypes.clear();
        }
    };

    if (loadError) {
        return <div className="p-4 bg-red-50 text-red-700 rounded-lg">Lỗi tải Google Maps: {loadError.message}</div>;
    }

    if (!isLoaded) {
        return <div className="p-4 bg-blue-50 text-blue-700 rounded-lg">Đang tải bản đồ...</div>;
    }

    return (
        <div className="relative">
            {/* Rain Toggle Button */}
            <button
                onClick={toggleRainLayer}
                className={`absolute top-4 right-4 z-10 px-4 py-2 rounded-lg font-medium text-sm transition-all shadow-lg ${showRainLayer
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'bg-white text-slate-700 hover:bg-slate-100'
                    }`}
            >
                {showRainLayer ? '🌧️ Ẩn mức mưa' : '🌧️ Xem mức mưa'}
            </button>

            <GoogleMap
                mapContainerStyle={mapContainerStyle}
                center={center}
                zoom={11}
                onLoad={onLoad}
            >
                {markers.map((item) => (
                    <Marker
                        key={item.id}
                        position={item.position}
                        onClick={() => setSelectedCase(item)}
                        icon={{
                            url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
                            scaledSize: new window.google.maps.Size(40, 40)
                        }}
                    />
                ))}

                {selectedCase && (
                    <InfoWindow
                        position={selectedCase.position}
                        onCloseClick={() => setSelectedCase(null)}
                    >
                        <div className="p-2 max-w-xs">
                            <div className="flex items-center gap-2 mb-2">
                                <MapPin size={16} className="text-blue-600" />
                                <span className="font-semibold text-sm">{selectedCase.area}</span>
                            </div>
                            <p className="text-sm text-slate-700 mb-3 leading-relaxed">
                                {selectedCase.content.length > 100
                                    ? selectedCase.content.substring(0, 100) + '...'
                                    : selectedCase.content}
                            </p>
                            {selectedCase.phones.length > 0 && (
                                <div className="flex flex-wrap gap-2 mb-2">
                                    {selectedCase.phones.map((phone, idx) => (
                                        <a
                                            key={idx}
                                            href={`tel:${phone.replace(/\s/g, '')}`}
                                            className="inline-flex items-center px-2 py-1 bg-green-50 text-green-700 rounded text-xs hover:bg-green-100"
                                        >
                                            <Phone size={12} className="mr-1" />
                                            {phone}
                                        </a>
                                    ))}
                                </div>
                            )}
                            <button
                                onClick={() => onCaseClick(selectedCase)}
                                className="w-full mt-2 px-3 py-1.5 bg-red-600 text-white rounded text-sm hover:bg-red-700 flex items-center justify-center gap-1"
                            >
                                <Navigation size={14} />
                                Xem chi tiết
                            </button>
                        </div>
                    </InfoWindow>
                )}
            </GoogleMap>

            {/* Legend */}
            <div className="mt-4 p-4 bg-white rounded-lg shadow-sm border border-slate-200">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                            <span className="text-sm text-slate-700">Cần cứu hộ ({markers.length})</span>
                        </div>
                    </div>
                    <span className="text-xs text-slate-500">Bấm vào điểm đỏ để xem chi tiết</span>
                </div>
            </div>
        </div>
    );
};

export default MapView;
