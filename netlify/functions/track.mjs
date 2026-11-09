// Contador anónimo de visitas e cliques das landing pages (sem cookies, sem dados pessoais).
import { eventStore } from "../shared/leads.mjs";

const ALLOWED = new Set(["pv", "thanks", "cta", "tab", "plan", "gallery", "lang", "tel", "form_start",
  "submit_try", "submit_ok", "submit_err", "phone_invalid"]);

export default async (req) => {
  if (req.method !== "POST") return new Response("", { status: 405 });
  const ua = req.headers.get("user-agent") || "";
  if (/bot|crawl|spider|preview|headless|lighthouse/i.test(ua)) return new Response(null, { status: 204 });
  let b;
  try { b = JSON.parse((await req.text()).slice(0, 500)); } catch { return new Response("", { status: 400 }); }
  const e = String(b.e || "");
  if (!ALLOWED.has(e)) return new Response("", { status: 400 });
  const l = b.l === "en" ? "en" : "pt";
  const d = String(b.d || "-").replace(/[^\w-]/g, "").slice(0, 24) || "-";
  const day = new Date().toISOString().slice(0, 10);
  const rnd = Math.random().toString(36).slice(2, 8);
  await eventStore().set(`${day}/${e}/${l}/${d}/${Date.now()}${rnd}`, "1");
  return new Response(null, { status: 204 });
};

export const config = { path: "/api/track" };
