import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

export default function CheckoutPage() {
  const [coupon, setCoupon] = useState("WELCOME10");
  const [subtotal, setSubtotal] = useState("");
  const nav = useNavigate();

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const body: any = {
      coupons: [coupon, "LAB50"],
      shipping_address: "123 Lab St",
    };
    if (subtotal) body.subtotal = parseFloat(subtotal);
    const { data } = await api.post("/checkout", body);
    await api.post(`/payments/${data.order_id}/capture`, { skip_payment: true });
    nav(`/orders/${data.order_id}`);
  };

  return (
    <div className="max-w-lg mx-auto bg-white p-8 rounded shadow">
      <h1 className="text-2xl font-semibold mb-4">Checkout</h1>
      <p className="text-sm text-gray-600 mb-4">
        Lab flow: optional client subtotal override and stacked coupons — then simulated payment.
      </p>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm text-gray-600">Coupon</label>
          <input
            className="w-full border rounded px-3 py-2"
            value={coupon}
            onChange={(e) => setCoupon(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm text-gray-600">
            Optional subtotal override (lab)
          </label>
          <input
            className="w-full border rounded px-3 py-2"
            value={subtotal}
            onChange={(e) => setSubtotal(e.target.value)}
            placeholder="leave empty for server"
          />
        </div>
        <button
          type="submit"
          className="w-full bg-amazon-accent text-black font-semibold py-2 rounded"
        >
          Place order
        </button>
      </form>
    </div>
  );
}
