import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api";

type Row = {
  id: number;
  customer_email: string;
  total: string;
  status: string;
  payment_status: string;
  created_at?: string;
};

export default function AdminOrders() {
  const [orders, setOrders] = useState<Row[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    api.get("/admin/orders", { params: { per: 50 } }).then((r) => {
      setOrders(r.data.orders || []);
      setTotal(r.data.total ?? 0);
    });
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900 mb-4">Orders</h1>
      <p className="text-sm text-gray-600 mb-2">Total records: {total}</p>
      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-3 font-semibold">ID</th>
              <th className="text-left p-3 font-semibold">Customer</th>
              <th className="text-left p-3 font-semibold">Total</th>
              <th className="text-left p-3 font-semibold">Status</th>
              <th className="text-left p-3 font-semibold">Payment</th>
              <th className="text-left p-3 font-semibold">Created</th>
              <th className="text-left p-3 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="p-3 font-mono">{o.id}</td>
                <td className="p-3">{o.customer_email}</td>
                <td className="p-3">${o.total}</td>
                <td className="p-3">{o.status}</td>
                <td className="p-3">{o.payment_status}</td>
                <td className="p-3 text-xs text-gray-500">{o.created_at || "—"}</td>
                <td className="p-3">
                  <Link
                    to={`/admin/orders/${o.id}`}
                    className="text-blue-600 hover:underline"
                  >
                    View / edit
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
