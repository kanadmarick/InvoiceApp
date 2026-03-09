import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import { Users, Search, Crown } from 'lucide-react';

export default function AccountList() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    api
      .get('/accounts/users/')
      .then(({ data }) => setAccounts(data.results || data))
      .catch((err) => {
        if (err.response?.status === 403) {
          setError('Admin access required to view all accounts.');
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const filtered = accounts.filter(
    (a) =>
      a.username?.toLowerCase().includes(search.toLowerCase()) ||
      a.email?.toLowerCase().includes(search.toLowerCase()) ||
      a.full_name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Accounts</h2>

      {error && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search accounts…"
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
          <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-600">No accounts found</h3>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filtered.map((acct) => (
            <Link
              key={acct.id}
              to={`/accounts/${acct.id}`}
              className="bg-white rounded-xl shadow-md hover:shadow-xl transition-shadow p-6"
            >
              <div className="flex items-center gap-4">
                {acct.profile_image ? (
                  <img
                    src={acct.profile_image}
                    alt={acct.username}
                    className="w-14 h-14 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-14 h-14 rounded-full bg-gradient-to-r from-purple-400 to-pink-400 flex items-center justify-center text-white text-xl font-bold">
                    {acct.username?.charAt(0)?.toUpperCase() || '?'}
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-bold text-gray-800 truncate">{acct.username}</h3>
                    {acct.is_premium && (
                      <Crown className="w-4 h-4 text-yellow-500 flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-gray-500 text-sm truncate">{acct.email}</p>
                  {acct.full_name && (
                    <p className="text-gray-400 text-sm truncate">{acct.full_name}</p>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
