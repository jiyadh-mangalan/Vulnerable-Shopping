import { FormEvent, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import ProductImage from "../components/ProductImage";

type Review = {
  id: number;
  rating: number;
  title: string;
  body: string;
  author: string;
};

export default function ProductPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [product, setProduct] = useState<any>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");

  useEffect(() => {
    const load = async () => {
      const { data } = await api.get(`/products/${id}`);
      setProduct(data.product);
      const r = await api.get(`/products/${id}/reviews`);
      setReviews(r.data.reviews || []);
    };
    load();
  }, [id]);

  const submitReview = async (e: FormEvent) => {
    e.preventDefault();
    if (!user) return;
    await api.post(`/products/${id}/reviews`, { rating: 5, title, body });
    setTitle("");
    setBody("");
    const r = await api.get(`/products/${id}/reviews`);
    setReviews(r.data.reviews || []);
  };

  if (!product) return <p>Loading…</p>;

  return (
    <div className="grid md:grid-cols-2 gap-8">
      <div className="rounded-lg overflow-hidden border border-gray-200">
        <ProductImage
          key={product.id}
          src={product.image_url}
          alt={product.name || ""}
          heightClass="h-80 min-h-[20rem]"
        />
      </div>
      <div>
        <h1 className="text-3xl font-semibold">{product.name}</h1>
        <p className="text-2xl text-red-700 font-bold mt-2">${product.price}</p>
        <p className="text-gray-700 mt-4">{product.description}</p>
        <AddToCart productId={product.id} />

        <div className="mt-10">
          <h2 className="text-xl font-semibold mb-2">Reviews</h2>
          <div className="space-y-4">
            {reviews.map((r) => (
              <div key={r.id} className="border rounded p-3 bg-white">
                <div className="font-medium">{r.title}</div>
                {/* VULN-FE-002: stored XSS rendered */}
                <div
                  className="text-sm text-gray-700 mt-1"
                  dangerouslySetInnerHTML={{ __html: r.body }}
                />
                <div className="text-xs text-gray-400 mt-2">{r.author}</div>
              </div>
            ))}
          </div>
          {user ? (
            <form onSubmit={submitReview} className="mt-4 space-y-2">
              <input
                className="w-full border rounded px-3 py-2"
                placeholder="Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              <textarea
                className="w-full border rounded px-3 py-2"
                placeholder="Review (HTML allowed for lab)"
                rows={4}
                value={body}
                onChange={(e) => setBody(e.target.value)}
              />
              <button
                type="submit"
                className="bg-amazon-accent text-black px-4 py-2 rounded font-semibold"
              >
                Submit review
              </button>
            </form>
          ) : (
            <p className="text-sm text-gray-500 mt-2">Login to write a review.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function AddToCart({ productId }: { productId: number }) {
  const { user } = useAuth();
  const [qty, setQty] = useState(1);
  const [price, setPrice] = useState("");

  const add = async () => {
    if (!user) return;
    await api.post("/cart/items", {
      product_id: productId,
      quantity: qty,
      price: price || undefined,
    });
    alert("Added to cart");
  };

  return (
    <div className="mt-6 flex flex-col gap-2 max-w-xs">
      <label className="text-sm text-gray-600">
        Qty
        <input
          type="number"
          className="ml-2 border rounded px-2 py-1 w-20"
          value={qty}
          onChange={(e) => setQty(parseInt(e.target.value, 10) || 1)}
        />
      </label>
      <label className="text-sm text-gray-600">
        Optional client price (lab)
        <input
          className="ml-2 border rounded px-2 py-1 w-32"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          placeholder="override"
        />
      </label>
      <button
        type="button"
        onClick={add}
        className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-2 rounded"
      >
        Add to Cart
      </button>
    </div>
  );
}
