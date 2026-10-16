      // ---- Cabeçalho: fica sólido ao fazer scroll; menu no telemóvel
      var topbar = document.getElementById("top");
      function onScroll() { topbar.classList.toggle("solid", window.scrollY > 40); }
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
      var burger = document.querySelector(".burger"), mainnav = document.getElementById("mainnav");
      burger.addEventListener("click", function () {
        var open = mainnav.classList.toggle("open");
        burger.setAttribute("aria-expanded", open ? "true" : "false");
        document.body.style.overflow = open ? "hidden" : "";
      });
      mainnav.querySelectorAll("a").forEach(function (a) {
        a.addEventListener("click", function () {
          mainnav.classList.remove("open");
          burger.setAttribute("aria-expanded", "false");
          document.body.style.overflow = "";
        });
      });

      // ---- Animação ao aparecer + números a contar
      var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      function countUp(el) {
        var to = parseInt(el.getAttribute("data-to"), 10), t0 = null, dur = 1400;
        if (reduce) { el.textContent = to; return; }
        function step(ts) {
          if (!t0) t0 = ts;
          var p = Math.min((ts - t0) / dur, 1);
          el.textContent = Math.round(to * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(step);
        }
        el.textContent = "0";
        requestAnimationFrame(step);
      }
      if ("IntersectionObserver" in window) {
        var io = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) {
            if (!en.isIntersecting) return;
            if (en.target.classList.contains("count")) countUp(en.target);
            else en.target.classList.add("in");
            io.unobserve(en.target);
          });
        }, { threshold: 0.15 });
        document.querySelectorAll(".reveal, .count").forEach(function (el) { io.observe(el); });
      } else {
        document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("in"); });
      }

      // ---- Carrossel
      var track = document.getElementById("track");
      document.querySelectorAll(".arrow").forEach(function (b) {
        b.addEventListener("click", function () {
          var w = track.clientWidth, dir = parseInt(b.getAttribute("data-dir"), 10);
          var max = track.scrollWidth - w;
          var next = track.scrollLeft + dir * w;
          if (next > max + 5) next = 0;
          if (next < -5) next = max;
          track.scrollTo({ left: next, behavior: reduce ? "auto" : "smooth" });
        });
      });

      // ---- Separadores das tipologias
      function showType(code) {
        document.querySelectorAll(".tab").forEach(function (x) {
          x.setAttribute("aria-selected", x.getAttribute("data-t") === code ? "true" : "false");
        });
        document.querySelectorAll(".panel").forEach(function (p) { p.classList.toggle("on", p.id === "pn-" + code); });
      }
      document.querySelectorAll(".tab").forEach(function (b) {
        b.addEventListener("click", function () { showType(b.getAttribute("data-t")); });
      });

      // ---- Galeria e plantas em ecrã inteiro
      var lb = document.getElementById("lightbox"), lbImg = lb.querySelector("img"), lbCap = lb.querySelector("figcaption");
      var lbItems = [], lbIdx = 0;
      function lbShow(i) {
        lbIdx = (i + lbItems.length) % lbItems.length;
        var it = lbItems[lbIdx];
        lbImg.src = it.getAttribute("data-full");
        lbImg.alt = it.getAttribute("data-cap");
        lbCap.textContent = it.getAttribute("data-cap");
      }
      function lbOpen(group, el) {
        lbItems = Array.prototype.slice.call(group);
        lbShow(lbItems.indexOf(el));
        if (lb.showModal) lb.showModal(); else lb.setAttribute("open", "");
      }
      document.querySelectorAll(".gi").forEach(function (g, i, all) { g.addEventListener("click", function () { lbOpen(all, g); }); });
      document.querySelectorAll(".panel").forEach(function (p) {
        var plans = p.querySelectorAll(".plan");
        plans.forEach(function (g) { g.addEventListener("click", function () { lbOpen(plans, g); }); });
      });
      lb.querySelectorAll(".lbnav").forEach(function (b) {
        b.addEventListener("click", function () { lbShow(lbIdx + parseInt(b.getAttribute("data-dir"), 10)); });
      });
      lb.querySelector(".lbclose").addEventListener("click", function () { lb.close(); });
      lb.addEventListener("click", function (ev) { if (ev.target === lb) lb.close(); });
      document.addEventListener("keydown", function (ev) {
        if (!lb.open) return;
        if (ev.key === "ArrowRight") lbShow(lbIdx + 1);
        if (ev.key === "ArrowLeft") lbShow(lbIdx - 1);
      });

      // ---- Formulário: referência por tipologia
      var REFS = { T0: "YR00041", T1: "YR00042", T2: "YR00043" };
      var type = document.getElementById("type"), ref = document.getElementById("ref");
      function setRef() { ref.value = REFS[type.value] || ""; }
      type.addEventListener("change", setRef);
      setRef();
      document.querySelectorAll("[data-pick]").forEach(function (a) {
        a.addEventListener("click", function () { type.value = a.getAttribute("data-pick"); setRef(); });
      });

      // ---- UTMs (Google Ads)
      var q = new URLSearchParams(location.search);
      ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"].forEach(function (k) {
        var el = document.getElementById(k);
        if (el && q.get(k)) el.value = q.get(k);
      });
      document.getElementById("campaign").value = q.get("utm_campaign") || "";

      // ---- Tipologia vinda do anúncio: ?type=T0, ?type=T1 ou ?type=T2
      var typeParam = (q.get("type") || "").toUpperCase();
      if (REFS[typeParam]) {
        type.value = typeParam;
        setRef();
        showType(typeParam);
      }

      // ---- Telefone: escolha do país (indicativo) e validação
      var phoneInput = document.getElementById("phone");
      var iti = window.intlTelInput(phoneInput, {
        initialCountry: "pt",
        countryOrder: ["pt", "es", "fr", "gb", "de", "br", "nl", "be", "ch", "it", "us"],
        countryNameLocale: "__LANG__",
        separateDialCode: true,
        strictMode: true,
        uiTranslations: __UI__,
      });
      var PHONE_MSG = "__PHONE_MSG__";
      phoneInput.addEventListener("input", function () { phoneInput.setCustomValidity(""); });
      phoneInput.addEventListener("countrychange", function () { phoneInput.setCustomValidity(""); });

      // ---- Email: só aceita emails com domínio válido (ex.: nome@exemplo.com)
      var emailInput = document.getElementById("email");
      var EMAIL_MSG = "__EMAIL_MSG__";
      emailInput.addEventListener("invalid", function () {
        if (emailInput.validity.typeMismatch || emailInput.validity.patternMismatch) emailInput.setCustomValidity(EMAIL_MSG);
      });
      emailInput.addEventListener("input", function () { emailInput.setCustomValidity(""); });

      // ---- Envio: Netlify Forms -> página de obrigado (conversão Google Ads).
      // O email para a Inmovilla é enviado pela função netlify/functions/submission-created.mjs.
      var THANKS_URL = "__THANKS__";
      var form = document.getElementById("lead"), btn = form.querySelector("button[type=submit]");
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (form.website && form.website.value) return; // armadilha de spam
        if (!iti.isValidNumber()) {
          phoneInput.setCustomValidity(PHONE_MSG);
          phoneInput.reportValidity();
          return;
        }
        btn.disabled = true;
        var data = new URLSearchParams(new FormData(form));
        data.set("phone", iti.getNumber()); // número completo com indicativo, ex: +351912345678
        fetch("/", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: data.toString() })
          .then(function (r) {
            if (!r.ok) throw new Error("HTTP " + r.status);
            location.href = THANKS_URL;
          })
          .catch(function () {
            btn.disabled = false;
            alert("__ERR__");
          });
      });
