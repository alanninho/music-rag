from src.retrieval.vector import retrieve
from src.retrieval.hybrid import hybrid_search
from src.retrieval.rerank import rerank
from src.evaluation.metrics import precision_at_k, recall_at_k
from src.generation.groundedness import check_groundedness



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

groundedness_test_cases = [
    {
        "context": "Nas released his debut album Illmatic in 1994.",
        "answer": "Nas released Illmatic in 1994.",
        "expected": True  # clearly grounded
    },
    {
        "context": "Nas released his debut album Illmatic in 1994.",
        "answer": "Nas won a Grammy in 1995.",
        "expected": False  # clearly ungrounded - not mentioned at all
    },
    {
        "context": "Nas has won one Grammy out of 17 nominations.",
        "answer": "Nas has won a Grammy award.",
        "expected": True  # grounded - doesn't claim a specific year
    },
    {
        "context": "Nas has won one Grammy out of 17 nominations.",
        "answer": "Nas won his Grammy in 1995 for Illmatic.",
        "expected": False  # ungrounded - invents specifics not in context
    },
]


def evaluate_groundedness_checker(test_cases: list[dict]) -> float:
    """
    Measure how often check_groundedness agrees with expected labels.
    Returns accuracy (0.0 to 1.0).
    """
    correct = 0
    for case in test_cases:
        result = check_groundedness(case['answer'], case['context'])
        if result['is_grounded'] == case['expected']:
            correct += 1
        else:
            print(f"Mismatch: expected {case['expected']}, got {result['is_grounded']}")
            print(f"  Answer: {case['answer']}")
            print(f"  Reasoning: {result['explanation']}")
    
    accuracy = correct / len(test_cases)
    print(f"Groundedness checker accuracy: {accuracy:.2%} ({correct}/{len(test_cases)})")
    return accuracy

print(evaluate_groundedness_checker(groundedness_test_cases))
