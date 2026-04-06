import { FormEvent, useState } from "react";
import { api } from "../api";

function unsafeMerge(target: any, source: any) {
  // VULN-FE-003: prototype pollution pattern (lab)
  for (const k of Object.keys(source)) {
    if (k === "__proto__" || k === "constructor") continue;
    (target as any)[k] = source[k];
  }
  return target;
}

export default function SettingsPage() {
  const [json, setJson] = useState('{"theme":"dark"}');
  const [preview, setPreview] = useState<any>({});

  const apply = (e: FormEvent) => {
    e.preventDefault();
    try {
      const parsed = JSON.parse(json);
      const base: any = {};
      const merged = unsafeMerge(base, parsed);
      setPreview(merged);
    } catch {
      alert("Invalid JSON");
    }
  };

  return (
    <div className="max-w-lg mx-auto bg-white p-8 rounded shadow">
      <h1 className="text-xl font-semibold mb-4">Account settings (lab)</h1>
      <p className="text-sm text-gray-600 mb-4">
        Merge helper demonstrates unsafe object merge — combine with backend mass assignment.
      </p>
      <form onSubmit={apply} className="space-y-4">
        <textarea
          className="w-full border rounded px-3 py-2 font-mono text-sm"
          rows={6}
          value={json}
          onChange={(e) => setJson(e.target.value)}
        />
        <button
          type="submit"
          className="bg-amazon-light text-white px-4 py-2 rounded"
        >
          Preview merge
        </button>
      </form>
      <pre className="mt-4 text-xs bg-gray-100 p-2 rounded overflow-auto">
        {JSON.stringify(preview, null, 2)}
      </pre>
    </div>
  );
}
