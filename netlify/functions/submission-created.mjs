// Corre automaticamente sempre que o Netlify recebe um formulário válido (evento "submission-created").
// Envia o lead para a Inmovilla e guarda o resultado (enviado / falhou) para o painel /painel.
//
// Variáveis de ambiente (Netlify > Site configuration > Environment variables):
//   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS  -> dados da conta de email que envia
//   SMTP_FROM                                   -> remetente
//   LEAD_EMAIL_TO (opcional)                    -> destino; por defeito o email da Inmovilla
//   PAINEL_PASSWORD                             -> senha da página /painel

import { connectLambda } from "@netlify/blobs";
import { pick, trySend, leadStore, buildEmail } from "../shared/leads.mjs";

export { buildEmail };

export const handler = async (event) => {
  const { payload } = JSON.parse(event.body);
  if (payload.form_name !== "lead") return { statusCode: 200, body: "ignored" };

  const rec = {
    id: String(payload.id || Date.now()),
    created_at: payload.created_at || new Date().toISOString(),
    source: "site",
    data: pick(payload.data || {}),
  };
  await trySend(rec);

  try {
    connectLambda(event);
    await leadStore(false).setJSON(`lead/${rec.id}`, rec);
  } catch (e) {
    console.error("Não foi possível guardar o registo do lead:", e && e.message);
  }

  if (rec.status !== "sent") {
    console.error(`FALHA no envio do lead ${rec.id} (${rec.data.name || ""}): ${rec.error}`);
    return { statusCode: 500, body: "send failed" };
  }
  return { statusCode: 200, body: "sent" };
};
