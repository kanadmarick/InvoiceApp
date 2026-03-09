import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import {
  FileText,
  CheckCircle,
  Clock,
  AlertTriangle,
  Plus,
  Building2,
  ArrowRight,
} from 'lucide-react';

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount || 0);
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get('/api/dashboard/')
      .then(({ data }) => setStats(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
      </div>
    );
  }

  const cards = [
    {
      label: 'Total Invoices',
      value: stats?.total_invoices ?? 0,
      icon: FileText,
      gradient: 'from-blue-500 to-blue-600',
      sub: `${stats?.total_invoices ?? 0} invoices in system`,
    },
    {
      label: 'Paid Amount',
      value: formatCurrency(stats?.paid_amount),
      icon: CheckCircle,
      gradient: 'from-green-500 to-green-600',
      sub: 'Paid invoice total',
    },
    {
      label: 'Pending Amount',
      value: formatCurrency(stats?.pending_amount),
      icon: Clock,
      gradient: 'from-orange-500 to-orange-600',
      sub: `${stats?.pending_count ?? 0} invoices pending`,
    },
    {
      label: 'Overdue',
      value: formatCurrency(stats?.overdue_amount),
      icon: AlertTriangle,
      gradient: 'from-red-500 to-red-600',
      sub: `${stats?.overdue_count ?? 0} invoices overdue`,
    },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Dashboard</h2>

      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {cards.map((card) => (
          <div
            key={card.label}
            className={`bg-gradient-to-br ${card.gradient} rounded-xl shadow-lg p-6 text-white transform hover:scale-105 transition-transform duration-200`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium opacity-80">{card.label}</p>
                <h3 className="text-3xl font-bold mt-2">{card.value}</h3>
                <p className="text-xs mt-2 opacity-80">{card.sub}</p>
              </div>
              <div className="bg-white/20 rounded-full p-4">
                <card.icon className="w-8 h-8" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Link
          to="/invoices/new"
          className="bg-white rounded-xl shadow-md p-6 hover:shadow-xl transition-shadow duration-200 border-2 border-transparent hover:border-indigo-500"
        >
          <div className="flex items-center">
            <div className="bg-indigo-100 rounded-full p-3 mr-4">
              <Plus className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h4 className="font-bold text-gray-800 text-lg">Create New Invoice</h4>
              <p className="text-gray-500 text-sm">Generate a new invoice quickly</p>
            </div>
          </div>
        </Link>

        <Link
          to="/businesses/new"
          className="bg-white rounded-xl shadow-md p-6 hover:shadow-xl transition-shadow duration-200 border-2 border-transparent hover:border-purple-500"
        >
          <div className="flex items-center">
            <div className="bg-purple-100 rounded-full p-3 mr-4">
              <Building2 className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h4 className="font-bold text-gray-800 text-lg">Add Business</h4>
              <p className="text-gray-500 text-sm">Register a new business</p>
            </div>
          </div>
        </Link>

        <Link
          to="/invoices"
          className="bg-white rounded-xl shadow-md p-6 hover:shadow-xl transition-shadow duration-200 border-2 border-transparent hover:border-blue-500"
        >
          <div className="flex items-center">
            <div className="bg-blue-100 rounded-full p-3 mr-4">
              <ArrowRight className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h4 className="font-bold text-gray-800 text-lg">View All Invoices</h4>
              <p className="text-gray-500 text-sm">Browse and manage invoices</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent activity */}
      {stats?.recent_activity?.length > 0 && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {stats.recent_activity.map((item, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-indigo-500 rounded-full mr-3" />
                  <span className="text-gray-700">{item.description || item.invoice_number}</span>
                </div>
                <span className="text-sm text-gray-500">
                  {item.date && new Date(item.date).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
