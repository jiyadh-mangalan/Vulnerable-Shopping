import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../auth";

export default function Layout() {
  const { user, setUser, setToken } = useAuth();

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <header className="bg-amazon-dark text-white">
        <div className="max-w-7xl mx-auto flex items-center gap-4 px-4 py-2">
          <Link to="/" className="text-xl font-bold tracking-tight">
            Vuln<span className="text-amazon-accent">Shop</span>
          </Link>
          <form action="/" method="get" className="flex-1 flex max-w-2xl">
            <input
              name="q"
              className="flex-1 rounded-l-md px-3 py-2 text-black text-sm"
              placeholder="Search lab catalog"
            />
            <button
              type="submit"
              className="bg-amazon-accent text-black px-4 rounded-r-md font-semibold"
            >
              Go
            </button>
          </form>
          <nav className="flex items-center gap-3 text-sm">
            {user ? (
              <>
                <span className="text-gray-300">{user.email}</span>
                <Link to="/orders" className="hover:underline">
                  Orders
                </Link>
                <Link to="/cart" className="hover:underline">
                  Cart
                </Link>
                {user.role === "admin" && (
                  <Link to="/admin" className="hover:underline text-yellow-300">
                    Admin
                  </Link>
                )}
                <button
                  type="button"
                  className="hover:underline"
                  onClick={() => {
                    setToken(null);
                    setUser(null);
                  }}
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="hover:underline">
                  Login
                </Link>
                <Link to="/register" className="hover:underline">
                  Register
                </Link>
              </>
            )}
          </nav>
        </div>
        <div className="bg-amazon-light text-sm px-4 py-1 flex flex-wrap gap-4 max-w-7xl mx-auto">
          <Link to="/?category_slug=electronics">Electronics</Link>
          <Link to="/?category_slug=books">Books</Link>
          <Link to="/?category_slug=home">Home</Link>
          <Link to="/?category_slug=apparel">Apparel</Link>
          <Link to="/?category_slug=sports">Sports</Link>
          <Link to="/settings">Account settings</Link>
        </div>
      </header>
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        <Outlet />
      </main>
      <footer className="bg-amazon-light text-gray-200 text-xs py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4">
          Intentionally vulnerable lab application. Do not expose to the internet.
        </div>
      </footer>
    </div>
  );
}
