https://docs.langchain.com/langsmith/evaluation


## **Evaluation**
1. Golden Set: 
    - Small high-quality dataset of input-output pairs with expected behavior
    - Measure overall correctness
2. Adversarial Set: 
    - Tricky inputs designed to break the system based on real-world failures like noisy data, edge cases, prompt injection and jailbreak attempts
    - Test robustness and failure handling
3. Regression Suite: 
    - A subset of golden and adversarial examples that are run after every change
    - Ensure nothing breaks after changes that used to work before

### **Workflow**
Step 1: Build a Golden Set to measure baseline performance
Step 2: Run System and collect failures
Step 3: Analyze failures and create an Adversarial Set
Step 4: Fix failures and add them to the Regression Suite


## **LangChain + Ragas**
Use **LangChain** to execute your pipeline and **Ragas** to quantitatively evaluate retrieval and generation quality using structured datasets.

## **CICD-Style Evals**
### **What Problem CI/CD Evals Solve?**
In GenAI systems: Small Change -> Unexpected Behavior
Examples:
- Prompt tweak → better answers but more hallucinations
- New embedding model → better retrieval but worse recall
- Model upgrade → different tone / format

Without CICD evals, you ship regressions silently.

**CI/CD evals ensure every change to your GenAI system is automatically tested against quality benchmarks, preventing regressions and unsafe deployments.**

### **High-Level Architecture**
```
Code Change (PR / Commit)
        ↓
Run GenAI Pipeline
        ↓
Run Evaluation (Golden + Adversarial + Regression)
        ↓
Compute Metrics
        ↓
Compare with Baseline
        ↓
Pass / Fail Decision
        ↓
Deploy or Block
```

### **Step 1: Define Evals Dataset**
```
evals/
  golden.json
  adversarial.json
  regression.json
```

### **Step 2: Standardize your Evaluation Pipeline Interface by returning `structured outputs`**
```python
def run_pipeline(query):
    docs = retriever.get_relevant_documents(query)
    
    answer = llm.invoke({
        "question": query,
        "context": docs
    })
    
    return {
        "answer": answer,
        "contexts": [d.page_content for d in docs]
    }
```

### **Step 3: Create an Eval Script**
```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
import json

def load_dataset(path):
    with open(path) as f:
        return json.load(f)

def run_eval(dataset, pipeline):
    data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }

    for sample in dataset:
        output = pipeline(sample["input"])
        
        data["question"].append(sample["input"])
        data["answer"].append(output["answer"])
        data["contexts"].append(output["contexts"])
        data["ground_truth"].append(sample["expected_output"])

    ds = Dataset.from_dict(data)

    result = evaluate(
        ds,
        metrics=[faithfulness, answer_relevancy]
    )

    return result
```

### **Step 4: Define Pass/Fail Thresholds**
```python
THRESHOLDS = {
    "faithfulness": 0.85,
    "answer_relevancy": 0.80
}

def check_thresholds(result):
    for metric, threshold in THRESHOLDS.items():
        if result[metric] < threshold:
            raise Exception(f"{metric} below threshold!")
```

### **Step 5: Add Regression Comparison**
```python
BASELINE = {
  "faithfulness": 0.87,
  "answer_relevancy": 0.82
}

def check_regression(result):
    for metric, threshold in BASELINE.items():
        if result[metric] < threshold:
            raise Exception(f"Regression detected in {metric}")
```

### **Step 6: CI Integration (GitHub Actions Example)**
Create `.github/workflows/evals.yml`. Example
```yaml
name: GenAI Eval Pipeline

on: [pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run Evals
      run: |
        python run_evals.py
```

### **Step 7: Fail the Pipeline**
- If your script raises exception: `CI FAILS ❌` - Meaning, PR cannot be merged.
- If your script passes: `CI PASSES ✅` - Meaning, PR can be merged.

### **Step 8: Add Logging & Reporting**
Instead of just pass/fail, log detailed metrics like below to a file or dashboard.
```json
{
  "faithfulness": 0.86,
  "answer_relevancy": 0.81
}
```

Store in
- database
- S3
- dashboard (Grafana, Superset)

### **Step 9: Advanced**
1. Metric Breakdown: Track following metrics per dataset
    - golden → accuracy
    - adversarial → hallucination rate
    - regression → pass rate
2. Canary Evaluation: Before full deploy, run on small traffic subset
3. Alerting: If production metrics drop, send slack alert
4. Version Tracking: Track model version, prompt version, embedding version, etc...

