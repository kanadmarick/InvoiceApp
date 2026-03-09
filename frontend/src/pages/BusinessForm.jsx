import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { ArrowLeft, Save } from 'lucide-react';

const emptyForm = {
  name: '',
  email: '',
  gstin: '',
  brand_color: '#000000',
  address_line_1: '',
  address_line_2: '',
  city: '',
  state: '',
  pincode: '',
  country: 'India',
};

export default function BusinessForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [form, setForm] = useState(emptyForm);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(isEdit);

  useEffect(() => {
    if (isEdit) {
      api
        .get(`/businesses/${id}/`)
        .then(({ data }) => {
          setForm({
            name: data.name || '',
            email: data.email || '',
            gstin: data.gstin || '',
            brand_color: data.brand_color || '#000000',
            address_line_1: data.address_line_1 || '',
            address_line_2: data.address_line_2 || '',
            city: data.city || '',
            state: data.state || '',
            pincode: data.pincode || '',
            country: data.country || 'India',
          });
        })
        .catch(() => navigate('/businesses'))
        .finally(() => setFetching(false));
    }
  }, [id, isEdit, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);
    try {
      if (isEdit) {
        await api.put(`/businesses/${id}/`, form);
        navigate(`/businesses/${id}`);
      } else {
        const { data } = await api.post('/businesses/', form);
        navigate(`/businesses/${data.id}`);
      }
    } catch (err) {
      const data = err.response?.data;
      if (typeof data === 'object') {
        setErrors(data);
      }
    } finally {
      setLoading(false);
    }
  };

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  if (fetching) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
      </div>
    );
  }

  return (
    <div>
      <Link
        to={isEdit ? `/businesses/${id}` : '/businesses'}
        className="inline-flex items-center text-indigo-600 hover:text-indigo-800 mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        {isEdit ? 'Back to Business' : 'Back to Businesses'}
      </Link>

      <div className="bg-white rounded-xl shadow-md p-8 max-w-2xl">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">
          {isEdit ? 'Edit Business' : 'New Business'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Name & Email */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Name *
              </label>
              <input
                type="text"
                required
                value={form.name}
                onChange={set('name')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
              {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input
                type="email"
                required
                value={form.email}
                onChange={set('email')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
            </div>
          </div>

          {/* GSTIN & Brand Color */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">GSTIN</label>
              <input
                type="text"
                value={form.gstin}
                onChange={set('gstin')}
                placeholder="e.g. 22AAAAA0000A1Z5"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
              {errors.gstin && <p className="text-red-500 text-sm mt-1">{errors.gstin}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Brand Color</label>
              <div className="flex items-center gap-3">
                <input
                  type="color"
                  value={form.brand_color}
                  onChange={set('brand_color')}
                  className="w-12 h-12 rounded cursor-pointer border-0"
                />
                <input
                  type="text"
                  value={form.brand_color}
                  onChange={set('brand_color')}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                />
              </div>
            </div>
          </div>

          {/* Address */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 1</label>
            <input
              type="text"
              value={form.address_line_1}
              onChange={set('address_line_1')}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 2</label>
            <input
              type="text"
              value={form.address_line_2}
              onChange={set('address_line_2')}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
            />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
              <input
                type="text"
                value={form.city}
                onChange={set('city')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
              <input
                type="text"
                value={form.state}
                onChange={set('state')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Pincode</label>
              <input
                type="text"
                value={form.pincode}
                onChange={set('pincode')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
              <input
                type="text"
                value={form.country}
                onChange={set('country')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition disabled:opacity-50"
            >
              <Save className="w-5 h-5 mr-2" />
              {loading ? 'Saving…' : isEdit ? 'Update Business' : 'Create Business'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
