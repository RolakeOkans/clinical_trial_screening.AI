---
title: TrialMatch.AI
emoji: 🧬
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
---

# TrialMatch.AI

Paste a patient chart → Instantly see eligible clinical trials.

Runs live with:
- GPT-4o-mini clinical reasoning
- Real-time ClinicalTrials.gov lookup
- Evidence-grounded rule matching

# How to Test the App
Open the sample patient chart PDF

Copy the full chart text and paste it into the Patient Chart box

In the same PDF, you will see a line labeled “Condition Search:”
→ Copy that text (example: “EGFR lung cancer”)

Paste it into the Condition Search field in the app

Click “Run Trial Matching”

The system will show which real clinical trials the patient is eligible or not eligible for, with rule-by-rule reasoning
