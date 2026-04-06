import { useEffect, useState } from "react";
import { api } from "../../api";

type U = { id: number; email: string; role: string; full_name?: string };

export default function AdminUsers() {
  const [users, setUsers] = useState<U[]>([]);

  useEffect(() => {
    api.get("/admin/users").then((r) => setUsers(r.data.users || [])).catch(() => setUsers([]));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900 mb-4">Users</h1>
      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-3 font-semibold">ID</th>
              <th className="text-left p-3 font-semibold">Email</th>
              <th className="text-left p-3 font-semibold">Name</th>
              <th className="text-left p-3 font-semibold">Role</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="p-3">{u.id}</td>
                <td className="p-3 font-mono">{u.email}</td>
                <td className="p-3">{u.full_name || "—"}</td>
                <td className="p-3">
                  <span
                    className={
                      u.role === "admin"
                        ? "bg-yellow-100 text-yellow-900 px-2 py-0.5 rounded text-xs"
                        : ""
                    }
                  >
                    {u.role}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
