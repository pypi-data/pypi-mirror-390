# Wiki Content for GitHub

This directory contains the markdown files for the GitHub Wiki.

## How to Upload to GitHub Wiki

### Option 1: Via Web Interface (Easiest)

1. Go to your repository: https://github.com/thecheapgeek/python-lite-camera
2. Click the **"Wiki"** tab
3. Click **"Create the first page"** (or "New Page" if wiki exists)
4. For each markdown file in this directory:
   - Copy the filename without `.md` (e.g., `Getting-Started`)
   - Paste the page name in GitHub Wiki
   - Copy the file contents
   - Paste into the GitHub Wiki editor
   - Click "Save Page"

### Option 2: Clone Wiki Git Repository (Advanced)

GitHub Wikis are actually Git repositories!

```bash
# Clone the wiki repository (replace with your repo URL)
git clone https://github.com/thecheapgeek/python-lite-camera.wiki.git

# Copy all wiki files
cp wiki/*.md python-lite-camera.wiki/

# Commit and push
cd python-lite-camera.wiki
git add .
git commit -m "Add initial wiki pages"
git push origin master
```

## Wiki Pages to Upload

Upload these files in order:

1. **Home.md** - Main landing page (name it "Home")
2. **_Sidebar.md** - Navigation sidebar (name it "_Sidebar")
3. **Getting-Started.md** - Getting started guide
4. **API-Reference.md** - API documentation
5. **Troubleshooting.md** - Troubleshooting guide
6. **Examples.md** - Code examples
7. **Camera-Compatibility.md** - Camera compatibility list
8. **Contributing.md** - Contributing guide

**Important:** Don't upload this README.md to the wiki!

## Page Names

When creating pages in GitHub Wiki, use these exact names:

- `Home` (not "Home.md")
- `_Sidebar` (enables sidebar navigation)
- `Getting-Started`
- `API-Reference`
- `Troubleshooting`
- `Examples`
- `Camera-Compatibility`
- `Contributing`

## After Upload

1. Verify all internal links work
2. Check that the sidebar appears on all pages
3. Test navigation between pages
4. Share the wiki URL: https://github.com/thecheapgeek/python-lite-camera/wiki

## Editing the Wiki

To make changes after upload:

**Web Interface:**
- Click "Edit" on any wiki page
- Make changes
- Save

**Git Repository:**
```bash
# Make changes to files
git add .
git commit -m "Update documentation"
git push
```

## Deleting This Directory

After uploading to GitHub Wiki, you can safely delete this `wiki/` directory from your main repository if you want. The wiki content will live in the separate wiki repository.

Or keep it as a backup/staging area for wiki changes.
