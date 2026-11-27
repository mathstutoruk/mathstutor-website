"""Generate register.html, login.html and account.html in the shared site shell.
Run from the repository root: python3 tools/build_account_pages.py
"""
import sys
sys.path.insert(0, "tools")
from build_pages import page

SCRIPT = '<script src="assets/account.js" defer></script>'

REGISTER = '''<main id="mainContent" class="acct">
  <div class="wrap acct-grid">
    <section class="acct-intro">
      <h1>Create your account</h1>
      <p>Students get their course's question packs in one place. Parents can link to their child's account and see the same packs.</p>
      <ul class="ticks" style="grid-template-columns:1fr">
        <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7"/></svg>Free to join</li>
        <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7"/></svg>Question packs and worked answers for your exam board</li>
        <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7"/></svg>Parents can follow along from their own login</li>
      </ul>
    </section>
    <div class="auth-card">
      <form id="registerForm" novalidate>
        <fieldset class="role-pick">
          <legend>I am a</legend>
          <label><input type="radio" name="role" value="student" checked><span>Student</span></label>
          <label><input type="radio" name="role" value="parent"><span>Parent</span></label>
        </fieldset>
        <div class="form-row">
          <div class="form-group"><label for="firstName">First name</label><input id="firstName" name="first_name" autocomplete="given-name" required></div>
          <div class="form-group"><label for="lastName">Last name</label><input id="lastName" name="last_name" autocomplete="family-name" required></div>
        </div>
        <div class="form-group"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required></div>
        <div class="form-group" data-for="student"><label for="course">Your course and exam board</label><select id="course" name="course" data-courses></select></div>
        <p class="hint" data-for="parent" hidden>After signing up, you'll link to your child using the code on their account page.</p>
        <div class="form-row">
          <div class="form-group"><label for="password">Password <span>(8+ characters)</span></label><input id="password" name="password" type="password" autocomplete="new-password" minlength="8" required></div>
          <div class="form-group"><label for="password2">Confirm password</label><input id="password2" name="password2" type="password" autocomplete="new-password" minlength="8" required></div>
        </div>
        <label class="check"><input type="checkbox" name="agree" required><span>I agree to my details being used to run this account.</span></label>
        <p id="registerMsg" class="msg" role="alert" hidden></p>
        <button type="submit" class="submit-btn">Create account</button>
        <p class="form-note">Already have an account? <a href="login.html">Log in</a></p>
      </form>
      <p id="registerDone" class="msg ok" role="status" hidden></p>
    </div>
  </div>
</main>'''

LOGIN = '''<main id="mainContent" class="acct">
  <div class="wrap acct-narrow">
    <div class="auth-card">
      <h1>Log in</h1>
      <p class="acct-sub">Welcome back. Log in to see your question packs.</p>
      <form id="loginForm">
        <div class="form-group"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required></div>
        <div class="form-group"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required></div>
        <p id="loginMsg" class="msg" role="alert" hidden></p>
        <button type="submit" class="submit-btn">Log in</button>
        <div class="auth-links"><button type="button" class="linkish" id="forgotBtn">Forgotten password?</button><a href="register.html">Create an account</a></div>
      </form>
      <form id="resetForm" hidden>
        <div class="form-group"><label for="newPassword">New password <span>(8+ characters)</span></label><input id="newPassword" name="new_password" type="password" autocomplete="new-password" minlength="8" required></div>
        <p id="resetMsg" class="msg" role="alert" hidden></p>
        <button type="submit" class="submit-btn">Save new password</button>
      </form>
    </div>
  </div>
</main>'''

ACCOUNT = '''<main id="mainContent" class="acct">
  <div class="wrap">
    <nav class="preview-switch" id="previewSwitch" aria-label="Preview as" hidden>
      <span>Preview as</span><a href="account.html?preview=student" data-role="student">Student</a><a href="account.html?preview=parent" data-role="parent">Parent</a>
    </nav>
    <div class="dash-head">
      <div><p class="role" id="roleLabel">My account</p><h1 id="hello">My account</h1></div>
      <button type="button" class="btn btn-line" id="logoutBtn">Log out</button>
    </div>
    <p id="loading" class="empty">Loading your account…</p>

    <div id="studentView" hidden>
      <div class="dash-grid">
        <section class="dash-card">
          <h2>My course</h2>
          <label for="myCourse" class="sr">Course and exam board</label>
          <select id="myCourse"></select>
          <p id="courseMsg" class="msg" role="status" hidden></p>
        </section>
        <section class="dash-card navy">
          <h2>Link a parent</h2>
          <p>Give this code to your parent so they can follow your progress from their account.</p>
          <p class="code" id="linkCode">------</p>
        </section>
        <section class="dash-card">
          <h2>Lessons</h2>
          <p>One-to-one or small online groups, matched to your exam board.</p>
          <a class="btn btn-gold" href="contact.html">Book lessons</a>
        </section>
      </div>
      <section class="dash-packs">
        <h2>My question packs</h2>
        <div id="myPacks"></div>
      </section>
    </div>

    <div id="parentView" hidden>
      <div class="dash-grid two">
        <section class="dash-card">
          <h2>My students</h2>
          <div id="children"></div>
        </section>
        <section class="dash-card navy">
          <h2>Link a student</h2>
          <p>Enter the 6-character code from your child's account page.</p>
          <form id="linkForm" class="inline-form">
            <label for="code" class="sr">Link code</label>
            <input id="code" name="code" maxlength="6" autocomplete="off" placeholder="e.g. K7Q2XM">
            <button class="btn btn-gold" type="submit">Link</button>
          </form>
          <p id="linkMsg" class="msg" role="status" hidden></p>
        </section>
      </div>
      <section class="dash-packs" id="childPacksWrap" hidden>
        <h2 id="childPacksTitle">Question packs</h2>
        <div id="childPacks"></div>
      </section>
    </div>
  </div>
</main>'''

for name, title, desc, main in [
    ("register.html", "Create an account | mathstutor.co.uk", "Create a free student or parent account to see question packs and worked answers for your exam board.", REGISTER),
    ("login.html", "Log in | mathstutor.co.uk", "Log in to your mathstutor.co.uk student or parent account.", LOGIN),
    ("account.html", "My account | mathstutor.co.uk", "Your mathstutor.co.uk account.", ACCOUNT),
]:
    meta = f'<title>{title}</title>\n<meta name="description" content="{desc}">'
    if name == "account.html":
        meta += '\n<meta name="robots" content="noindex">'
    html = page(meta, "login", main, SCRIPT).replace('<body class="page">', f'<body class="page" data-account="{name[:-5]}">')
    open(name, "w", encoding="utf-8").write(html)
    print("built", name)
