
# MyHeartRisk NADI Training Completion Assessment

This is a Streamlit web app for:
- MyHeartRisk NADI Train-the-Trainer completion
- 10 dummy case scenario practice
- Knowledge check
- Google Form completion declaration
- Certificate of Completion generation

## Files

```text
streamlit_app/
├── app.py
├── requirements.txt
└── README.md
```

## Run locally in VS Code

Open terminal in the folder and run:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

If `py` does not work, use:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Update Google Form link

In `app.py`, replace:

```python
GOOGLE_FORM_URL = "https://forms.gle/PASTE_YOUR_GOOGLE_FORM_LINK_HERE"
```

with your real Google Form link.

## Publish later

For Streamlit Community Cloud, upload:
- `app.py`
- `requirements.txt`
- `README.md`

Then set the main file as:

```text
app.py
```

## Certificate

The app generates:
- HTML certificate
- PDF certificate if `fpdf2` is installed

## Certificate logo and signature fix
This fixed version includes an `assets/` folder with:
- `uitm_care_logo.png`
- `myheartrisk_icon.png`
- `signature_sazzli.png`
- `myheartrisk_gold_seal.png`

Do not delete the `assets/` folder. The certificate preview and PDF generator load the logo and signature from this folder.
