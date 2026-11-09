// Dados do painel /painel (protegido pela senha PAINEL_PASSWORD).
//   GET  /api/painel?days=30              -> leads + contagem de visitas/cliques
//   POST /api/painel {action:"smtp"}       -> testa a ligação ao Gmail (sem enviar email)
//   POST /api/painel {action:"resend", ids:[...]}  -> reenvia leads para a Inmovilla
//   POST /api/painel {action:"import", rows:[...]} -> importa leads do CSV do Netlify Forms
import { timingSafeEqual, createHash } from "node:crypto";
import { leadStore, eventStore, trySend, transport, pick } from "../shared/leads.mjs";

const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });

function authorised(req) {
  const want = process.env.PAINEL_PASSWORD || "";
  const got = req.headers.get("x-painel-key") || "";
  if (!want) return false;
  const a = createHash("sha256").update(want).digest(), b = createHash("sha256").update(got).digest();
  return timingSafeEqual(a, b);
}

async function listAll(store, prefix) {
  const keys = [];
  for await (const page of store.list({ prefix, paginate: true })) for (const b of page.blobs) keys.push(b.key);
  return keys;
}

async function getLeads() {
  const store = leadStore();
  const keys = await listAll(store, "lead/");
  const recs = await Promise.all(keys.map((k) => store.get(k, { type: "json" })));
  return recs.filter(Boolean).sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
}

async function getEvents(days) {
  const store = eventStore();
  const out = [];
  const today = new Date();
  const dayList = [];
  for (let i = 0; i < days; i++) dayList.push(new Date(today.getTime() - i * 864e5).toISOString().slice(0, 10));
  await Promise.all(dayList.map(async (day) => {
    const keys = await listAll(store, `${day}/`);
    const counts = {};
    for (const k of keys) {
      const [, e, l, d] = k.split("/");
      const id = `${e}|${l}|${d}`;
      counts[id] = (counts[id] || 0) + 1;
    }
    out.push({ day, counts });
  }));
  return out.sort((a, b) => b.day.localeCompare(a.day));
}

export default async (req) => {
  if (!process.env.PAINEL_PASSWORD) return json({ error: "PAINEL_PASSWORD não está configurada no Netlify." }, 503);
  if (!authorised(req)) return json({ error: "Senha incorreta." }, 401);

  if (req.method === "GET") {
    const days = Math.min(Math.max(parseInt(new URL(req.url).searchParams.get("days") || "30", 10) || 30, 1), 90);
    const [leads, events] = await Promise.all([getLeads(), getEvents(days)]);
    return json({ leads, events, now: new Date().toISOString() });
  }

  if (req.method !== "POST") return json({ error: "Método não suportado." }, 405);
  let body;
  try { body = await req.json(); } catch { return json({ error: "Pedido inválido." }, 400); }

  if (body.action === "smtp") {
    try { await transport().verify(); return json({ ok: true }); }
    catch (e) { return json({ ok: false, error: String(e && e.message || e).split("\n")[0] }); }
  }

  if (body.action === "resend") {
    const store = leadStore();
    const ids = (body.ids || []).slice(0, 5).map(String);
    const results = [];
    for (const id of ids) {
      const rec = await store.get(`lead/${id}`, { type: "json" });
      if (!rec) { results.push({ id, status: "missing" }); continue; }
      await trySend(rec, 1);
      await store.setJSON(`lead/${id}`, rec);
      results.push({ id, status: rec.status, error: rec.error || "" });
    }
    return json({ results });
  }

  if (body.action === "import") {
    const store = leadStore();
    let added = 0, skipped = 0;
    await Promise.all((body.rows || []).slice(0, 100).map(async (row) => {
      const data = pick(row);
      if (!data.name && !data.email) { skipped++; return; }
      const created = String(row.created_at || "");
      const id = row.id ? String(row.id).replace(/[^\w-]/g, "") : "imp-" + createHash("sha1").update(created + data.email + data.phone).digest("hex").slice(0, 16);
      if (await store.get(`lead/${id}`)) { skipped++; return; }
      await store.setJSON(`lead/${id}`, { id, created_at: created || new Date().toISOString(), source: "import", status: "imported", data, attempts: [] });
      added++;
    }));
    return json({ added, skipped });
  }

  return json({ error: "Ação desconhecida." }, 400);
};

export const config = { path: "/api/painel" };
