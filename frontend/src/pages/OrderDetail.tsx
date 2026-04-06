import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";

export default function OrderDetail() {
  const { id } = useParams();
  const [order, setOrder] = useState<any>(null);

  useEffect(() => {
    api.get(`/orders/${id}`).then((r) => setOrder(r.data.order));
  }, [id]);

  const downloadInvoice = async () => {
    const { data } = await api.get(`/orders/${id}/invoice`, { responseType: "text" });
    const blob = new Blob([data], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `invoice-${id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!order) return <p>Loading…</p>;

  return (
    <div className="bg-white p-6 rounded shadow max-w-2xl">
      <h1 className="text-2xl font-semibold mb-2">Order #{order.id}</h1>
      <p className="text-gray-600 text-sm mb-4">
        Total ${order.total} — {order.payment_status}
      </p>
      <ul className="divide-y">
        {order.items?.map((it: any, i: number) => (
          <li key={i} className="py-2 flex justify-between">
            <span>Product {it.product_id} × {it.quantity}</span>
            <span>${it.unit_price}</span>
          </li>
        ))}
      </ul>
      <button
        type="button"
        className="inline-block mt-4 text-blue-600 underline"
        onClick={() => downloadInvoice()}
      >
        Download invoice
      </button>
    </div>
  );
}
