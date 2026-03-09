import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../api';
import {
  ArrowLeft,
  Pencil,
  Trash2,
  Mail,
  MapPin,
  Hash,
  Calendar,
  CheckCircle,
  Clock,
  AlertTriangle,
  Download,
} from 'lucide-react';

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(amount || 0);
}

const statusConfig = {
  PAID: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
  PENDING: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
  OVERDUE: { color: 'bg-red-100 text-red-800', icon: AlertTriangle },
  PARTIALLY_PAID: { color: 'bg-blue-100 text-blue-800', icon: Clock },
  DRAFT: { color: 'bg-gray-100 text-gray-800', icon: Hash },
};

export default function InvoiceDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  useEffect(() => {
    api
      .get(`/billings/invoices/${id}/`)
      .then(({ data }) => setInvoice(data))
      .catch(() => navigate('/invoices'))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.delete(`/billings/invoices/${id}/`);
      navigate('/invoices');
    } catch {
      setDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      const response = await api.get(`/billings/invoices/${id}/pdf/`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice_${invoice?.invoice_number || id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF download failed:', err);
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
      </div>
    );
  }

  if (!invoice) return null;

  const st = statusConfig[invoice.status] || statusConfig.DRAFT;
  const StatusIcon = st.icon;

  const clientAddress = invoice.client
    ? [
        invoice.client.address_line_1,
        invoice.client.address_line_2,
        invoice.client.city,
        invoice.client.state,
        invoice.client.pincode,
        invoice.client.country,
      ]
        .filter(Boolean)
        .join(', ')
    : '';

  return (
    <div>
      <Link
        to="/invoices"
        className="inline-flex items-center text-indigo-600 hover:text-indigo-800 mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Invoices
      </Link>

      {/* Header card */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-gray-800">{invoice.invoice_number}</h1>
              <span
                className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-semibold ${st.color}`}
              >
                <StatusIcon className="w-4 h-4" />
                {invoice.status?.replace('_', ' ')}
              </span>
            </div>
            <p className="text-gray-500 mt-1">
              Created {new Date(invoice.created_at).toLocaleDateString()}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleDownloadPdf}
              disabled={downloadingPdf}
              className="inline-flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition disabled:opacity-50"
            >
              <Download className="w-4 h-4 mr-2" />
              {downloadingPdf ? 'Generating…' : 'Download PDF'}
            </button>
            <Link
              to={`/invoices/${id}/edit`}
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
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Client info */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Client Information</h3>
          {invoice.client && (
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <Hash className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm text-gray-500">Name</p>
                  <p className="text-gray-800 font-medium">{invoice.client.name}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Mail className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm text-gray-500">Email</p>
                  <p className="text-gray-800">{invoice.client.email}</p>
                </div>
              </div>
              {clientAddress && (
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm text-gray-500">Address</p>
                    <p className="text-gray-800">{clientAddress}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Line items */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Line Items</h3>
          {invoice.items?.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 text-sm font-semibold text-gray-500">#</th>
                    <th className="text-left py-2 text-sm font-semibold text-gray-500">
                      Description
                    </th>
                    <th className="text-right py-2 text-sm font-semibold text-gray-500">Qty</th>
                    <th className="text-right py-2 text-sm font-semibold text-gray-500">
                      Unit Price
                    </th>
                    <th className="text-right py-2 text-sm font-semibold text-gray-500">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {invoice.items.map((item, i) => (
                    <tr key={item.id || i}>
                      <td className="py-3 text-gray-500">{i + 1}</td>
                      <td className="py-3 text-gray-800">{item.description}</td>
                      <td className="py-3 text-right text-gray-700">{item.quantity}</td>
                      <td className="py-3 text-right text-gray-700">
                        {formatCurrency(item.unit_price)}
                      </td>
                      <td className="py-3 text-right font-medium text-gray-800">
                        {formatCurrency(item.line_total)}
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t-2 border-gray-300">
                    <td colSpan={4} className="py-3 text-right font-bold text-gray-800">
                      Total
                    </td>
                    <td className="py-3 text-right font-bold text-gray-800 text-lg">
                      {formatCurrency(invoice.total_amount)}
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          ) : (
            <p className="text-gray-400">No line items</p>
          )}
        </div>
      </div>

      {/* Milestones */}
      {invoice.milestones?.length > 0 && (
        <div className="bg-white rounded-xl shadow-md p-6 mt-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Milestones</h3>
          <div className="space-y-3">
            {invoice.milestones.map((ms, i) => {
              const msColor =
                ms.status === 'PAID'
                  ? 'bg-green-100 text-green-800'
                  : ms.status === 'OVERDUE'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-yellow-100 text-yellow-800';
              return (
                <div
                  key={ms.id || i}
                  className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-800">{ms.description}</p>
                      <p className="text-sm text-gray-500">
                        Due: {new Date(ms.due_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-medium text-gray-800">{formatCurrency(ms.amount)}</span>
                    <span
                      className={`inline-flex px-2.5 py-1 rounded-full text-xs font-semibold ${msColor}`}
                    >
                      {ms.status}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Notes */}
      {invoice.notes && (
        <div className="bg-white rounded-xl shadow-md p-6 mt-6">
          <h3 className="text-lg font-bold text-gray-800 mb-2">Notes</h3>
          <p className="text-gray-600 whitespace-pre-wrap">{invoice.notes}</p>
        </div>
      )}

      {/* Delete confirmation modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-bold text-gray-800">Delete Invoice</h3>
            <p className="text-gray-600 mt-2">
              Are you sure you want to delete <strong>{invoice.invoice_number}</strong>? This action
              cannot be undone.
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
