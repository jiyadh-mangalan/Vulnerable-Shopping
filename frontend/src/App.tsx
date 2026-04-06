import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import Layout from "./components/Layout";
import AdminLayout from "./pages/admin/AdminLayout";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminOrderDetail from "./pages/admin/AdminOrderDetail";
import AdminOrders from "./pages/admin/AdminOrders";
import AdminPayments from "./pages/admin/AdminPayments";
import AdminProducts from "./pages/admin/AdminProducts";
import AdminTools from "./pages/admin/AdminTools";
import AdminUsers from "./pages/admin/AdminUsers";
import CartPage from "./pages/Cart";
import CheckoutPage from "./pages/Checkout";
import Home from "./pages/Home";
import Login from "./pages/Login";
import OrderDetail from "./pages/OrderDetail";
import OrdersPage from "./pages/Orders";
import ProductPage from "./pages/Product";
import Register from "./pages/Register";
import SettingsPage from "./pages/Settings";

function Private({ children }: { children: JSX.Element }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function AdminOnly({ children }: { children: JSX.Element }) {
  const { user, token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  if (user?.role !== "admin") {
    return (
      <div className="bg-yellow-50 border border-yellow-200 p-4 rounded max-w-lg mx-auto mt-8">
        Admin JWT required — forge token with role=admin for lab.
      </div>
    );
  }
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="product/:id" element={<ProductPage />} />
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route
            path="cart"
            element={
              <Private>
                <CartPage />
              </Private>
            }
          />
          <Route
            path="checkout"
            element={
              <Private>
                <CheckoutPage />
              </Private>
            }
          />
          <Route
            path="orders"
            element={
              <Private>
                <OrdersPage />
              </Private>
            }
          />
          <Route
            path="orders/:id"
            element={
              <Private>
                <OrderDetail />
              </Private>
            }
          />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        <Route
          path="/admin"
          element={
            <AdminOnly>
              <AdminLayout />
            </AdminOnly>
          }
        >
          <Route index element={<AdminDashboard />} />
          <Route path="users" element={<AdminUsers />} />
          <Route path="orders" element={<AdminOrders />} />
          <Route path="orders/:id" element={<AdminOrderDetail />} />
          <Route path="payments" element={<AdminPayments />} />
          <Route path="products" element={<AdminProducts />} />
          <Route path="tools" element={<AdminTools />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
