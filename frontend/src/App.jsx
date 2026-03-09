import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import BusinessList from './pages/BusinessList';
import BusinessDetail from './pages/BusinessDetail';
import BusinessForm from './pages/BusinessForm';
import InvoiceList from './pages/InvoiceList';
import InvoiceDetail from './pages/InvoiceDetail';
import InvoiceForm from './pages/InvoiceForm';
import AccountList from './pages/AccountList';
import AccountDetail from './pages/AccountDetail';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function GuestRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/" replace /> : children;
}

export default function App() {
  return (
    <Routes>
      {/* Auth pages — no sidebar */}
      <Route path="/login" element={<GuestRoute><Login /></GuestRoute>} />
      <Route path="/register" element={<GuestRoute><Register /></GuestRoute>} />

      {/* Protected pages — with sidebar layout */}
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="businesses" element={<BusinessList />} />
        <Route path="businesses/new" element={<BusinessForm />} />
        <Route path="businesses/:id" element={<BusinessDetail />} />
        <Route path="businesses/:id/edit" element={<BusinessForm />} />
        <Route path="invoices" element={<InvoiceList />} />
        <Route path="invoices/new" element={<InvoiceForm />} />
        <Route path="invoices/:id" element={<InvoiceDetail />} />
        <Route path="invoices/:id/edit" element={<InvoiceForm />} />
        <Route path="accounts" element={<AccountList />} />
        <Route path="accounts/:id" element={<AccountDetail />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
