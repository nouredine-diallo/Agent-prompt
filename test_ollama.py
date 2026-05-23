import time
import ollama

start = time.time()

res = ollama.chat(
    model="mistral:7b",
    messages=[{"role": "user", "content": "say hello"}]
)

print(res)
print("TIME:", time.time() - start)