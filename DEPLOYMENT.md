# GitHub Deployment and Maintenance

This project is a static personal blog. GitHub Pages can serve it directly after the static post index and RSS files are rebuilt.

## First-time GitHub Setup

1. Create a new GitHub repository.
2. In this folder, initialize Git and connect the remote:

```bash
git init
git branch -M main
git remote add origin https://github.com/<your-name>/<repo-name>.git
```

3. Update `site.config.json` so `url` matches the GitHub Pages URL:

```json
{
  "url": "https://<your-name>.github.io/<repo-name>/"
}
```

4. Commit and push:

```bash
python3 scripts/build_posts_index.py
git add index.html README.md DEPLOYMENT.md site.config.json feed.xml posts assets scripts .github .gitignore
git commit -m "Initial GitHub Pages deployment"
git push -u origin main
```

5. In GitHub, open **Settings → Pages** and set the source to **GitHub Actions**.

## Daily Maintenance Flow

Before publishing a preview version:

```bash
python3 scripts/build_posts_index.py
python3 -m http.server 8766
```

Check the site locally:

```text
http://localhost:8766/index.html
```

Then commit only real source/content changes:

```bash
git status --short
git add index.html site.config.json feed.xml posts assets scripts README.md DEPLOYMENT.md .github .gitignore
git commit -m "Describe the change"
git push
```

## What Should Not Be Committed

Do not commit local test leftovers:

- `test-artifacts/`
- `test-results/`
- browser screenshots from temporary verification
- Python cache folders
- local `.env` files

The `.gitignore` file already excludes these.

## Static Content Checklist

When adding Markdown posts manually:

1. Add or edit files under `posts/`.
2. Put images and videos under `assets/`.
3. Run `python3 scripts/build_posts_index.py`.
4. Preview locally.
5. Commit and push.

The GitHub Actions workflow also rebuilds the post index during deployment, but running it locally first catches problems earlier.
