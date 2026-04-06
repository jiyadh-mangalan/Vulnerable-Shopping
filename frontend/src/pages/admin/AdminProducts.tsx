import { FormEvent, useEffect, useState } from "react";
import { api } from "../../api";

type P = { id: number; name: string; price: string; stock: number };

export default function AdminProducts() {
  const [products, setProducts] = useState<P[]>([]);
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [stock, setStock] = useState("10");

  const load = () => {
    api.get("/admin/products").then((r) => setProducts(r.data.items || []));
  };

  useEffect(() => {
    load();
  }, []);

  const create = async (e: FormEvent) => {
    e.preventDefault();
    await api.post("/admin/products", {
      name,
      price: parseFloat(price) || 0,
      stock: parseInt(stock, 10) || 0,
    });
    setName("");
    setPrice("");
    load();
  };

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900 mb-4">Products</h1>

      <form onSubmit={create} className="bg-white rounded-lg shadow border p-4 mb-6 flex flex-wrap gap-3 items-end">
        <div>
          <label className="text-xs text-gray-600 block">Name</label>
          <input
            className="border rounded px-3 py-2"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="text-xs text-gray-600 block">Price</label>
          <input
            type="number"
            step="0.01"
            className="border rounded px-3 py-2 w-28"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
          />
        </div>
        <div>
          <label className="text-xs text-gray-600 block">Stock</label>
          <input
            type="number"
            className="border rounded px-3 py-2 w-24"
            value={stock}
            onChange={(e) => setStock(e.target.value)}
          />
        </div>
        <button
          type="submit"
          className="bg-amazon-accent text-black font-semibold px-4 py-2 rounded"
        >
          Add product
        </button>
      </form>

      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-3 font-semibold">ID</th>
              <th className="text-left p-3 font-semibold">Name</th>
              <th className="text-left p-3 font-semibold">Price</th>
              <th className="text-left p-3 font-semibold">Stock</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id} className="border-b border-gray-100">
                <td className="p-3">{p.id}</td>
                <td className="p-3">{p.name}</td>
                <td className="p-3">${p.price}</td>
                <td className="p-3">{p.stock}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
