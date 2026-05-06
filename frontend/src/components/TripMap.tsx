import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Icon, LatLngBounds, DivIcon } from 'leaflet';
import { api } from '../lib/api';

interface Footprint {
  id: number;
  image_url: string;
  note: string;
  latitude: number;
  longitude: number;
  location_name: string | null;
  recorded_at: string;
}

const customIcon = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

// 中国区域默认中心
const CHINA_CENTER: [number, number] = [35.8617, 104.1954];

const MAP_STYLES = [
  {
    key: 'standard',
    name: '标准',
    url: 'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
    subdomains: ['1', '2', '3', '4'] as string[],
    attribution: '&copy; <a href="https://www.amap.com">高德地图</a>',
  },
  {
    key: 'satellite',
    name: '卫星',
    url: 'https://webst0{s}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}',
    subdomains: ['1', '2', '3', '4'] as string[],
    attribution: '&copy; <a href="https://www.amap.com">高德地图</a>',
  },
  {
    key: 'light',
    name: '浅色',
    url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    subdomains: ['a', 'b', 'c', 'd'] as string[],
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
  },
  {
    key: 'dark',
    name: '深色',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    subdomains: ['a', 'b', 'c', 'd'] as string[],
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
  },
  {
    key: 'terrain',
    name: '地形',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    subdomains: ['a', 'b', 'c'] as string[],
    attribution: '&copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
  },
  {
    key: 'voyager',
    name: '航海',
    url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    subdomains: ['a', 'b', 'c', 'd'] as string[],
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
  },
];

function createCardIcon(fp: Footprint): DivIcon {
  const hasImg = Boolean(fp.image_url);
  const html = `
    <div style="
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.18);
      padding: 5px;
      width: 130px;
      text-align: center;
      border: 1px solid #e2e8f0;
      font-family: system-ui, -apple-system, sans-serif;
    ">
      ${hasImg ? `<img src="${fp.image_url}" style="width:100%;height:64px;object-fit:cover;border-radius:4px;margin-bottom:4px;display:block;">` : ''}
      <div style="font-size:11px;font-weight:600;color:#1e293b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:0 2px;">${fp.note}</div>
      ${fp.location_name ? `<div style="font-size:10px;color:#64748b;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:0 2px;">${fp.location_name}</div>` : ''}
    </div>
  `;
  return new DivIcon({
    className: '',
    html,
    iconSize: [140, hasImg ? 105 : 45],
    iconAnchor: [70, hasImg ? 52 : 22],
  });
}

function FitBounds({ footprints }: { footprints: Footprint[] }) {
  const map = useMap();
  useEffect(() => {
    if (footprints.length === 1) {
      const fp = footprints[0];
      map.setView([fp.latitude, fp.longitude], 10);
    } else if (footprints.length > 1) {
      const bounds = new LatLngBounds(
        footprints.map((fp) => [fp.latitude, fp.longitude] as [number, number])
      );
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
    }
  }, [map, footprints]);
  return null;
}

export default function TripMap() {
  const [footprints, setFootprints] = useState<Footprint[]>([]);
  const [loading, setLoading] = useState(true);
  const [showImages, setShowImages] = useState(true);
  const [cardMode, setCardMode] = useState(false);
  const [mapStyle, setMapStyle] = useState(MAP_STYLES[0]);

  useEffect(() => {
    api
      .get('/footprints/map')
      .then((res) => setFootprints(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="h-64 flex items-center justify-center text-slate-400">地图加载中...</div>;
  }

  const hasFootprints = footprints.length > 0;
  const currentStyle = mapStyle;

  return (
    <div className="h-[500px] rounded-xl overflow-hidden border border-slate-200 shadow-sm relative">
      {/* 地图控制栏 */}
      <div className="absolute top-2 right-2 z-[500] flex flex-col gap-2">
        <div className="bg-white rounded-lg shadow-md p-1.5 flex flex-col gap-1 max-h-48 overflow-y-auto">
          {MAP_STYLES.map((style) => (
            <button
              key={style.key}
              onClick={() => setMapStyle(style)}
              className={`px-2 py-1 text-xs rounded font-medium transition ${
                currentStyle.key === style.key
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {style.name}
            </button>
          ))}
        </div>

        {hasFootprints && (
          <>
            <button
              onClick={() => setShowImages((v) => !v)}
              className={`px-3 py-1.5 text-xs rounded-lg shadow-md font-medium transition bg-white ${
                showImages ? 'text-blue-600' : 'text-slate-500'
              }`}
            >
              {showImages ? '隐藏图片' : '显示图片'}
            </button>
            <button
              onClick={() => setCardMode((v) => !v)}
              className={`px-3 py-1.5 text-xs rounded-lg shadow-md font-medium transition bg-white ${
                cardMode ? 'text-blue-600' : 'text-slate-500'
              }`}
            >
              {cardMode ? '标记模式' : '卡片模式'}
            </button>
          </>
        )}
      </div>

      <MapContainer
        center={CHINA_CENTER}
        zoom={4}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution={currentStyle.attribution}
          url={currentStyle.url}
          subdomains={currentStyle.subdomains}
        />

        {hasFootprints && <FitBounds footprints={footprints} />}

        {footprints.map((fp) => (
          <Marker
            key={fp.id}
            position={[fp.latitude, fp.longitude]}
            icon={cardMode ? createCardIcon(fp) : customIcon}
          >
            {!cardMode && (
              <Popup>
                <div className="max-w-xs">
                  {showImages && fp.image_url && (
                    <img
                      src={fp.image_url}
                      alt=""
                      className="w-full h-24 object-cover rounded mb-2"
                    />
                  )}
                  <p className="text-sm font-medium">{fp.note}</p>
                  {fp.location_name && (
                    <p className="text-xs text-slate-500 mt-1">{fp.location_name}</p>
                  )}
                </div>
              </Popup>
            )}
          </Marker>
        ))}
      </MapContainer>

      {!hasFootprints && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="bg-white/80 px-4 py-2 rounded-lg text-sm text-slate-500 shadow">
            添加足迹后，地图将在这里展示
          </div>
        </div>
      )}
    </div>
  );
}
