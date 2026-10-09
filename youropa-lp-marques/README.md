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
