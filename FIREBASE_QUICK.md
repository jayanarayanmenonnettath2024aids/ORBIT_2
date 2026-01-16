# Quick: Convert Firebase JSON to Environment Variable

## Windows (PowerShell)
```powershell
cd C:\Users\JAYAN\Downloads\orbit\backend
(Get-Content firebase-credentials.json -Raw) -replace '\r?\n', '' | Set-Clipboard
```

Now paste in Render/Vercel as `FIREBASE_CREDENTIALS_JSON`

## Mac/Linux
```bash
cat firebase-credentials.json | tr -d '\n' | pbcopy
```

## Or Use Render Secret Files (Easier!)
1. Render Dashboard → Your Service → Environment
2. Secret Files → Add Secret File
3. Filename: `firebase-credentials.json`
4. Contents: Paste your JSON file content
5. Save

Done! ✅
