import { FormEvent, useState } from "react";
import { api } from "../../api";

export default function AdminTools() {
  const [pingHost, setPingHost] = useState("127.0.0.1");
  const [pingOut, setPingOut] = useState("");
  const [cfg, setCfg] = useState<any>(null);

  const ping = async (e: FormEvent) => {
    e.preventDefault();
    const { data } = await api.get("/admin/ping", { params: { host: pingHost } });
    setPingOut(JSON.stringify(data, null, 2));
  };

  const loadConfig = async () => {
    const { data } = await api.get("/admin/config");
    setCfg(data);
  };

  return (
    <div className="space-y-8 max-w-2xl">
      <h1 className="text-2xl font-semibold text-gray-900">Tools</h1>

      <section className="bg-white rounded-lg shadow border p-6">
        <h2 className="font-semibold mb-2">Export orders (no auth — VULN-057)</h2>
        <p className="text-sm text-gray-600 mb-3">
          Opens CSV in a new tab (lab: unauthenticated export).
        </p>
        <a
          href="/api/v1/admin/export/orders"
          target="_blank"
          rel="noreferrer"
          className="text-blue-600 underline text-sm"
        >
          Download orders_export.csv
        </a>
      </section>

      <section className="bg-white rounded-lg shadow border p-6">
        <h2 className="font-semibold mb-2">Ping (VULN-030)</h2>
        <form onSubmit={ping} className="flex gap-2 flex-wrap items-end">
          <div>
            <label className="text-xs text-gray-600 block">Host</label>
            <input
              className="border rounded px-3 py-2 font-mono text-sm"
              value={pingHost}
              onChange={(e) => setPingHost(e.target.value)}
            />
          </div>
          <button type="submit" className="bg-gray-800 text-white px-4 py-2 rounded text-sm">
            Run
          </button>
        </form>
        {pingOut ? (
          <pre className="mt-3 text-xs bg-gray-50 p-3 rounded overflow-auto max-h-48">{pingOut}</pre>
        ) : null}
      </section>

      <section className="bg-white rounded-lg shadow border p-6">
        <h2 className="font-semibold mb-2">Config leak (VULN-033)</h2>
        <button
          type="button"
          onClick={loadConfig}
          className="bg-red-700 text-white px-4 py-2 rounded text-sm"
        >
          Load secrets (admin JWT)
        </button>
        {cfg ? (
          <pre className="mt-3 text-xs bg-gray-50 p-3 rounded overflow-auto">{JSON.stringify(cfg, null, 2)}</pre>
        ) : null}
      </section>
    </div>
  );
}
