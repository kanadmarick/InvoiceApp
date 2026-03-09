import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Home,
  Building2,
  FileText,
  Users,
  LogOut,
  Settings,
  Bell,
  Menu,
  X,
} from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { to: '/', icon: Home, label: 'Dashboard', end: true },
  { to: '/businesses', icon: Building2, label: 'Businesses' },
  { to: '/invoices', icon: FileText, label: 'Invoices' },
  { to: '/accounts', icon: Users, label: 'Accounts' },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const initial = user?.username?.charAt(0)?.toUpperCase() || '?';

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-30 w-64 bg-gradient-to-b from-indigo-600 to-indigo-800 text-white flex-shrink-0 shadow-xl transform transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-6 border-b border-indigo-500 flex items-center justify-between">
          <h1 className="text-2xl font-bold flex items-center">
            <FileText className="w-7 h-7 mr-3" />
            Invoice Pro
          </h1>
          <button className="lg:hidden" onClick={() => setSidebarOpen(false)}>
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="mt-6 px-4 flex-1">
          {navItems.map(({ to, icon: Icon, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center px-4 py-3 mb-2 rounded-lg transition-all duration-200 hover:bg-indigo-700 hover:translate-x-1 ${
                  isActive ? 'bg-indigo-700' : ''
                }`
              }
            >
              <Icon className="w-5 h-5 mr-3" />
              <span className="font-medium">{label}</span>
            </NavLink>
          ))}

          <div className="border-t border-indigo-500 my-4" />

          <button
            onClick={handleLogout}
            className="w-full flex items-center px-4 py-3 mb-2 rounded-lg transition-all duration-200 hover:bg-red-600 hover:translate-x-1 text-left"
          >
            <LogOut className="w-5 h-5 mr-3" />
            <span className="font-medium">Logout</span>
          </button>

          <a
            href={`${import.meta.env.VITE_API_URL || ''}/admin/`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center px-4 py-3 mb-2 rounded-lg transition-all duration-200 hover:bg-indigo-700 hover:translate-x-1"
          >
            <Settings className="w-5 h-5 mr-3" />
            <span className="font-medium">Admin Panel</span>
          </a>
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="bg-white shadow-sm z-10">
          <div className="flex items-center justify-between px-4 lg:px-8 py-4">
            <button className="lg:hidden p-2" onClick={() => setSidebarOpen(true)}>
              <Menu className="w-6 h-6 text-gray-600" />
            </button>
            <div className="flex-1" />
            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-lg hover:bg-gray-100 relative">
                <Bell className="w-5 h-5 text-gray-600" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              </button>
              <NavLink
                to={`/accounts/${user?.id}`}
                className="flex items-center hover:bg-gray-100 rounded-lg px-2 py-1 transition-colors duration-200"
              >
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-400 to-pink-400 flex items-center justify-center text-white font-bold">
                  {initial}
                </div>
                <span className="ml-2 text-gray-700 font-medium hidden sm:inline">
                  {user?.username}
                </span>
              </NavLink>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
