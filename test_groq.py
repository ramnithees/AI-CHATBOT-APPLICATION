from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

models = client.models.list()

print("=" * 60)
print("MODELS AVAILABLE TO YOUR GROQ API KEY")
print("=" * 60)

for model in models.data:
    print(model.id)