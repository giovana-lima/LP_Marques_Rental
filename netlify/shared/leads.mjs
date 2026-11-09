// Código partilhado pelas funções: formato do email para a Inmovilla, envio SMTP e registo dos leads.
import nodemailer from "nodemailer";
import { getStore } from "@netlify/blobs";

export const DEFAULT_TO = "i.youroparealestateportugal.14287@inmovilla.com";

// Referência do imóvel por tipologia
export const REFS = { T0: "YR00041", T1: "YR00042", T2: "YR00043", T3: "YR00096" };

// Campos do formulário que guardamos no registo (o resto é ignorado)
export const FIELDS = ["name", "email", "phone", "typology", "within_budget", "move_in_timing", "language",
  "property_ref", "campaign", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];

const clean = (v) => String(v ?? "").trim();

export function pick(data = {}) {
  const out = {};
  for (const f of FIELDS) if (data[f] != null && clean(data[f]) !== "") out[f] = clean(data[f]).slice(0, 300);
  return out;
}

export function buildEmail(data) {
  const name = clean(data.name);
  const typology = clean(data.typology);
  const origin = clean(data.language) === "en" ? "LP Marques Rental EN" : "LP Marques Rental PT";

  const subject = `New contact from: ${name}`;
  const text = [
    "Dear Client,",
    "Please find below the details of your new lead.",
    "",
    `email: ${clean(data.email)}`,
    `name: ${name}`,
    `phone number: ${clean(data.phone)}`,
    `Origin: ${origin}`,
    `Ref : ${REFS[typology] || ""}`,
    "",
    "Message:",
    "",
    "Que tipologia de apartamento procura?",
    typology,
    "",
    "O valor inicial da renda da tipologia que prefere está dentro do seu orçamento?",
    clean(data.within_budget),
    "",
    "Está disponível para mudar-se…",
    clean(data.move_in_timing),
    "",
    "Best of luck!",
  ].join("\n");

  return { subject, text };
}

export function transport() {
  const port = Number(process.env.SMTP_PORT || 465);
  return nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port,
    secure: port === 465,
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
  });
}

export async function sendLead(data) {
  const { subject, text } = buildEmail(data);
  await transport().sendMail({
    from: process.env.SMTP_FROM || process.env.SMTP_USER,
    to: process.env.LEAD_EMAIL_TO || DEFAULT_TO,
    subject,
    text,
  });
}

// Tenta enviar e devolve o registo atualizado (não lança erro)
export async function trySend(rec, tries = 2) {
  rec.attempts = rec.attempts || [];
  for (let i = 0; i < tries; i++) {
    try {
      await sendLead(rec.data);
      rec.attempts.push({ at: new Date().toISOString(), ok: true });
      rec.status = "sent";
      rec.error = "";
      return rec;
    } catch (e) {
      rec.attempts.push({ at: new Date().toISOString(), ok: false, error: String(e && e.message || e).slice(0, 300) });
      rec.status = "failed";
      rec.error = String(e && e.message || e).split("\n")[0].slice(0, 200);
      if (i < tries - 1) await new Promise((r) => setTimeout(r, 1500));
    }
  }
  return rec;
}

export const leadStore = () => getStore({ name: "leads", consistency: "strong" });
export const eventStore = () => getStore({ name: "events" });

// ---- Leitura dos registos (painel e API)
export async function listAll(store, prefix) {
  const keys = [];
  for await (const page of store.list({ prefix, paginate: true })) for (const b of page.blobs) keys.push(b.key);
  return keys;
}

export async function getLeads() {
  const store = leadStore();
  const keys = await listAll(store, "lead/");
  const recs = await Promise.all(keys.map((k) => store.get(k, { type: "json" })));
  return recs.filter(Boolean).sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
}

// Lista de dias (AAAA-MM-DD, UTC), do mais recente para o mais antigo
export function lastDays(n) {
  const out = [], now = Date.now();
  for (let i = 0; i < n; i++) out.push(new Date(now - i * 864e5).toISOString().slice(0, 10));
  return out;
}
export function dayRange(from, to) {
  const out = [];
  for (let t = Date.parse(to + "T00:00:00Z"); t >= Date.parse(from + "T00:00:00Z") && out.length < 400; t -= 864e5) out.push(new Date(t).toISOString().slice(0, 10));
  return out;
}

// Contagens por dia: [{ day, counts: { "evento|lingua|detalhe": n } }]
export async function getEvents(dayList) {
  const store = eventStore();
  const out = await Promise.all(dayList.map(async (day) => {
    const keys = await listAll(store, `${day}/`);
    const counts = {};
    for (const k of keys) {
      const [, e, l, d] = k.split("/");
      const id = `${e}|${l}|${d}`;
      counts[id] = (counts[id] || 0) + 1;
    }
    return { day, counts };
  }));
  return out.sort((a, b) => b.day.localeCompare(a.day));
}
