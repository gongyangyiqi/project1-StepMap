import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { Icon } from 'leaflet';
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

interface Trip {
  id: number;
  title: string;
  start_date: string;
  end_date: string;
  footprint_count: number;
}

export default function TripDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [trip, setTrip] = useState<Trip | null>(null);
  const [footprints, setFootprints] = useState<Footprint[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showMapPicker, setShowMapPicker] = useState(false);

  // Add footprint form state
  const [imageUrl, setImageUrl] = useState('');
  const [note, setNote] = useState('');
  const [lat, setLat] = useState('');
  const [lng, setLng] = useState('');
  const [locationName, setLocationName] = useState('');
  const [recordedAt, setRecordedAt] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);

  const fetchData = async () => {
    if (!id) return;
    try {
      const [tripRes, fpRes] = await Promise.all([
        api.get(`/trips/${id}`),
        api.get(`/footprints/trip/${id}`),
      ]);
      setTrip(tripRes.data);
      setFootprints(fpRes.data);
    } catch {
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const handleAddFootprint = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    setSubmitting(true);
    try {
      await api.post('/footprints', {
        trip_id: parseInt(id),
        image_url: imageUrl,
        note,
        latitude: parseFloat(lat),
        longitude: parseFloat(lng),
        location_name: locationName || null,
        recorded_at: new Date(recordedAt).toISOString(),
      });
      setShowAddForm(false);
      setImageUrl('');
      setNote('');
      setLat('');
      setLng('');
      setLocationName('');
      setRecordedAt('');
      setUploadingImage(false);
      fetchData();
    } catch {
      alert('添加失败，请检查输入');
    } finally {
      setSubmitting(false);
    }
  };

  const getLocation = () => {
    if (!navigator.geolocation) {
      alert('浏览器不支持定位');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(pos.coords.latitude.toFixed(6));
        setLng(pos.coords.longitude.toFixed(6));
      },
      () => {
        alert('定位失败，请手动输入坐标');
      }
    );
  };

const CHINA_CENTER: [number, number] = [35.8617, 104.1954];

const clickIcon = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

