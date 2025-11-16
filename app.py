import gradio as gr
import requests
from openai import OpenAI

# ========= 🔑 SET YOUR KEY HERE OR HF SECRET ========= #
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")   # <-- Use HF secret
client = OpenAI(api_key=OPENAI_API_KEY)

# ===================================================== #
# 🧠 GPT RULE CHECKER
# ===================================================== #
def gpt_check_rule(rule, chart):
    prompt = f"""
You are a clinical trial eligibility checker.
Rule:
{rule}
Patient chart:
{chart}
Return JSON ONLY:
{{
 "status": "met" | "not_met" | "not_applicable",
 "evidence": "short quote from chart or empty"
}}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    try:
        return eval(response.choices[0].message.content)
    except:
        return {"status": "not_applicable", "evidence": ""}


# ===================================================== #
# 📡 TRIAL FETCHER
# ===================================================== #
def fetch_trials(condition, limit=5):

    url = f"https://clinicaltrials.gov/api/v2/studies?query.cond={condition}&filter.overallStatus=RECRUITING&fields=NCTId,BriefTitle,EligibilityCriteria&limit={limit}"
    r = requests.get(url)

    if r.status_code != 200:
        return []

    studies = r.json().get("studies", [])
    trials = []

    for s in studies:
        trials.append({
            "id": s["protocolSection"]["identificationModule"]["nctId"],
            "title": s["protocolSection"]["identificationModule"]["briefTitle"],
            "criteria": s["protocolSection"]["eligibilityModule"]["eligibilityCriteria"]
        })
    return trials



# ===================================================== #
# 🧠 GPT STRUCTURED EXTRACTION
# ===================================================== #
def extract_rules(raw_text):
    prompt = f"""
Convert the eligibility text into JSON:
{{
 "Inclusion": [...],
 "Exclusion": [...]
}}
TEXT:
{raw_text}
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # safest extraction method:
    text = resp.choices[0].message.content
    start = text.find("{")
    end = text.rfind("}") + 1
    return eval(text[start:end])


# ===================================================== #
# 🧬 MAIN MATCH ENGINE
# ===================================================== #
def match_engine(chart, condition, limit):

    trials = fetch_trials(condition, limit)
    if not trials:
        return "❗ No trials found"

    final_report = f"# 🧬 TrialMatch.AI Report\n\n### Condition searched: **{condition}**\n\n"

    for t in trials:

        final_report += f"\n\n---\n## 🔗 {t['title']}  \n**NCT:** {t['id']}\n"
        final_report += f"[View Trial](https://clinicaltrials.gov/study/{t['id']})\n\n"

        rules = extract_rules(t["criteria"])
        inc = rules["Inclusion"]
        exc = rules["Exclusion"]

        eligible = True
        evidence_log = ""

        for r in inc:
            check = gpt_check_rule(r, chart)
            evidence_log += f"**INC:** {r} → `{check['status']}`\n"
            if check["status"] == "not_met":
                eligible = False

        for r in exc:
            check = gpt_check_rule(r, chart)
            evidence_log += f"**EXC:** {r} → `{check['status']}`\n"
            if check["status"] == "met":
                eligible = False

        final_report += f"### RESULT: {'🟢 Eligible' if eligible else '🔴 Not Eligible'}\n\n"
        final_report += evidence_log

    return final_report


# ===================================================== #
# 🎨 GRADIO UI
# ===================================================== #
with gr.Blocks(title="TrialMatch.AI") as demo:
    gr.Markdown("# 🧬 TrialMatch.AI\nPaste a chart → Get eligible trials with rule reasoning.")

    chart = gr.Textbox(lines=15, label="Patient Chart")
    cond = gr.Textbox(label="Condition Search (e.g. EGFR Lung Cancer)")
    limit = gr.Slider(1, 10, value=3, step=1, label="Max Trials")

    run = gr.Button("Run Trial Matching")

    out = gr.Markdown()

    run.click(fn=match_engine, inputs=[chart, cond, limit], outputs=out)

demo.launch()
