/**
 * Preference Chart Component
 * Visualisasi preferensi user menggunakan recharts
 */
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#0ea5e9', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'];

export const CuisineChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        Belum ada data masakan favorit
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="count" fill="#0ea5e9" name="Jumlah Pencarian" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export const LocationPieChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        Belum ada data lokasi favorit
      </div>
    );
  }

  const topLocations = data.slice(0, 6); // Ambil top 6 lokasi

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={topLocations}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percentage }) => `${name} (${percentage}%)`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="count"
        >
          {topLocations.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
};

export const ActivityChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        Belum ada data aktivitas
      </div>
    );
  }

  const formattedData = data.map(item => ({
    ...item,
    date: new Date(item.date).toLocaleDateString('id-ID', { 
      month: 'short', 
      day: 'numeric' 
    })
  }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={formattedData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="count" fill="#10b981" name="Jumlah Chat" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export const PreferenceStatsCard = ({ title, value, icon, color = 'primary' }) => {
  const colorClasses = {
    primary: 'bg-primary-100 text-primary-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-yellow-100 text-yellow-700',
    danger: 'bg-red-100 text-red-700',
    purple: 'bg-purple-100 text-purple-700',
  };

  return (
    <div className="card">
      <div className="flex items-center gap-4">
        <div className={`p-4 rounded-full ${colorClasses[color]}`}>
          {icon}
        </div>
        <div>
          <p className="text-gray-600 text-sm">{title}</p>
          <p className="text-2xl font-bold text-gray-800">{value || '-'}</p>
        </div>
      </div>
    </div>
  );
};

export const MoodsList = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        Belum ada data preferensi suasana
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {data.slice(0, 5).map((mood, index) => (
        <div key={index} className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-purple-500"></div>
            <span className="text-gray-700 capitalize">{mood.name}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-gray-600">{mood.count}x</span>
            <span className="text-xs text-gray-400">({mood.percentage}%)</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export const TopSearchesList = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        Belum ada riwayat pencarian
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {data.map((search, index) => (
        <div key={index} className="p-3 bg-gray-50 rounded-lg">
          <p className="text-gray-800 font-medium text-sm">{search.query}</p>
          <p className="text-xs text-gray-500 mt-1">
            {new Date(search.timestamp).toLocaleString('id-ID')}
          </p>
        </div>
      ))}
    </div>
  );
};
