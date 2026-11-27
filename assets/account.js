/* mathstutor.co.uk accounts: register, log in, dashboard.
 *
 * Until SUPABASE_URL and SUPABASE_ANON_KEY are filled in, the pages run in
 * preview mode with sample data and nothing is stored anywhere.
 * See docs/accounts-setup.md for how to switch real accounts on.
 */
window.MT_CONFIG = window.MT_CONFIG || {
  SUPABASE_URL: "",       // e.g. https://abcd1234.supabase.co
  SUPABASE_ANON_KEY: "",  // the "anon public" key, never the service role key
};

(() => {
  const cfg = window.MT_CONFIG;
  const LIVE = Boolean(cfg.SUPABASE_URL && cfg.SUPABASE_ANON_KEY);
  const $ = sel => document.querySelector(sel);
  const page = document.body.dataset.account;

  const COURSES = [
    ["GCSE Maths", [["edexcel-gcse-maths-question-packs", "Edexcel (1MA1)"], ["aqa-gcse-maths-question-packs", "AQA (8300)"], ["ocr-gcse-maths-question-packs", "OCR (J560)"]]],
    ["GCSE Further Maths", [["aqa-level-2-further-maths-question-packs", "AQA Level 2 Further Maths (8365)"], ["edexcel-level-2-extended-maths-question-packs", "Edexcel Level 2 Extended Maths (7M20)"], ["ocr-additional-maths-question-packs", "OCR Additional Maths (6993)"]]],
    ["A-level Maths", [["edexcel-a-level-maths-question-packs", "Edexcel (9MA0)"], ["aqa-a-level-maths-question-packs", "AQA (7357)"], ["ocr-a-level-maths-question-packs", "OCR A (H240)"], ["ocr-mei-a-level-maths-question-packs", "OCR B MEI (H640)"]]],
    ["A-level Further Maths", [["edexcel-a-level-further-maths-question-packs", "Edexcel (9FM0)"], ["aqa-a-level-further-maths-question-packs", "AQA (7367)"], ["ocr-a-level-further-maths-question-packs", "OCR A (H245)"], ["ocr-mei-a-level-further-maths-question-packs", "OCR B MEI (H645)"]]],
    ["IB Maths", [["ib-aa-sl-question-packs", "Analysis and Approaches SL"], ["ib-aa-hl-question-packs", "Analysis and Approaches HL"]]],
  ];
  const courseName = key => {
    for (const [group, list] of COURSES) for (const [k, label] of list) if (k === key) return `${group}: ${label}`;
    return "No course chosen";
  };
  const courseOptions = selected => COURSES.map(([group, list]) =>
    `<optgroup label="${group}">${list.map(([k, label]) => `<option value="${k}"${k === selected ? " selected" : ""}>${group}, ${label}</option>`).join("")}</optgroup>`
  ).join("");
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const say = (el, text, kind = "info") => { el.className = "msg " + kind; el.textContent = text; el.hidden = !text; };

  // Fill every course <select> on the page.
  document.querySelectorAll("select[data-courses]").forEach(s => { s.innerHTML = '<option value="">Choose a course</option>' + courseOptions(""); });

  // Preview banner
  if (!LIVE) {
    const b = document.createElement("div");
    b.className = "demo-banner";
    b.textContent = new URLSearchParams(location.search).has("preview")
      ? "Preview with sample data. Nothing here is saved."
      : "Student and parent accounts are opening soon. Get in touch and I'll let you know when they're ready.";
    document.querySelector("main")?.prepend(b);
  }

  let sb = null;
  const ready = new Promise(resolve => {
    if (!LIVE) return resolve();
    const s = document.createElement("script");
    s.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.min.js";
    s.onload = () => { sb = window.supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_ANON_KEY); resolve(); };
    s.onerror = () => resolve();
    document.head.appendChild(s);
  });

  /* ---------- Register ---------- */
  if (page === "register") {
    const form = $("#registerForm"), msg = $("#registerMsg");
    const syncRole = () => {
      const role = form.role.value;
      form.querySelectorAll("[data-for]").forEach(el => { el.hidden = el.dataset.for !== role; });
      form.course.required = role === "student";
    };
    form.querySelectorAll('input[name="role"]').forEach(r => r.addEventListener("change", syncRole));
    syncRole();
    form.addEventListener("submit", async e => {
      e.preventDefault();
      if (form.password.value.length < 8) return say(msg, "Use at least 8 characters for your password.", "error");
      if (form.password.value !== form.password2.value) return say(msg, "The two passwords don't match.", "error");
      const role = form.role.value;
      if (!LIVE) return say(msg, "Accounts are opening soon, so nothing has been saved yet. Use the contact form and I'll let you know as soon as they're ready.", "info");
      await ready;
      if (!sb) return say(msg, "Couldn't reach the account service. Check your connection and try again.", "error");
      form.querySelector("button[type=submit]").disabled = true;
      const { error } = await sb.auth.signUp({
        email: form.email.value.trim(),
        password: form.password.value,
        options: {
          emailRedirectTo: new URL("account.html", location.href).href,
          data: { role, first_name: form.first_name.value.trim(), last_name: form.last_name.value.trim(), course: role === "student" ? form.course.value : null },
        },
      });
      form.querySelector("button[type=submit]").disabled = false;
      if (error) return say(msg, error.message, "error");
      form.hidden = true;
      say($("#registerDone"), `Account created. We've sent a confirmation link to ${form.email.value.trim()}. Open it to finish signing up.`, "ok");
    });
  }

  /* ---------- Log in ---------- */
  if (page === "login") {
    const form = $("#loginForm"), msg = $("#loginMsg"), resetForm = $("#resetForm");
    form.addEventListener("submit", async e => {
      e.preventDefault();
      if (!LIVE) return say(msg, "Accounts are opening soon, so there's nothing to log in to yet.", "info");
      await ready;
      if (!sb) return say(msg, "Couldn't reach the account service. Check your connection and try again.", "error");
      const { error } = await sb.auth.signInWithPassword({ email: form.email.value.trim(), password: form.password.value });
      if (error) return say(msg, "That email and password don't match an account. Check them, or reset your password.", "error");
      location.href = "account.html";
    });
    $("#forgotBtn").addEventListener("click", async () => {
      const email = form.email.value.trim();
      if (!email) return say(msg, "Type your email address above first, then choose Forgotten password.", "error");
      if (!LIVE) return say(msg, "In the live site, this sends a password reset link to your email.", "info");
      await ready;
      const { error } = await sb.auth.resetPasswordForEmail(email, { redirectTo: new URL("login.html", location.href).href });
      say(msg, error ? error.message : `If ${email} has an account, a reset link is on its way.`, error ? "error" : "ok");
    });
    // Arriving from a reset email: show the new-password form.
    ready.then(() => {
      if (!sb) return;
      sb.auth.onAuthStateChange(event => {
        if (event === "PASSWORD_RECOVERY") { form.hidden = true; resetForm.hidden = false; }
      });
    });
    resetForm.addEventListener("submit", async e => {
      e.preventDefault();
      const pw = resetForm.new_password.value;
      if (pw.length < 8) return say($("#resetMsg"), "Use at least 8 characters.", "error");
      const { error } = await sb.auth.updateUser({ password: pw });
      if (error) return say($("#resetMsg"), error.message, "error");
      location.href = "account.html";
    });
  }

  /* ---------- Account dashboard ---------- */
  if (page === "account") {
    let packs = null;
    const loadPacks = async () => packs || (packs = await fetch("assets/packs.json").then(r => r.json()));

    const renderPacks = async (key, target) => {
      const box = $(target);
      if (!key) { box.innerHTML = '<p class="empty">Choose your course above to see its question packs.</p>'; return; }
      const data = (await loadPacks())[key];
      if (!data) { box.innerHTML = '<p class="empty">No question packs found for this course.</p>'; return; }
      const count = data.sections.reduce((n, s) => n + s.topics.length, 0);
      box.innerHTML = `<div class="pack-tools"><p><b>${count} topic packs</b> for ${esc(data.title)}</p>
        <label class="search"><span class="sr">Search topics</span><input type="search" placeholder="Search topics" data-filter></label></div>` +
        data.sections.map(s => `<details class="pack-group" open><summary>${esc(s.h)} <span>${s.topics.length}</span></summary><ul>` +
          s.topics.map(t => `<li data-topic="${esc(t.t.toLowerCase())}"><span>${esc(t.t)}</span><span class="dl">` +
            (t.q ? `<a href="${esc(t.q)}" target="_blank" rel="noopener">Questions</a>` : "") +
            (t.a ? `<a href="${esc(t.a)}" target="_blank" rel="noopener">Answers</a>` : "") + `</span></li>`).join("") +
          `</ul></details>`).join("");
      box.querySelector("[data-filter]").addEventListener("input", e => {
        const q = e.target.value.trim().toLowerCase();
        box.querySelectorAll("li[data-topic]").forEach(li => { li.hidden = q && !li.dataset.topic.includes(q); });
        box.querySelectorAll(".pack-group").forEach(g => { g.hidden = q && !g.querySelector("li:not([hidden])"); });
      });
    };

    const showStudent = async profile => {
      $("#studentView").hidden = false;
      $("#hello").textContent = `Hi ${profile.first_name || "there"}`;
      $("#roleLabel").textContent = "Student account";
      const sel = $("#myCourse");
      sel.innerHTML = '<option value="">Choose a course</option>' + courseOptions(profile.course);
      $("#linkCode").textContent = profile.link_code || "------";
      sel.addEventListener("change", async () => {
        if (LIVE) {
          const { error } = await sb.from("profiles").update({ course: sel.value || null }).eq("id", profile.id);
          if (error) return say($("#courseMsg"), "Couldn't save your course. Try again.", "error");
        }
        say($("#courseMsg"), "Course saved.", "ok");
        renderPacks(sel.value, "#myPacks");
      });
      renderPacks(profile.course, "#myPacks");
    };

    const showParent = async (profile, children) => {
      $("#parentView").hidden = false;
      $("#hello").textContent = `Hi ${profile.first_name || "there"}`;
      $("#roleLabel").textContent = "Parent account";
      const list = $("#children");
      list.innerHTML = children.length ? children.map((c, i) => `<article class="child">
          <div><h3>${esc(c.first_name)} ${esc(c.last_name)}</h3><p>${esc(courseName(c.course))}</p></div>
          <button type="button" class="btn btn-line" data-child="${i}">See their question packs</button></article>`).join("")
        : '<p class="empty">No students linked yet. Ask your child for the link code on their account page, then enter it below.</p>';
      list.querySelectorAll("[data-child]").forEach(b => b.addEventListener("click", () => {
        const c = children[+b.dataset.child];
        $("#childPacksTitle").textContent = `${c.first_name}'s question packs`;
        $("#childPacksWrap").hidden = false;
        renderPacks(c.course, "#childPacks");
        $("#childPacksWrap").scrollIntoView({ behavior: "smooth", block: "start" });
      }));
      $("#linkForm").addEventListener("submit", async e => {
        e.preventDefault();
        const code = e.target.code.value.trim().toUpperCase();
        if (!/^[A-Z0-9]{6}$/.test(code)) return say($("#linkMsg"), "Link codes are 6 letters and numbers.", "error");
        if (!LIVE) return say($("#linkMsg"), "In the live site, this links your child's account to yours.", "info");
        const { error } = await sb.rpc("link_child", { code });
        if (error) return say($("#linkMsg"), "That code didn't match a student account. Check it and try again.", "error");
        location.reload();
      });
    };

    $("#logoutBtn").addEventListener("click", async () => {
      if (LIVE && sb) await sb.auth.signOut();
      location.href = "login.html";
    });

    (async () => {
      if (!LIVE) {
        const params = new URLSearchParams(location.search);
        if (!params.has("preview")) { location.replace("login.html"); return; }
        $("#loading").hidden = true;
        const role = params.get("preview") === "parent" ? "parent" : "student";
        const sw = $("#previewSwitch"); sw.hidden = false;
        sw.querySelector(`[data-role="${role}"]`).setAttribute("aria-current", "page");
        if (role === "parent") {
          showParent({ first_name: "Sam" }, [
            { first_name: "Aisha", last_name: "(sample)", course: "edexcel-a-level-maths-question-packs" },
            { first_name: "Leo", last_name: "(sample)", course: "aqa-gcse-maths-question-packs" },
          ]);
        } else {
          showStudent({ first_name: "Aisha", course: "edexcel-a-level-maths-question-packs", link_code: "K7Q2XM" });
        }
        return;
      }
      await ready;
      if (!sb) { $("#loading").textContent = "Couldn't reach the account service. Refresh to try again."; return; }
      const { data: { session } } = await sb.auth.getSession();
      if (!session) { location.href = "login.html"; return; }
      const { data: profile, error } = await sb.from("profiles").select("*").eq("id", session.user.id).single();
      $("#loading").hidden = true;
      if (error || !profile) { $("#loading").hidden = false; $("#loading").textContent = "Your account is still being set up. Refresh in a moment."; return; }
      if (profile.role === "parent") {
        const { data: children } = await sb.rpc("my_children");
        showParent(profile, children || []);
      } else {
        showStudent(profile);
      }
    })();
  }
})();
