# SuperTET PRT Practice App (v2)

Chalkboard-and-notebook styled exam practice: subject-wise MCQs, mixed quizzes, revision of
mistakes, and timed mock tests, with a progress dashboard for every student.

## Run

    pip install -r requirements.txt
    streamlit run app.py

## What students get
- **Your name** (sidebar): scores, streak, saved questions and mistakes are kept per student.
  Leave it empty to use the shared "Guest" profile (this is where your old results.csv lives).
- **Home**: streak, daily goal, accuracy and a "Where you stand" chart by subject, with a one-tap
  "Focus on <weakest subject>" button.
- **Practice**: by subject, or a **Mixed quiz** from any subjects you pick. Tap an option and it is checked
  instantly; a correct answer moves on to the next question automatically (switch this off with the checkbox).
  A wrong answer stays on screen with the explanation. Tap 🔖 Save on any question.
- **Notes**: concept notes uploaded by the teacher. Filter by subject, search, read the PDF in the app or
  download it. Short typed notes are supported too.
- **Revision**: your saved questions and **My mistakes** (wrong answers stay here until you get them right).
- **Test Series**: timer, question palette, mark-for-review, result with time taken and a comparison
  with your last attempt, plus a Wrong / Correct / Skipped review filter.

## Admin
Password: `.streamlit/secrets.toml` (default `admin123` - change it).
- Add one question, bulk upload CSV/JSON (duplicates are skipped), edit/delete/search questions.
- **Notes** tab: upload a PDF (or type a short Markdown note) for any subject, and delete old ones.
- **Students** tab: every student's tests, average score, accuracy and streak, plus a full ZIP backup.

## Your data
Everything lives in `data/` (questions, `results.csv`, `students/<name>/...`).
Copy your existing `data/` folder over before first run. Demo content is in `sample_data/`
(Home -> "Load demo questions" when the app is empty).

Note: names are not passwords. Anyone who types the same name sees that profile, which is fine for a
class or study group but is not private accounts.

## Deploying (important)
Upload the **hidden** `.streamlit` folder too (GitHub's web uploader and some zip tools skip folders
starting with a dot). The app now stays readable even without it - colours are forced to the light
chalkboard look in `app.py` - but `.streamlit/secrets.toml` holds your admin password, so it is still needed.
On Streamlit Community Cloud, put the admin password in the app's **Secrets** settings instead.
