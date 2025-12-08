import os
import ast

text = ""
with open("output/MDRMN017.txt", "r") as f:
    text = f.read()
    f.close()

if text == "":
    print("No text found")
    exit()

l = ast.literal_eval(text)
for page in l:
    c = False
    for text in page:
        if text[3].lower().find("total targeted population") != -1:
            print(text[3])
            c = not(c)
            continue
        if c:
            print(text[3])

print("=========================================")
print("=========================================")

for page in l:
    c = False
    for i in range(len(page) - 2):
        og_text = page[i][3]
        text = " ".join(page[i + j][3] for j in range(3))
        text = text.replace("- ", "")
        text_gap = "".join(page[i + j][3] for j in range(3))
        text_gap = text_gap.replace("- ", "")

        if text.startswith("Community Engagement And Accountability") or text_gap.startswith("Community Engagement And Accountability"):
            c = True
        if text.startswith("Livelihoods And Basic Needs") or text_gap.startswith("Livelihoods And Basic Needs"):
            c = True
        if text.startswith("Multi-purpose Cash") or text_gap.startswith("Multi-purpose Cash"):
            c = True
        if text.startswith("Risk Reduction, Climate Adaptation And Recovery") or text_gap.startswith("Risk Reduction, Climate Adaption And Recovery"):
            c = True
        if text.startswith("National Society Strengthening"):
            c = True
        if "secretariat services" in og_text.lower():
            c = True
        if text.startswith("Health "):
            c = True
        if "narrative" in og_text.lower() or "description" in og_text.lower():
            c = False
            print("=========================================")
        if c:
            print(og_text)

