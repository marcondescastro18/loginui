import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "https://login-api.znh7ry.easypanel.host";

export const api = axios.create({
  baseURL: API_URL,
});

