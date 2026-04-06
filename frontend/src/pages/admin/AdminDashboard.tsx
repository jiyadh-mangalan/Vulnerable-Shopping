import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api";

export default function AdminDashboard() {
  const [stats, setStats] = useState<{
    users: number;
    orders: number;
    revenue_paid: string;
    unpaid_orders: number;
  } | null>(null);

  useEffect(() => {
    api.get("/admin/stats").then((r) => setStats(r.data)).catch(() => setStats(null));
  }, []);

  if (!stats) return <p className="text-gray-600">Loading…</p>;

  const cards = [
    { label: "Users", value: stats.users, link: "/admin/users" },
    { label: "Orders", value: stats.orders, link: "/admin/orders" },
    { label: "Revenue (paid)", value: `$${stats.revenue_paid}`, link: "/admin/payments" },
    { label: "Unpaid orders", value: stats.unpaid_orders, link: "/admin/orders" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((c) => (
          <Link
            key={c.label}
            to={c.link}
            className="bg-white rounded-lg shadow border border-gray-200 p-6 hover:shadow-md transition"
          >
            <div className="text-sm text-gray-500">{c.label}</div>
            <div className="text-2xl font-bold text-amazon-dark mt-1">{c.value}</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
