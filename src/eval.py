from src.retrieval import retrieve
from src.hybrid_retrieval import hybrid_search
from src.rerank import rerank
from src.metrics import precision_at_k, recall_at_k
import mlflow


golden_questions = [
    {
        "question": "What albums did Nas release in the 90s?",
        "golden_ids": [5, 6, 7, 8, 9]
    },
    {
        "question": "What was Nas's feud with Jay-Z about?",
        "golden_ids": [12, 14, 15, 358, 362]
    },
    {
        "question": "Tell me about Dr. Dre's career.",
        "golden_ids": [219, 220, 221]
    },
    {
        "question": "When was Wu-Tang Clan formed and what was their debut album?",
        "golden_ids": [150, 154, 187]
    }
]


def run_eval(golden_questions: list[dict], top_k: int = 5) -> None:
    '''
    Run all three practical strategies against the golden set,
    log precision/recall to MLflow
    '''
    mlflow.set_experiment('retrieval-comparison')
    
    results_by_method = {'vector': [], 'hybrid': [], 'reranked': []}
    for entry in golden_questions:
        question = entry['question']
        golden_ids = entry['golden_ids']
        
        vector_results = retrieve(question, top_k=top_k)
        hybrid_results = hybrid_search(question, top_k=top_k)
        candidates = hybrid_search(question, top_k=10)
        reranked_results = rerank(question, candidates, top_k=top_k)
        
        for name, results in [
            ('vector', vector_results),
            ('hybrid', hybrid_results),
            ('reranked', reranked_results)
        ]:
            retrieved_ids = [r['id'] for r in results]
            p = precision_at_k(retrieved_ids, golden_ids)
            r = recall_at_k(retrieved_ids, golden_ids)
            
            results_by_method[name].append((p, r))
    
    print("Retrieval loop finished, results_by_method =", results_by_method)
    
    # after the loop: for each method, compute the average precision/recall
    # across all questions, and log a run for it
    for method_name in ['vector', 'hybrid', 'reranked']:
        scores = results_by_method[method_name]
        avg_precision = sum(p for p, r in scores)/len(scores)
        avg_recall = sum(r for p, r in scores)/len(scores)
        print(f"About to log run for {method_name}: precision={avg_precision}, recall={avg_recall}")
        
        with mlflow.start_run(run_name=method_name):
            mlflow.log_param('method', method_name)
            mlflow.log_metric('avg precision', avg_precision)
            mlflow.log_metric('avg recall', avg_recall)
        print(f"Logged run for {method_name}")

mlflow.set_tracking_uri("sqlite:///C:/Users/alanm/OneDrive/Documents/DS AI Projects/music-rag/mlflow.db")
print("MLflow tracking URI:", mlflow.get_tracking_uri())
run_eval(golden_questions)