function MapPickerMarker({ onPick }: { onPick: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      onPick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

function MapPickerModal({ onPick, onClose }: { onPick: (lat: number, lng: number) => void; onClose: () => void }) {
  const [picked, setPicked] = useState<[number, number] | null>(null);

  return (
    <div className="fixed inset-0 z-[9999] bg-white flex flex-col">
      <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between bg-white shrink-0">
        <h3 className="font-bold text-slate-800">在地图上点击选点</h3>
        <button
          onClick={onClose}
          className="text-slate-500 hover:text-slate-700 px-3 py-1.5 rounded-lg hover:bg-slate-100 transition text-sm"
        >
          关闭
        </button>
      </div>
      <div className="flex-1 relative">
        <MapContainer
          center={CHINA_CENTER}
          zoom={4}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; 高德地图'
            url="https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}"
            subdomains={['1', '2', '3', '4']}
          />
          <MapPickerMarker onPick={(la, ln) => setPicked([la, ln])} />
          {picked && <Marker position={picked} icon={clickIcon} />}
        </MapContainer>

        {!picked && (
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-white/90 px-5 py-2.5 rounded-lg shadow-lg text-sm text-slate-600 pointer-events-none z-[1000]">
            点击地图选择位置
          </div>
        )}

        {picked && (
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 z-[1000]">
            <div className="bg-white/90 px-4 py-2 rounded-lg text-sm text-slate-700 text-center shadow">
              纬度 {picked[0].toFixed(6)}，经度 {picked[1].toFixed(6)}
            </div>
            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="px-5 py-2.5 bg-white text-slate-700 rounded-lg shadow-lg border border-slate-200 font-medium hover:bg-slate-50 transition"
              >
                取消
              </button>
              <button
                onClick={() => {
                  onPick(picked[0], picked[1]);
                  onClose();
                }}
                className="px-5 py-2.5 bg-blue-600 text-white rounded-lg shadow-lg font-medium hover:bg-blue-700 transition"
              >
                确认选点
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingImage(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await api.post('/uploads', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setImageUrl(res.data.url);
    } catch {
      alert('图片上传失败');
    } finally {
      setUploadingImage(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        加载中...
      </div>
    );
  }

  if (!trip) return null;

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="text-slate-600 hover:text-slate-800"
          >
            ← 返回
          </button>
          <h1 className="text-lg font-bold text-slate-800 truncate max-w-xs">
            {trip.title}
          </h1>
          <button
            onClick={() => setShowAddForm(true)}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            + 添加足迹
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6">
        <div className="mb-6 text-sm text-slate-500">
          {trip.start_date} ~ {trip.end_date} · {trip.footprint_count} 个足迹
        </div>

        {footprints.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
            <p className="text-slate-500 mb-4">还没有足迹，去添加第一条记录吧。</p>
            <button
              onClick={() => setShowAddForm(true)}
              className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
            >
              添加足迹
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {footprints.map((fp) => (
              <div
                key={fp.id}
                className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden"
              >
                {fp.image_url && (
                  <img
                    src={fp.image_url}
                    alt={fp.note}
                    className="w-full h-48 object-cover"
                    loading="lazy"
                  />
                )}
                <div className="p-4">
                  <p className="text-slate-800 font-medium">{fp.note}</p>
                  <div className="mt-2 text-sm text-slate-500 flex items-center gap-3">
                    <span>{new Date(fp.recorded_at).toLocaleString('zh-CN')}</span>
                    {fp.location_name && <span>📍 {fp.location_name}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {showAddForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[9999] px-4">
          <div className="bg-white rounded-xl shadow-lg w-full max-w-md max-h-[90vh] overflow-y-auto p-6">
            <h2 className="text-lg font-bold text-slate-800 mb-4">添加足迹</h2>
            <form onSubmit={handleAddFootprint} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  照片
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  required={!imageUrl}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                {uploadingImage && (
                  <p className="text-xs text-slate-500 mt-1">上传中...</p>
                )}
                {imageUrl && (
                  <img
                    src={imageUrl}
                    alt="预览"
                    className="mt-2 w-full h-32 object-cover rounded-lg"
                  />
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  一句话描述
                </label>
                <input
                  type="text"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  required
                  maxLength={100}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="记录这一刻..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  记录时间
                </label>
                <input
                  type="datetime-local"
                  value={recordedAt}
                  onChange={(e) => setRecordedAt(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  位置坐标
                </label>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => setShowMapPicker(true)}
                    className="flex-1 py-2.5 bg-blue-50 text-blue-700 rounded-lg font-medium hover:bg-blue-100 transition border border-blue-200 text-sm"
                  >
                    {lat && lng ? '重新选点' : '🗺️ 在地图上选点'}
                  </button>
                  <button
                    type="button"
                    onClick={getLocation}
                    className="px-4 py-2.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition border border-blue-200"
                  >
                    自动定位
                  </button>
                </div>
                {lat && lng && (
                  <p className="mt-2 text-xs text-slate-500">
                    已选：纬度 {lat}，经度 {lng}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  地点名称（可选）
                </label>
                <input
                  type="text"
                  value={locationName}
                  onChange={(e) => setLocationName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="例如：东京塔"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 py-2.5 border border-slate-300 text-slate-700 rounded-lg font-medium hover:bg-slate-50 transition"
                >
                  取消
                </button>
                <button
                  type="submit"
                  disabled={submitting || uploadingImage || !imageUrl}
                  className="flex-1 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition"
                >
                  {submitting ? '保存中...' : uploadingImage ? '上传中...' : '保存'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showMapPicker && (
        <MapPickerModal
          onPick={(la, ln) => {
            setLat(la.toFixed(6));
            setLng(ln.toFixed(6));
          }}
          onClose={() => setShowMapPicker(false)}
        />
      )}
    </div>
  );
}
