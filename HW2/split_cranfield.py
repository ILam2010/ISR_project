import os

input_file = "C:/Users/User/Information-Retrieval/cran.all.1400"
output_dir = "collection/"

os.makedirs(output_dir, exist_ok=True)

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

docs = content.split(".I ")

for doc in docs[1:]:
    lines = doc.splitlines()
    doc_id = lines[0].strip()

    text = "\n".join(lines)

    with open(f"{output_dir}/{doc_id}.txt", "w", encoding="utf-8") as out:
        out.write(text)

print("Done splitting Cranfield collection!")
