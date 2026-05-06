import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { api } from '../lib/api';
import CreateTripModal from '../components/CreateTripModal';
import TripMap from '../components/TripMap';

interface Trip {
  id: number;
  title: string;
  start_date: string;
  end_date: string;
  footprint_count: number;
  cover_image_url: string | null;
}

export default function HomePage() {
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const fetchTrips = async () => {
    try {
      const res = await api.get('/trips');
      setTrips(res.data);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrips();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-slate-800">迹录 StepMap</h1>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowModal(true)}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              + 新建旅行
            </button>
            <button
              onClick={logout}
              className="px-4 py-2 text-sm text-slate-600 hover:text-slate-800 border border-slate-300 rounded-lg hover:bg-slate-50 transition"
            >
              退出
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <TripMap />
        </div>

        {loading ? (
          <div className="text-center text-slate-400 py-12">加载中...</div>
        ) : trips.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
            <h2 className="text-lg font-semibold text-slate-700 mb-2">
              还没有旅行记录
            </h2>
            <p className="text-slate-500 mb-6">点击上方按钮创建你的第一条旅行。</p>
            <button
              onClick={() => setShowModal(true)}
              className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
            >
              创建旅行
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {trips.map((trip) => (
              <div
                key={trip.id}
                onClick={() => navigate(`/trips/${trip.id}`)}
                className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 cursor-pointer hover:shadow-md transition"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-800">
                      {trip.title}
                    </h3>
                    <p className="text-sm text-slate-500 mt-1">
                      {trip.start_date} ~ {trip.end_date}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-slate-100 text-slate-600">
                      {trip.footprint_count} 个足迹
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {showModal && (
        <CreateTripModal onClose={() => setShowModal(false)} onCreated={fetchTrips} />
      )}
    </div>
  );
}
