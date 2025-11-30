# How to Upload to GitHub

Since you don't have the GitHub CLI (`gh`) installed, here are the manual steps to upload your project.

## 1. Initialize Git locally
Run these commands in your terminal (I can run the first 3 for you if you want, but you need to do the GitHub part):

```bash
git init
git add .
git commit -m "Initial commit: Amazon and Walmart warehouse analysis"
```

## 2. Create a Repository on GitHub
1.  Go to [github.com/new](https://github.com/new).
2.  Repository name: `warehouse-location-analysis` (or whatever you prefer).
3.  Description: "Geocoding and analysis of Amazon and Walmart warehouses".
4.  Public/Private: Your choice.
5.  **Do not** initialize with README, .gitignore, or License (we already have local files).
6.  Click **Create repository**.

## 3. Connect and Push
Once created, GitHub will show you a page with commands. Look for the section **"…or push an existing repository from the command line"**. It will look like this:

```bash
git remote add origin https://github.com/YOUR_USERNAME/warehouse-location-analysis.git
git branch -M main
git push -u origin main
```

Copy and run those commands in your terminal.
