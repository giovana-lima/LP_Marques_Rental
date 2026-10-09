// Corre automaticamente sempre que o Netlify recebe um formulário válido (evento "submission-created").
// Envia o lead para a Inmovilla no formato combinado.
//
// Variáveis de ambiente (Netlify > Site configuration > Environment variables):
//   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS  -> dados da conta de email que envia
//   SMTP_FROM                                   -> remetente, ex: "Youropa <leads@youropapt.com>"
//   LEAD_EMAIL_TO (opcional)                    -> destino; por defeito o email da Inmovilla abaixo

import nodemailer from "nodemailer";

const DEFAULT_TO = "i.youroparealestateportugal.14287@inmovilla.com";

// Referência do imóvel por tipologia
const REFS = { T0: "YR00041", T1: "YR00042", T2: "YR00043" };

export function buildEmail(data) {
  const clean = (v) => String(v ?? "").trim();
  const name = clean(data.name);
  const typology = clean(data.typology);
  const origin =
    clean(data.language) === "en" ? "LP Marques Rental EN" : "LP Marques Rental PT";

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

export const handler = async (event) => {
  const { payload } = JSON.parse(event.body);
  if (payload.form_name !== "lead") return { statusCode: 200, body: "ignored" };

  const { subject, text } = buildEmail(payload.data || {});

  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT || 465),
    secure: Number(process.env.SMTP_PORT || 465) === 465,
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
  });

  await transporter.sendMail({
    from: process.env.SMTP_FROM || process.env.SMTP_USER,
    to: process.env.LEAD_EMAIL_TO || DEFAULT_TO,
    subject,
    text,
  });

  return { statusCode: 200, body: "sent" };
};
