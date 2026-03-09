import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../context/AuthContext';
import {
  ArrowLeft,
  Mail,
  Phone,
  Crown,
  Pencil,
  Save,
  X,
  Calendar,
} from 'lucide-react';

export default function AccountDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: currentUser, updateUser } = useAuth();
  const [account, setAccount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});

  const isOwnProfile = currentUser?.id === id;

  useEffect(() => {
    api
      .get(`/accounts/users/${id}/`)
      .then(({ data }) => {
        setAccount(data);
        setForm({
          first_name: data.first_name || '',
          last_name: data.last_name || '',
          email: data.email || '',
          phone_number: data.phone_number || '',
          bio: data.bio || '',
        });
      })
      .catch(() => navigate('/accounts'))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const handleSave = async () => {
    setErrors({});
    setSaving(true);
    try {
      const { data } = await api.patch(`/accounts/users/${id}/`, form);
      setAccount(data);
      setEditing(false);
      if (isOwnProfile) {
        updateUser(data);
      }
    } catch (err) {
      const data = err.response?.data;
      if (typeof data === 'object') setErrors(data);
    } finally {
      setSaving(false);
    }
  };

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
      </div>
    );
  }

  if (!account) return null;

  const initial = account.username?.charAt(0)?.toUpperCase() || '?';

  return (
    <div>
      <Link
        to="/accounts"
        className="inline-flex items-center text-indigo-600 hover:text-indigo-800 mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Accounts
      </Link>

      <div className="bg-white rounded-xl shadow-md overflow-hidden max-w-3xl">
        {/* Header */}
        <div className="h-32 bg-gradient-to-r from-purple-500 to-pink-500 relative">
          <div className="absolute -bottom-12 left-8">
            {account.profile_image ? (
              <img
                src={account.profile_image}
                alt={account.username}
                className="w-24 h-24 rounded-full border-4 border-white shadow-lg object-cover"
              />
            ) : (
              <div className="w-24 h-24 rounded-full border-4 border-white shadow-lg bg-gradient-to-r from-purple-400 to-pink-400 flex items-center justify-center text-white text-3xl font-bold">
                {initial}
              </div>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="pt-16 px-8 pb-8">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-3xl font-bold text-gray-800">{account.username}</h1>
                {account.is_premium && <Crown className="w-5 h-5 text-yellow-500" />}
              </div>
              {account.full_name && (
                <p className="text-gray-500 mt-1">{account.full_name}</p>
              )}
            </div>
            {isOwnProfile && !editing && (
              <button
                onClick={() => setEditing(true)}
                className="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition"
              >
                <Pencil className="w-4 h-4 mr-2" />
                Edit Profile
              </button>
            )}
          </div>

          {editing ? (
            <div className="mt-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={form.first_name}
                    onChange={set('first_name')}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  />
                  {errors.first_name && (
                    <p className="text-red-500 text-sm mt-1">{errors.first_name}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={form.last_name}
                    onChange={set('last_name')}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={form.email}
                  onChange={set('email')}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                />
                {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                <input
                  type="text"
                  value={form.phone_number}
                  onChange={set('phone_number')}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
                <textarea
                  value={form.bio}
                  onChange={set('bio')}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none resize-none"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition disabled:opacity-50"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {saving ? 'Saving…' : 'Save Changes'}
                </button>
                <button
                  onClick={() => setEditing(false)}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="mt-6 space-y-4">
              <div className="flex items-center gap-3">
                <Mail className="w-5 h-5 text-gray-400" />
                <span className="text-gray-700">{account.email}</span>
              </div>
              {account.phone_number && (
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-700">{account.phone_number}</span>
                </div>
              )}
              {account.bio && (
                <div className="mt-4">
                  <h3 className="text-sm font-semibold text-gray-500 mb-1">Bio</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{account.bio}</p>
                </div>
              )}
              <div className="flex items-center gap-3 text-sm text-gray-400 mt-4">
                <Calendar className="w-4 h-4" />
                <span>Joined {new Date(account.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
