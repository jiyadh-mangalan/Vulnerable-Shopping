import { FormEvent, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../../api";

export default function AdminOrderDetail() {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [order, setOrder] = useState<any>(null);
  const [items, setItems] = useState<any[]>([]);
  const [status, setStatus] = useState("");
  const [paymentStatus, setPaymentStatus] = useState("");
  const [adminNotes, setAdminNotes] = useState("");

  const load = () => {
    api.get(`/admin/orders/${id}`).then((r) => {
      setOrder(r.data.order);
      setItems(r.data.items || []);
      setStatus(r.data.order.status);
      setPaymentStatus(r.data.order.payment_status);
      setAdminNotes(r.data.order.admin_notes || "");
      setLoading(false);
    });
  };

  useEffect(() => {
    load();
  }, [id]);

  const save = async (e: FormEvent) => {
    e.preventDefault();
    await api.patch(`/admin/orders/${id}`, {
      status,
      payment_status: paymentStatus,
      admin_notes: adminNotes,
    });
    load();
  };

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

  const refund = async () => {
    await api.post(`/admin/orders/${id}/refund`, { reason: "admin refund" });
    load();
  };

  if (loading || !order) return <p className="text-gray-600">Loading…</p>;

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-semibold text-gray-900 mb-2">Order #{order.id}</h1>
      <p className="text-sm text-gray-600 mb-6">
        {order.customer_email} · ${order.total} · {order.created_at}
      </p>

      <div className="bg-white rounded-lg shadow border border-gray-200 p-6 mb-6">
        <h2 className="font-semibold mb-3">Line items</h2>
        <ul className="divide-y text-sm">
          {items.map((it, i) => (
            <li key={i} className="py-2 flex justify-between">
              <span>Product {it.product_id} × {it.quantity}</span>
              <span>${it.unit_price}</span>
            </li>
          ))}
        </ul>
        <div className="mt-4 flex gap-3">
          <button
            type="button"
            onClick={downloadInvoice}
            className="text-blue-600 text-sm underline"
          >
            Download invoice
          </button>
          <button
            type="button"
            onClick={refund}
            className="text-red-700 text-sm underline"
          >
            Issue refund (demo)
          </button>
        </div>
      </div>

      <form onSubmit={save} className="bg-white rounded-lg shadow border border-gray-200 p-6 space-y-4">
        <h2 className="font-semibold">Edit order</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <label className="block text-sm">
            <span className="text-gray-600">Status</span>
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            />
          </label>
          <label className="block text-sm">
            <span className="text-gray-600">Payment status</span>
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={paymentStatus}
              onChange={(e) => setPaymentStatus(e.target.value)}
            />
          </label>
        </div>
        <label className="block text-sm">
          <span className="text-gray-600">Admin notes (stored raw — VULN-055)</span>
          <textarea
            className="mt-1 w-full border rounded px-3 py-2 font-mono text-sm"
            rows={4}
            value={adminNotes}
            onChange={(e) => setAdminNotes(e.target.value)}
            placeholder="Internal notes…"
          />
        </label>
        {/* VULN-055: stored XSS preview — intentional for lab */}
        {adminNotes ? (
          <div className="border border-dashed border-orange-300 rounded p-3 bg-orange-50">
            <div className="text-xs text-orange-800 mb-1">Preview (dangerous):</div>
            <div
              className="text-sm prose max-w-none"
              dangerouslySetInnerHTML={{ __html: adminNotes }}
            />
          </div>
        ) : null}
        <button
          type="submit"
          className="bg-amazon-dark text-white px-4 py-2 rounded font-medium hover:bg-gray-800"
        >
          Save changes
        </button>
      </form>
    </div>
  );
}
