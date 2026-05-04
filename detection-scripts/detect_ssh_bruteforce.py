from collections import Counter

THRESHOLD = 50
sources = Counter()

with open("conn.log", "r") as file:
    fields = []

    for line in file:
        if line.startswith("#fields"):
            fields = line.strip().split("\t")[1:]
            continue

        if line.startswith("#"):
            continue

        values = line.strip().split("\t")
        row = dict(zip(fields, values))

        src = row.get("id.orig_h")
        dst = row.get("id.resp_h")
        port = row.get("id.resp_p")
        service = row.get("service")

        if port == "22" or service == "ssh":
            sources[(src, dst)] += 1

for (src, dst), count in sources.items():
    if count >= THRESHOLD:
        print(f"[ALERT] Possible SSH brute force: {src} -> {dst} | Connections: {count}")

