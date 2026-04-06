import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api";
import ProductImage from "../components/ProductImage";

type Product = {
  id: number;
  name: string;
  price: string;
  stock: number;
  image_url?: string;
};

export default function Home() {
  const [params] = useSearchParams();
  const q = params.get("q") || "";
  const categorySlug = params.get("category_slug") || "";
  const category = params.get("category") || "";
  const [items, setItems] = useState<Product[]>([]);
  const [domEcho, setDomEcho] = useState("");

  useEffect(() => {
    const load = async () => {
      if (q) {
        const { data } = await api.get("/products/search", { params: { q } });
        setItems(data.items || []);
      } else {
        const { data } = await api.get("/products", {
          params: category ? { category } : {},
        });
        setItems(data.items || []);
      }
    };
    load().catch(() => setItems([]));
  }, [q, category, categorySlug]);

  useEffect(() => {
    // VULN-FE-001: DOM XSS — query reflected without sanitization
    const sp = new URLSearchParams(window.location.search);
    const ref = sp.get("ref") || "";
    setDomEcho(ref);
  }, []);

  return (
    <div>
      {domEcho ? (
        <div
          className="mb-4 p-2 bg-yellow-50 border border-yellow-200 text-sm"
          dangerouslySetInnerHTML={{ __html: `Ref: ${domEcho}` }}
        />
      ) : null}
      <h1 className="text-2xl font-semibold mb-4 text-gray-800">
        {q ? `Results for "${q}"` : "Featured products"}
      </h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {items.map((p) => (
          <Link
            key={p.id}
            to={`/product/${p.id}`}
            className="bg-white rounded-lg shadow hover:shadow-lg transition border border-gray-200 overflow-hidden flex flex-col"
          >
            <ProductImage src={p.image_url} alt="" heightClass="h-40" />
            <div className="p-3 flex-1 flex flex-col">
              <div className="font-medium text-gray-900 line-clamp-2">{p.name}</div>
              <div className="mt-auto pt-2 text-lg font-semibold text-red-700">
                ${p.price}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
