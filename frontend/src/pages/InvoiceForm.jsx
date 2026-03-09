import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { ArrowLeft, Save, Plus, Trash2 } from 'lucide-react';

const emptyItem = { description: '', quantity: 1, unit_price: 0 };
const emptyMilestone = { description: '', amount: 0, due_date: '', status: 'PENDING' };

export default function InvoiceForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [businesses, setBusinesses] = useState([]);
  const [form, setForm] = useState({
    business: '',
    client_name: '',
    client_email: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    state: '',
    pincode: '',
    country: 'India',
    invoice_number: '',
    notes: '',
  });
  const [items, setItems] = useState([{ ...emptyItem }]);
  const [milestones, setMilestones] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);

  // Fetch businesses for dropdown
  useEffect(() => {
    api
      .get('/businesses/')
      .then(({ data }) => {
        const list = data.results || data;
        setBusinesses(list);
        if (!isEdit && list.length === 1) {
          setForm((f) => ({ ...f, business: list[0].id }));
        }
      })
      .catch(() => {});
  }, [isEdit]);

  // Fetch invoice for edit
  useEffect(() => {
    if (isEdit) {
      api
        .get(`/billings/invoices/${id}/`)
        .then(({ data }) => {
          setForm({
            business: data.client?.business || '',
            client_name: data.client?.name || '',
            client_email: data.client?.email || '',
            address_line_1: data.client?.address_line_1 || '',
            address_line_2: data.client?.address_line_2 || '',
            city: data.client?.city || '',
            state: data.client?.state || '',
            pincode: data.client?.pincode || '',
            country: data.client?.country || 'India',
            invoice_number: data.invoice_number || '',
            notes: data.notes || '',
          });
          setItems(
            data.items?.length > 0
              ? data.items.map((it) => ({
                  description: it.description,
                  quantity: it.quantity,
                  unit_price: it.unit_price,
                }))
              : [{ ...emptyItem }]
          );
          setMilestones(
            data.milestones?.map((ms) => ({
              description: ms.description,
              amount: ms.amount,
              due_date: ms.due_date,
              status: ms.status,
            })) || []
          );
        })
        .catch(() => navigate('/invoices'))
        .finally(() => setFetching(false));
    } else {
      setFetching(false);
    }
  }, [id, isEdit, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);

    const payload = {
      ...form,
      items: items.filter((it) => it.description),
      milestones: milestones.filter((ms) => ms.description),
    };

    try {
      if (isEdit) {
        await api.put(`/billings/invoices/${id}/`, payload);
        navigate(`/invoices/${id}`);
      } else {
        const { data } = await api.post('/billings/invoices/', payload);
        navigate(`/invoices/${data.id}`);
      }
    } catch (err) {
      const data = err.response?.data;
      if (typeof data === 'object') setErrors(data);
    } finally {
      setLoading(false);
    }
  };

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const updateItem = (index, field, value) => {
    const next = [...items];
    next[index] = { ...next[index], [field]: value };
    setItems(next);
  };

  const addItem = () => setItems([...items, { ...emptyItem }]);
  const removeItem = (i) => setItems(items.filter((_, idx) => idx !== i));

  const updateMilestone = (index, field, value) => {
    const next = [...milestones];
    next[index] = { ...next[index], [field]: value };
    setMilestones(next);
  };

  const addMilestone = () => setMilestones([...milestones, { ...emptyMilestone }]);
  const removeMilestone = (i) => setMilestones(milestones.filter((_, idx) => idx !== i));

  const lineTotal = (item) =>
    (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0);
  const grandTotal = items.reduce((sum, it) => sum + lineTotal(it), 0);

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
        to={isEdit ? `/invoices/${id}` : '/invoices'}
        className="inline-flex items-center text-indigo-600 hover:text-indigo-800 mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        {isEdit ? 'Back to Invoice' : 'Back to Invoices'}
      </Link>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Business & Invoice Number */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">
            {isEdit ? 'Edit Invoice' : 'New Invoice'}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Business *</label>
              <select
                required
                value={form.business}
                onChange={set('business')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none bg-white"
              >
                <option value="">Select a business</option>
                {businesses.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
              {errors.business && <p className="text-red-500 text-sm mt-1">{errors.business}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Invoice Number
              </label>
              <input
                type="text"
                value={form.invoice_number}
                onChange={set('invoice_number')}
                placeholder="Auto-generated if blank"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
              {errors.invoice_number && (
                <p className="text-red-500 text-sm mt-1">{errors.invoice_number}</p>
              )}
            </div>
          </div>
        </div>

        {/* Client info */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Client Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Client Name *
              </label>
              <input
                type="text"
                required
                value={form.client_name}
                onChange={set('client_name')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
              {errors.client_name && (
                <p className="text-red-500 text-sm mt-1">{errors.client_name}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Client Email *
              </label>
              <input
                type="email"
                required
                value={form.client_email}
                onChange={set('client_email')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
              {errors.client_email && (
                <p className="text-red-500 text-sm mt-1">{errors.client_email}</p>
              )}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address Line 1
              </label>
              <input
                type="text"
                value={form.address_line_1}
                onChange={set('address_line_1')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address Line 2
              </label>
              <input
                type="text"
                value={form.address_line_2}
                onChange={set('address_line_2')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mt-5">
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
        </div>

        {/* Line items */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-800">Line Items</h3>
            <button
              type="button"
              onClick={addItem}
              className="inline-flex items-center px-3 py-1.5 text-sm bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition"
            >
              <Plus className="w-4 h-4 mr-1" />
              Add Item
            </button>
          </div>

          <div className="space-y-3">
            {items.map((item, i) => (
              <div key={i} className="flex gap-3 items-start">
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="Description"
                    value={item.description}
                    onChange={(e) => updateItem(i, 'description', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm"
                  />
                </div>
                <div className="w-24">
                  <input
                    type="number"
                    placeholder="Qty"
                    min="0"
                    step="0.01"
                    value={item.quantity}
                    onChange={(e) => updateItem(i, 'quantity', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm text-right"
                  />
                </div>
                <div className="w-32">
                  <input
                    type="number"
                    placeholder="Unit Price"
                    min="0"
                    step="0.01"
                    value={item.unit_price}
                    onChange={(e) => updateItem(i, 'unit_price', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm text-right"
                  />
                </div>
                <div className="w-32 flex items-center justify-end">
                  <span className="text-sm font-medium text-gray-700 mr-2">
                    ₹{lineTotal(item).toFixed(2)}
                  </span>
                  {items.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeItem(i)}
                      className="p-1 text-red-400 hover:text-red-600"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200 text-right">
            <span className="text-lg font-bold text-gray-800">Total: ₹{grandTotal.toFixed(2)}</span>
          </div>

          {errors.items && <p className="text-red-500 text-sm mt-2">{errors.items}</p>}
        </div>

        {/* Milestones */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-800">Milestones (Optional)</h3>
            <button
              type="button"
              onClick={addMilestone}
              className="inline-flex items-center px-3 py-1.5 text-sm bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition"
            >
              <Plus className="w-4 h-4 mr-1" />
              Add Milestone
            </button>
          </div>

          {milestones.length === 0 ? (
            <p className="text-gray-400 text-sm">No milestones. Click "Add Milestone" to track payment schedules.</p>
          ) : (
            <div className="space-y-3">
              {milestones.map((ms, i) => (
                <div key={i} className="flex gap-3 items-start">
                  <div className="flex-1">
                    <input
                      type="text"
                      placeholder="Description"
                      value={ms.description}
                      onChange={(e) => updateMilestone(i, 'description', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm"
                    />
                  </div>
                  <div className="w-28">
                    <input
                      type="number"
                      placeholder="Amount"
                      min="0"
                      step="0.01"
                      value={ms.amount}
                      onChange={(e) => updateMilestone(i, 'amount', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm text-right"
                    />
                  </div>
                  <div className="w-36">
                    <input
                      type="date"
                      value={ms.due_date}
                      onChange={(e) => updateMilestone(i, 'due_date', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm"
                    />
                  </div>
                  <div className="w-28">
                    <select
                      value={ms.status}
                      onChange={(e) => updateMilestone(i, 'status', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm bg-white"
                    >
                      <option value="PENDING">Pending</option>
                      <option value="PAID">Paid</option>
                      <option value="OVERDUE">Overdue</option>
                    </select>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeMilestone(i)}
                    className="p-1 text-red-400 hover:text-red-600 mt-1"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Notes */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Notes</h3>
          <textarea
            value={form.notes}
            onChange={set('notes')}
            rows={3}
            placeholder="Any additional notes for the invoice…"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none resize-none"
          />
        </div>

        {/* Submit */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition disabled:opacity-50"
          >
            <Save className="w-5 h-5 mr-2" />
            {loading ? 'Saving…' : isEdit ? 'Update Invoice' : 'Create Invoice'}
          </button>
        </div>
      </form>
    </div>
  );
}
