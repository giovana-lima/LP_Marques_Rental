# LP Marquês – Arrendamento (Youropa)

## Estrutura

```
public/                      -> o que fica online
  rent-porto-pt.html         landing page PT (abre na raiz do subdomínio)
  rent-porto-en.html         landing page EN
  obrigado-pt.html           página de obrigado PT (conversão Google Ads)
  thank-you-en.html          página de obrigado EN (conversão Google Ads)
  assets/fonts, assets/img   fontes e imagens
netlify/functions/
  submission-created.mjs     envia cada lead por email para a Inmovilla
netlify.toml                 configuração do Netlify
package.json                 dependência (nodemailer)
```

## Como funciona o formulário

1. O visitante envia o formulário → o Netlify Forms recebe os dados (aparecem em **Forms** no painel do Netlify).
2. O Netlify corre automaticamente a função `submission-created.mjs`.
3. A função envia o email para `i.youroparealestateportugal.14287@inmovilla.com`:
   - Assunto: `New contact from: {nome}`
   - Origin: `LP Marques Rental PT` ou `LP Marques Rental EN`, conforme a página
   - Ref: T0 → YR00041, T1 → YR00042, T2 → YR00043
4. O visitante vai para a página de obrigado.

## Configuração no Netlify (uma vez só)

1. Ligar o repositório do GitHub ao Netlify (as definições de build já estão no `netlify.toml`).
2. **Forms**: em *Site configuration > Forms*, ativar a deteção de formulários (Form detection) e fazer um novo deploy.
3. **Variáveis de ambiente**: em *Site configuration > Environment variables*, criar:

| Variável    | Exemplo (Gmail / Google Workspace)        |
|-------------|-------------------------------------------|
| SMTP_HOST   | smtp.gmail.com                            |
| SMTP_PORT   | 465                                       |
| SMTP_USER   | conta que envia, ex: leads@youropapt.com  |
| SMTP_PASS   | palavra-passe de aplicação dessa conta    |
| SMTP_FROM   | Youropa Leads <leads@youropapt.com>       |

   No Gmail, a "palavra-passe de aplicação" cria-se em *Conta Google > Segurança > Verificação em 2 passos > Palavras-passe de aplicação*.
   Para testar sem enviar para a Inmovilla, criar também `LEAD_EMAIL_TO` com o vosso email; depois apagar.

4. Fazer novo deploy, enviar um formulário de teste e confirmar que o lead entra na Inmovilla.

## Domínio

Em *Domain management*, adicionar o subdomínio (ex.: `arrendar.youropapt.com`) e criar o registo CNAME indicado pelo Netlify.
As duas línguas ficam no mesmo site: `/` (PT) e `/rent-porto-en.html` (EN). O botão de idioma funciona assim.

## Editar a landing page (versão "Jardins do Marquês")

As páginas `public/rent-porto-pt.html` e `public/rent-porto-en.html` são geradas por `tools/build_v2.py`
(textos PT/EN no início do ficheiro), `tools/v2.css` (estilo) e `tools/v2.js` (funcionamento).
Depois de alterar, correr `python3 tools/build_v2.py`. O Cookiebot, o GTM, o SEO e o rodapé são
mantidos a partir das páginas atuais. As fotos novas estão em `public/assets/img/v2/`.

## Painel e API

- **Painel:** `https://arrendar-marques.youropapt.com/painel` (senha = variável `PAINEL_PASSWORD`).
  Mostra os leads e se chegaram ao Inmovilla, permite reenviar, importar o CSV do Netlify Forms
  e testar a ligação ao Gmail. Também mostra visitas e cliques (contagem anónima, sem cookies).
- **API só de leitura** (para o Youropa Dashboard ou outros sistemas). Precisa da variável `API_KEY`.
  Enviar a chave no cabeçalho `Authorization: Bearer <API_KEY>`.

| Endereço | O que devolve |
| --- | --- |
| `/api/v1/resumo?days=30` ou `?from=2026-11-01&to=2026-11-30` | Totais, série diária, por tipologia, por origem e leads (sem contactos) |
| `/api/v1/leads?from=…&to=…&status=sent\|failed\|imported` | Lista de leads (sem contactos) |
| `/api/v1/leads?…&contacts=1` | Lista de leads com nome, email e telefone |
| `/api/v1/leads.csv?…` | O mesmo em CSV |

Exemplo (Python, na atualização do `data.json` do dashboard):

```python
import json, os, urllib.request
req = urllib.request.Request("https://arrendar-marques.youropapt.com/api/v1/resumo?days=90",
                             headers={"Authorization": "Bearer " + os.environ["MARQUES_API_KEY"]})
landing = json.load(urllib.request.urlopen(req))
data = json.load(open("data.json", encoding="utf-8"))
data["landingMarques"] = landing
json.dump(data, open("data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
```

Se o dashboard chamar a API diretamente no browser, o domínio dele tem de estar em `API_ORIGINS`
(ex.: `https://dashboard.youropapt.com`). Nesse caso a chave fica visível no código da página,
por isso é preferível ir buscar os dados na atualização do `data.json`.

Variáveis de ambiente usadas: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`,
`LEAD_EMAIL_TO` (opcional), `PAINEL_PASSWORD`, `API_KEY`, `API_ORIGINS` (opcional).
