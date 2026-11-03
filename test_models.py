from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv('.env')
c = Groq(api_key=os.environ['GROQ_API_KEY'])
for m in ['llama-3.1-8b-instant', 'llama-3.2-3b-preview', 'mixtral-8x7b-32768', 'gemma2-9b-it', 'llama-3.1-70b-versatile']:
    try:
        r = c.chat.completions.create(model=m, messages=[{'role':'user','content':'hi'}], max_tokens=2)
        print('OK', m)
        break
    except Exception as e:
        print('FAIL', m, str(e)[:80])
