// API só de leitura para sistemas externos (ex.: Youropa Dashboard).
// Autenticação: cabeçalho "Authorization: Bearer <API_KEY>" ou "x-api-key: <API_KEY>".
//
//   GET /api/v1/resumo?from=AAAA-MM-DD&to=AAAA-MM-DD   (ou ?days=30)
//       -> totais, série diária, por tipologia, por origem e lista de leads (sem contactos)
//   GET /api/v1/leads?from=...&to=...&status=sent|failed|imported&contacts=1
//       -> lista de leads; com contacts=1 inclui nome, email e telefone
//   GET /api/v1/leads.csv?...                           -> o mesmo em CSV
//
// Variáveis no Netlify: API_KEY (obrigatória), API_ORIGINS (opcional, domínios autorizados a
// chamar a API a partir do browser, separados por vírgula, ex: https://dashboard.youropapt.com).
import { timingSafeEqual, createHash } from "node:crypto";
import { getLeads, getEvents, lastDays, dayRange, REFS } from "../shared/leads.mjs";

const TYPES = ["T0", "T1", "T2", "T3"];

function cors(req) {
  const allowed = (process.env.API_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  const origin = req.headers.get("origin") || "";
  if (!origin || !allowed.includes(origin)) return {};
  return { "access-control-allow-origin": origin, "access-control-allow-headers": "authorization, x-api-key", "access-control-allow-methods": "GET", vary: "Origin" };
}
const reply = (req, body, status = 200, type = "application/json; charset=utf-8") =>
  new Response(typeof body === "string" ? body : JSON.stringify(body, null, 2), { status, headers: { "content-type": type, "cache-control": "no-store", ...cors(req) } });

function authorised(req) {
  const want = process.env.API_KEY || "";
  const got = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "") || req.headers.get("x-api-key") || "";
  if (!want || !got) return false;
  const a = createHash("sha256").update(want).digest(), b = createHash("sha256").update(got).digest();
  return timingSafeEqual(a, b);
}

const isDay = (s) => /^\d{4}-\d{2}-\d{2}$/.test(s || "");
const lisbonDay = (iso) => new Date(iso).toLocaleDateString("sv-SE", { timeZone: "Europe/Lisbon" });

function period(url) {
  const q = url.searchParams;
  if (isDay(q.get("from"))) {
    const to = isDay(q.get("to")) ? q.get("to") : new Date().toISOString().slice(0, 10);
    return { from: q.get("from"), to, days: dayRange(q.get("from"), to) };
  }
  const n = Math.min(Math.max(parseInt(q.get("days") || "30", 10) || 30, 1), 400);
  const days = lastDays(n);
  return { from: days[days.length - 1], to: days[0], days };
}

function leadOut(l, contacts) {
  const d = l.data || {};
  const o = {
    id: l.id, created_at: l.created_at, date: lisbonDay(l.created_at),
    typology: d.typology || "", ref: REFS[d.typology] || "", language: d.language || "",
    within_budget: d.within_budget || "", move_in_timing: d.move_in_timing || "",
    utm_source: d.utm_source || "", utm_medium: d.utm_medium || "", utm_campaign: d.utm_campaign || "",
    source: l.source, inmovilla_status: l.status, inmovilla_error: l.error || "",
  };
  if (contacts) Object.assign(o, { name: d.name || "", email: d.email || "", phone: d.phone || "" });
  return o;
}

function summarise(events, leads, p) {
  const sum = (ev, lang, detail, list = events) => list.reduce((t, d) => {
    for (const k in d.counts) { const [e, l, x] = k.split("|"); if (e === ev && (!lang || l === lang) && (!detail || x === detail)) t += d.counts[k]; }
    return t;
  }, 0);
  const inP = leads.filter((l) => { const d = lisbonDay(l.created_at); return d >= p.from && d <= p.to; });
  const visits = sum("pv"), sent = sum("submit_ok");
  return {
    period: { from: p.from, to: p.to, timezone_events: "UTC", timezone_leads: "Europe/Lisbon" },
    totals: {
      visits, visits_pt: sum("pv", "pt"), visits_en: sum("pv", "en"),
      cta_clicks: sum("cta"), form_started: sum("form_start"), form_sent: sent, thank_you_views: sum("thanks"),
      conversion_rate: visits ? +(sent / visits * 100).toFixed(2) : 0,
      leads: inP.length, leads_sent_to_inmovilla: inP.filter((l) => l.status === "sent").length,
      leads_failed: inP.filter((l) => l.status === "failed").length, phone_clicks: sum("tel"),
    },
    by_day: events.slice().reverse().map((d) => {
      const L = inP.filter((l) => lisbonDay(l.created_at) === d.day);
      return { date: d.day, visits: sum("pv", 0, 0, [d]), cta_clicks: sum("cta", 0, 0, [d]), form_started: sum("form_start", 0, 0, [d]), form_sent: sum("submit_ok", 0, 0, [d]), leads: L.length, leads_failed: L.filter((l) => l.status === "failed").length };
    }),
    by_typology: Object.fromEntries(TYPES.map((t) => [t, {
      ref: REFS[t], tab_views: sum("tab", 0, t), plan_views: sum("plan", 0, t), cta_clicks: sum("cta", 0, t),
      form_sent: sum("submit_ok", 0, t), leads: inP.filter((l) => (l.data || {}).typology === t).length,
    }])),
    by_source: { google_ads: sum("pv", 0, "google"), other_sites: sum("pv", 0, "ext"), direct: sum("pv", 0, "direct") },
    leads: inP.map((l) => leadOut(l, false)),
    generated_at: new Date().toISOString(),
  };
}

function toCSV(rows) {
  if (!rows.length) return "";
  const cols = Object.keys(rows[0]);
  const q = (v) => { const s = String(v ?? ""); return /[",\n;]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
  return "﻿" + [cols.join(","), ...rows.map((r) => cols.map((c) => q(r[c])).join(","))].join("\n");
}

export default async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(req) });
  if (req.method !== "GET") return reply(req, { error: "Only GET." }, 405);
  if (!process.env.API_KEY) return reply(req, { error: "API_KEY is not configured." }, 503);
  if (!authorised(req)) return reply(req, { error: "Invalid API key." }, 401);

  const url = new URL(req.url);
  const route = url.pathname.replace(/^\/api\/v1\/?/, "");
  const p = period(url);

  if (route === "resumo" || route === "summary") {
    const [events, leads] = await Promise.all([getEvents(p.days), getLeads()]);
    return reply(req, summarise(events, leads, p));
  }
  if (route === "leads" || route === "leads.csv") {
    const status = url.searchParams.get("status");
    const contacts = url.searchParams.get("contacts") === "1";
    const rows = (await getLeads())
      .filter((l) => { const d = lisbonDay(l.created_at); return d >= p.from && d <= p.to && (!status || l.status === status); })
      .map((l) => leadOut(l, contacts));
    if (route === "leads.csv") return reply(req, toCSV(rows), 200, "text/csv; charset=utf-8");
    return reply(req, { period: { from: p.from, to: p.to }, count: rows.length, leads: rows });
  }
  return reply(req, { error: "Unknown endpoint.", endpoints: ["/api/v1/resumo", "/api/v1/leads", "/api/v1/leads.csv"] }, 404);
};

export const config = { path: ["/api/v1/resumo", "/api/v1/summary", "/api/v1/leads", "/api/v1/leads.csv"] };
