import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import { Plus, Building2, Search } from 'lucide-react';

export default function BusinessList() {
  const [businesses, setBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api
      .get('/businesses/')
      .then(({ data }) => setBusinesses(data.results || data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = businesses.filter(
    (b) =>
      b.name.toLowerCase().includes(search.toLowerCase()) ||
      b.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
        <h2 className="text-2xl font-bold text-gray-800">Businesses</h2>
        <Link
          to="/businesses/new"
          className="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition font-medium"
        >
          <Plus className="w-5 h-5 mr-2" />
          Add Business
        </Link>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search businesses…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
        />
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl shadow-md">
          <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-600">No businesses found</h3>
          <p className="text-gray-400 mt-1">Create your first business to get started</p>
          <Link
            to="/businesses/new"
            className="inline-flex items-center mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Business
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filtered.map((biz) => (
            <Link
              key={biz.id}
              to={`/businesses/${biz.id}`}
              className="bg-white rounded-xl shadow-md hover:shadow-xl transition-shadow p-6 border-l-4"
              style={{ borderLeftColor: biz.brand_color || '#6366f1' }}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-bold text-gray-800">{biz.name}</h3>
                  <p className="text-gray-500 text-sm mt-1">{biz.email}</p>
                </div>
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white text-lg font-bold"
                  style={{ backgroundColor: biz.brand_color || '#6366f1' }}
                >
                  {biz.name.charAt(0).toUpperCase()}
                </div>
              </div>
              <div className="mt-4 text-xs text-gray-400">
                Created {new Date(biz.created_at).toLocaleDateString()}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
