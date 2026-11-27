# Switching on student and parent accounts

The Register, Log in and My account pages run in **preview mode** until these steps are done.

1. Create a free account at supabase.com and a new project. Choose **London** as the region.
2. In the project, open **SQL Editor**, paste the whole of `docs/supabase-setup.sql` and run it.
3. In **Authentication > URL Configuration**, set the Site URL to `https://mathstutor.co.uk` and add
   `https://mathstutor.co.uk/account.html` and `https://mathstutor.co.uk/login.html` as redirect URLs.
4. In **Project Settings > API**, copy the **Project URL** and the **anon public** key into
   `assets/account.js` (`SUPABASE_URL` and `SUPABASE_ANON_KEY`). Never use the service role key here.
5. Update the privacy policy to cover accounts before inviting families.

What is stored: name, email, account type, chosen course, and which students a parent has linked.
Passwords are handled by Supabase and never stored in this website.
