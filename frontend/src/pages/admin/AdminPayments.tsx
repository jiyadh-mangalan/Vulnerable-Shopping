import { useEffect, useState } from "react";
import { api } from "../../api";

type P = {
  id: number;
  order_id: number;
  amount: string;
  card_last4?: string;
  status: string;
  customer_email: string;
  created_at?: string;
};

export default function AdminPayments() {
  const [payments, setPayments] = useState<P[]>([]);

  useEffect(() => {
    api.get("/admin/payments").then((r) => setPayments(r.data.payments || []));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900 mb-4">Payments</h1>
      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-3 font-semibold">ID</th>
              <th className="text-left p-3 font-semibold">Order</th>
              <th className="text-left p-3 font-semibold">Customer</th>
              <th className="text-left p-3 font-semibold">Amount</th>
              <th className="text-left p-3 font-semibold">Card</th>
              <th className="text-left p-3 font-semibold">Status</th>
              <th className="text-left p-3 font-semibold">When</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((p) => (
              <tr key={p.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="p-3">{p.id}</td>
                <td className="p-3 font-mono">{p.order_id}</td>
                <td className="p-3">{p.customer_email}</td>
                <td className="p-3">${p.amount}</td>
                <td className="p-3">{p.card_last4 || "—"}</td>
                <td className="p-3">{p.status}</td>
                <td className="p-3 text-xs text-gray-500">{p.created_at || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
