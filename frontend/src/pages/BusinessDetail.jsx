import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../api';
import { Pencil, Trash2, ArrowLeft, Mail, MapPin, Hash } from 'lucide-react';

export default function BusinessDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [business, setBusiness] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    api
      .get(`/businesses/${id}/`)
      .then(({ data }) => setBusiness(data))
      .catch(() => navigate('/businesses'))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.delete(`/businesses/${id}/`);
      navigate('/businesses');
    } catch {
      setDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
      </div>
    );
  }

  if (!business) return null;

  const address = [
    business.address_line_1,
    business.address_line_2,
    business.city,
    business.state,
    business.pincode,
    business.country,
  ]
    .filter(Boolean)
    .join(', ');

  return (
    <div>
      <Link to="/businesses" className="inline-flex items-center text-indigo-600 hover:text-indigo-800 mb-6">
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Businesses
      </Link>

      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        {/* Header */}
        <div
          className="h-32 relative"
          style={{ backgroundColor: business.brand_color || '#6366f1' }}
        >
          <div className="absolute -bottom-12 left-8">
            {business.logo ? (
              <img
                src={business.logo}
                alt={business.name}
                className="w-24 h-24 rounded-xl border-4 border-white shadow-lg object-cover bg-white"
              />
            ) : (
              <div className="w-24 h-24 rounded-xl border-4 border-white shadow-lg bg-white flex items-center justify-center text-3xl font-bold text-gray-400">
                {business.name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="pt-16 px-8 pb-8">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">{business.name}</h1>
              <p className="text-gray-500 mt-1">Owned by {business.owner}</p>
            </div>
            <div className="flex gap-2">
              <Link
                to={`/businesses/${id}/edit`}
                className="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition"
              >
                <Pencil className="w-4 h-4 mr-2" />
                Edit
              </Link>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            <div className="flex items-start gap-3">
              <Mail className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="text-gray-800">{business.email}</p>
              </div>
            </div>

            {business.gstin && (
              <div className="flex items-start gap-3">
                <Hash className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">GSTIN</p>
                  <p className="text-gray-800">{business.gstin}</p>
                </div>
              </div>
            )}

            {address && (
              <div className="flex items-start gap-3 md:col-span-2">
                <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Address</p>
                  <p className="text-gray-800">{address}</p>
                </div>
              </div>
            )}
          </div>

          <div className="mt-6 flex items-center gap-2 text-sm text-gray-400">
            <span>Created {new Date(business.created_at).toLocaleDateString()}</span>
            <span>·</span>
            <span>Updated {new Date(business.updated_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>

      {/* Delete confirmation modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-bold text-gray-800">Delete Business</h3>
            <p className="text-gray-600 mt-2">
              Are you sure you want to delete <strong>{business.name}</strong>? This action cannot
              be undone.
            </p>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition disabled:opacity-50"
              >
                {deleting ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
