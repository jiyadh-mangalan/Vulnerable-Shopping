import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function CartPage() {
  const [data, setData] = useState<any>(null);

  const load = async () => {
    const { data } = await api.get("/cart");
    setData(data);
  };

  useEffect(() => {
    load().catch(() => setData(null));
  }, []);

  if (!data) return <p>Loading cart…</p>;

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Shopping Cart</h1>
      <div className="bg-white rounded shadow divide-y">
        {data.items?.map((it: any) => (
          <div key={it.id} className="p-4 flex justify-between">
            <div>
              <div className="font-medium">{it.name}</div>
              <div className="text-sm text-gray-500">
                Qty {it.quantity} × ${it.unit_price}
              </div>
            </div>
            <div className="font-semibold">${it.line_total}</div>
          </div>
        ))}
      </div>
      <div className="mt-4 flex justify-between items-center">
        <div className="text-xl font-bold">Subtotal: ${data.subtotal}</div>
        <Link
          to="/checkout"
          className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold px-6 py-2 rounded"
        >
          Proceed to checkout
        </Link>
      </div>
    </div>
  );
}
