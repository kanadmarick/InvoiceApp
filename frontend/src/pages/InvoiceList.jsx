import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import { Plus, FileText, Search, Filter } from 'lucide-react';

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount || 0);
}

const statusColors = {
  PAID: 'bg-green-100 text-green-800',
  PENDING: 'bg-yellow-100 text-yellow-800',
  OVERDUE: 'bg-red-100 text-red-800',
  PARTIALLY_PAID: 'bg-blue-100 text-blue-800',
  DRAFT: 'bg-gray-100 text-gray-800',
};

export default function InvoiceList() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const fetchInvoices = () => {
    setLoading(true);
    const params = {};
    if (search) params.search = search;
    if (statusFilter) params.status = statusFilter;

    api
      .get('/billings/invoices/', { params })
      .then(({ data }) => setInvoices(data.results || data))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchInvoices();
  }, [statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchInvoices();
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
        <h2 className="text-2xl font-bold text-gray-800">Invoices</h2>
        <Link
          to="/invoices/new"
          className="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition font-medium"
        >
          <Plus className="w-5 h-5 mr-2" />
          New Invoice
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <form onSubmit={handleSearchSubmit} className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search invoices…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          />
        </form>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="pl-10 pr-8 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none appearance-none bg-white"
          >
            <option value="">All Statuses</option>
            <option value="PAID">Paid</option>
            <option value="PENDING">Pending</option>
            <option value="OVERDUE">Overdue</option>
            <option value="PARTIALLY_PAID">Partially Paid</option>
            <option value="DRAFT">Draft</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
        </div>
      ) : invoices.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl shadow-md">
          <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-600">No invoices found</h3>
          <p className="text-gray-400 mt-1">Create your first invoice to get started</p>
          <Link
            to="/invoices/new"
            className="inline-flex items-center mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Invoice
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Invoice #
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Client
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Business
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {invoices.map((inv) => (
                  <tr key={inv.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <Link
                        to={`/invoices/${inv.id}`}
                        className="text-indigo-600 hover:text-indigo-800 font-medium"
                      >
                        {inv.invoice_number}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-gray-700">{inv.client_name}</td>
                    <td className="px-6 py-4 text-gray-700">{inv.business_name}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex px-2.5 py-1 rounded-full text-xs font-semibold ${
                          statusColors[inv.status] || 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {inv.status?.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right font-medium text-gray-800">
                      {formatCurrency(inv.total_amount)}
                    </td>
                    <td className="px-6 py-4 text-gray-500 text-sm">
                      {new Date(inv.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
