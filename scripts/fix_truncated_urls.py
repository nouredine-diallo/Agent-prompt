infile = "../urls_from_pdf.txt"
outfile = "../urls_fixed.txt"
with open(infile,"r",encoding="utf-8") as f:
    lines = [l.rstrip() for l in f if l.strip()]
out=[]
i=0
while i < len(lines):
    u = lines[i]
    if u.endswith("-") and i+1 < len(lines):
        u = u[:-1] + lines[i+1].lstrip()
        i+=2
    else:
        i+=1
    out.append(u)
with open(outfile,"w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("Wrote", outfile)
