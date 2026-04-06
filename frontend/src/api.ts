import axios from "axios";

const base = import.meta.env.VITE_API_BASE_URL || "";

export const api = axios.create({
  baseURL: base || "/api/v1",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const t = localStorage.getItem("token");
  if (t) {
    config.headers.Authorization = `Bearer ${t}`;
  }
  return config;
});
