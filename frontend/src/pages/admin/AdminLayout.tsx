import { Link, NavLink, Outlet } from "react-router-dom";

const nav = [
  { to: "/admin", end: true, label: "Dashboard" },
  { to: "/admin/users", label: "Users" },
  { to: "/admin/orders", label: "Orders" },
  { to: "/admin/payments", label: "Payments" },
  { to: "/admin/products", label: "Products" },
  { to: "/admin/tools", label: "Tools" },
];

export default function AdminLayout() {
  return (
    <div className="min-h-screen flex bg-gray-900 text-gray-100">
      <aside className="w-56 shrink-0 bg-amazon-dark border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <Link to="/" className="text-amazon-accent font-bold text-lg">
            VulnShop
          </Link>
          <div className="text-xs text-gray-400 mt-1">Admin console</div>
        </div>
        <nav className="flex-1 p-2 space-y-1">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `block px-3 py-2 rounded text-sm ${
                  isActive ? "bg-amazon-light text-white" : "text-gray-300 hover:bg-gray-800"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 text-xs text-gray-500 border-t border-gray-700">
          <Link to="/" className="text-amazon-accent hover:underline">
            ← Storefront
          </Link>
        </div>
      </aside>
      <main className="flex-1 overflow-auto bg-gray-100 text-gray-900 p-6">
        <Outlet />
      </main>
    </div>
  );
}
