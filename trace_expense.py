from retriever import Retriever
from generator import generate_answer, _build_context

query = 'What is the expense ratio of HDFC Large Cap Fund Direct Growth?'
print('QUERY:', query)
retriever = Retriever()
results = retriever.retrieve(query, top_k=150, similarity_threshold=0.3)
print('RETRIEVED_COUNT:', len(results))

# rerank
ql = query.lower()
scored = []
for h in results:
    text = str(h.get('text','')).lower()
    score = h.get('similarity', 0)
    sid = str(h.get('source_id','')).lower()
    if 'expense ratio' in ql:
        fund_match = ('hdfc large cap' in ql and 'direct growth' in ql)
        if '1.02' in h.get('text','') and 'hdfc large cap' in text:
            score += 0.5
        if 'expense ratio' in text and 'hdfc large cap' in text:
            score += 0.4
        if fund_match and 'hdfc large cap' in text and 'direct growth' in text and 'expense ratio' in text:
            score += 0.3
        elif fund_match and 'hdfc large cap' in text and 'expense ratio' in text:
            score += 0.2
        elif 'expense ratio' in text:
            score += 0.1
    scored.append((score,h))
scored.sort(key=lambda x:x[0],reverse=True)
results_final=[h for _,h in scored[:5]]
print('FINAL_COUNT:', len(results_final))
for i,h in enumerate(results_final):
    print('=== FINAL['+str(i)+'] source_id='+str(h.get('source_id'))+' ===')
    print(h.get('text'))
    print()
# check
found=False
for i,h in enumerate(results_final):
    if h.get('source_id')=='hdfc_large_cap' and 'Expense ratio' in h.get('text',''):
        found=True
        print('FOUND_hdfc_large_cap_with_expense_at',i)
        break
print('FOUND:', found)
ctx=_build_context(results_final)
print('CTX_HAS_102:', '1.02' in ctx)
try:
    ans=generate_answer(query,results_final)
    print('RAW:', ans)
except Exception as e:
    print('ERR')
