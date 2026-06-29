# Website Setup Guide — Mark Kimuyu Research

This is your complete site: a one-page website with a contact form that
emails submissions straight to your Gmail inbox.

**Files:**
- `index.html` — the website itself
- `server.py` — the backend that serves the site and sends form emails
- `requirements.txt` — Python dependencies

---

## Part 1 — Create a Gmail App Password

Gmail won't let regular passwords be used by apps like this one — you need
a special 16-character "App Password."

1. Go to **myaccount.google.com/security**
2. Under "How you sign in to Google," make sure **2-Step Verification** is
   turned on (App Passwords require it). If it's off, turn it on first —
   you'll need your phone.
3. Once 2-Step Verification is on, search for **"App Passwords"** in the
   Google Account search bar (or go directly to
   **myaccount.google.com/apppasswords**).
4. Create a new app password — name it something like "website".
5. Google will show you a 16-character password (e.g. `abcd efgh ijkl mnop`).
   **Copy it now** — you won't be able to see it again. Remove the spaces
   when you use it.

This app password is what the website uses to send emails — it's separate
from your real Gmail password and can be revoked anytime without affecting
your account.

---

## Part 2 — Run it locally to test

1. Put `index.html`, `server.py`, and `requirements.txt` in the same folder.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your environment variables (replace the app password with the one
   you just copied):

   ```bash
   export GMAIL_ADDRESS="markkimuyu2@gmail.com"
   export GMAIL_APP_PASSWORD="abcdefghijklmnop"
   export NOTIFY_EMAIL="markkimuyu2@gmail.com"
   ```

   (On Windows PowerShell, use `$env:GMAIL_ADDRESS="..."` etc.)

4. Run the server:
   ```bash
   python server.py
   ```

5. Open **http://localhost:5000** in your browser. You should see the full
   site. Fill out the contact form and submit it — check your Gmail inbox,
   the message should arrive within a few seconds, with the client's email
   set as "Reply-To" so you can just hit reply.

---

## Part 3 — Deploy it permanently (so it's live on the internet)

Once it works locally, put it online with **Render.com** (free tier is
fine for a personal site):

1. Create a free GitHub account if you don't have one, and create a new
   repository (e.g. "my-website"). Upload `index.html`, `server.py`, and
   `requirements.txt` to it.

2. Go to **render.com**, sign up, and click **New → Web Service**.

3. Connect your GitHub repo.

4. Configure:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn server:app`

5. Under **Environment**, add these environment variables:
   - `GMAIL_ADDRESS` = `markkimuyu2@gmail.com`
   - `GMAIL_APP_PASSWORD` = (your 16-character app password, no spaces)
   - `NOTIFY_EMAIL` = `markkimuyu2@gmail.com`

6. Click **Deploy**. Render will give you a live URL like
   `https://mark-kimuyu-research.onrender.com` — that's your website,
   live on the internet, working contact form included.

7. (Optional) If you buy a custom domain later (e.g. `markkimuyu.com`),
   Render lets you connect it under **Settings → Custom Domain**.

---

## Notes

- **Rate limiting**: the contact form allows max 5 submissions per visitor
  per hour, to prevent spam/abuse. This resets automatically.
- **Spam**: if the site starts attracting spam submissions once it's
  public, the easiest next step is adding a CAPTCHA (e.g. Google
  reCAPTCHA) — let me know if you want that added later.
- **Editing content**: all the text (services, project examples, etc.) is
  in `index.html` — search for the text you want to change and edit it
  directly, no build step needed.
- **Free tier sleep**: Render's free tier "sleeps" the server after 15
  minutes of no traffic, so the very first visitor after a quiet period
  may wait ~30 seconds for it to wake up. This is normal for the free
  tier; upgrading removes it if it becomes a problem.

---

## Troubleshooting

| Problem | Likely cause |
|---|---|
| Form says "could not reach server" | Server isn't running, or wrong URL |
| Form says "could not send your message" | Wrong Gmail address/app password, or 2-Step Verification not enabled |
| Emails not arriving | Check spam folder; confirm `NOTIFY_EMAIL` is correct |
| Site loads but looks unstyled | Check your internet connection — fonts load from Google Fonts |

If anything throws an error, paste it here and I'll help you fix it.
