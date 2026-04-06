import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function OrdersPage() {
  const [orders, setOrders] = useState<any[]>([]);

  useEffect(() => {
    api.get("/orders").then((r) => setOrders(r.data.orders || []));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Your orders</h1>
      <div className="space-y-2">
        {orders.map((o) => (
          <Link
            key={o.id}
            to={`/orders/${o.id}`}
            className="block bg-white p-4 rounded shadow hover:bg-gray-50"
          >
            <div className="flex justify-between">
              <span>Order #{o.id}</span>
              <span className="font-semibold">${o.total}</span>
            </div>
            <div className="text-xs text-gray-500">{o.status} · {o.payment_status}</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
