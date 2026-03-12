**Retrieval quality is measured through a set of evaluation metrics that compare what documents were retrieved against what should have been retrieved for a given query.**

Think of it like grading a search engine—you need to know if the right information came back and if it was relevant to answering the question. LangSmith provides standardized evaluation approaches for this.

## Key Retrieval Quality Metrics

There are several metrics you can use to measure how well your retrieval system works:

## 1. Document Relevance

**Measures whether the retrieved documents actually answer the question.**

Use `LLM-as-judge` evaluators to assess if each retrieved document is semantically related to the query:

```python
from langsmith.evaluation import evaluate
from langchain_openai import ChatOpenAI

# Create an evaluator that scores document relevance
relevance_evaluator = "Document relevance"  # Built-in LangSmith evaluator

# Run evaluation
results = evaluate(
    dataset_name="your_retrieval_dataset",
    llm_as_judge=ChatOpenAI(model="gpt-4"),
    evaluators=["retrieval_qa"],  # Evaluates relevance
)

# View results
for result in results:
    print(f"Relevant: {result['score']}")  # 0 = not relevant, 1 = relevant
```

This returns a score showing what percentage of retrieved documents were actually relevant.

## 2. Answer Faithfulness

**Checks whether the LLM's answer is grounded in the retrieved documents (not making things up).**

```python
from langsmith.evaluation import LLMAsJudgeFaithfulness

faithfulness = LLMAsJudgeFaithfulness()

# Evaluates: Is the answer supported by the retrieved context?
score = faithfulness.evaluate_strings(
    prediction="The answer based on docs",
    reference="Original retrieved documents"
)

print(f"Faithfulness score: {score}")  # High = answer doesn't hallucinate
```

## 3. Answer Helpfulness

**Evaluates whether the generated answer actually helps address the user's question.**

```python
from langsmith.evaluation import LLMAsJudgeHelpfulness

helpfulness = LLMAsJudgeHelpfulness()

# Evaluates: Does the answer meaningfully address the question?
score = helpfulness.evaluate_strings(
    prediction="Your system's answer",
    input="User's original question"
)

print(f"Helpfulness score: {score}")
```

## 4. Answer Correctness (with Reference Data)

**If you have known correct answers, measure if your system matches them.**

```python
from langsmith.evaluation import evaluate

# Run evaluation comparing against reference answers
results = evaluate(
    dataset_name="qa_with_reference_answers",
    config={"evaluators": ["answer_correctness"]},  # Needs reference answers
)

# Shows: What % of answers matched the reference answer?
```

## Practical Setup: Building an Evaluation Dataset

Here's how to build a test dataset and measure retrieval quality end-to-end:

```python
from langsmith import Client
from langchain_openai import ChatOpenAI
from langchain.retrievers import VectorStoreRetriever

client = Client()

# Step 1: Create a test dataset with known good examples
dataset = client.create_dataset(
    dataset_name="retrieval_quality_test",
    description="Test queries with expected relevant docs"
)

# Add test examples
client.create_examples(
    inputs=[
        {"query": "What is machine learning?"},
        {"query": "How do transformers work?"},
        {"query": "Explain embeddings"},
    ],
    outputs=[
        {
            "answer": "Machine learning is...",
            "relevant_docs": ["doc_1", "doc_2"]
        },
        {
            "answer": "Transformers use attention...",
            "relevant_docs": ["doc_3", "doc_4"]
        },
        {
            "answer": "Embeddings convert text to vectors...",
            "relevant_docs": ["doc_5"]
        }
    ],
    dataset_id=dataset.id
)

# Step 2: Run your RAG application
def rag_pipeline(query: str):
    """Your retrieval + generation pipeline"""
    retrieved_docs = retriever.invoke(query)
    answer = llm.invoke(f"Answer based on: {retrieved_docs}\n\nQuestion: {query}")
    return {
        "answer": answer,
        "retrieved_docs": [doc.metadata["id"] for doc in retrieved_docs]
    }

# Step 3: Evaluate against the dataset
results = client.evaluate(
    dataset_id=dataset.id,
    target=rag_pipeline,
    evaluators=[
        "document_relevance",      # Did we retrieve the right docs?
        "answer_faithfulness",     # Is answer grounded in docs?
        "answer_helpfulness"       # Does answer help the user?
    ],
    experiment_prefix="chunk_size_experiment"
)

# View results
print(f"Average relevance score: {results.feedback_stats['document_relevance'].mean}")
print(f"Faithfulness: {results.feedback_stats['answer_faithfulness'].mean}")
```

## How to Use This to Optimize Chunk Size

Now you can iterate on chunk size and measure improvements:

```python
import pandas as pd

# Test different configurations
configs = [
    {"chunk_size": 500, "overlap": 100},
    {"chunk_size": 1000, "overlap": 200},  # Your starting point
    {"chunk_size": 1500, "overlap": 300},
    {"chunk_size": 2000, "overlap": 400},
]

results_summary = []

for config in configs:
    # Recreate chunking with new size
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["overlap"]
    )
    
    # Re-embed and index
    splits = text_splitter.split_documents(docs)
    vectorstore = InMemoryVectorStore.from_documents(splits, embeddings)
    
    # Run evaluation
    eval_results = client.evaluate(
        dataset_id=dataset.id,
        target=rag_pipeline,
        evaluators=["document_relevance", "answer_faithfulness"],
        experiment_prefix=f"chunk_{config['chunk_size']}"
    )
    
    results_summary.append({
        "chunk_size": config["chunk_size"],
        "relevance": eval_results.feedback_stats['document_relevance'].mean,
        "faithfulness": eval_results.feedback_stats['answer_faithfulness'].mean,
    })

# Compare results
df = pd.DataFrame(results_summary)
print(df)
# chunk_size  relevance  faithfulness
#      500      0.82        0.79
#     1000      0.89        0.85  ← Best!
#     1500      0.87        0.82
#     2000      0.84        0.78
```

## Key Signals That Retrieval Quality Is Poor

Watch for these in your evaluation results:

- **Low relevance score (< 0.7)**: Retrieved documents don't match the query. Try smaller chunks or better embedding model
- **Low faithfulness (< 0.75)**: LLM generates answers not supported by docs. Problem is generation, not retrieval
- **Low helpfulness (< 0.6)**: Retrieved context isn't sufficient to answer questions. Try larger chunk size or more retrieved docs (`k=6` → `k=10`)
- **High variation across queries**: Some questions answered well, others poorly. Data quality issue—check if your test dataset has diverse question types

## Quick Wins to Improve Retrieval Quality

```python
# 1. Retrieve more docs initially
retriever = vectorstore.as_retriever(k=10)  # Instead of k=6

# 2. Use better embeddings
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# 3. Adjust chunk overlap to preserve context
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=300  # More overlap = more context at boundaries
)

# 4. Use hybrid retrieval (keyword + semantic)
# (More advanced, reduces false negatives)
```

**Relevant docs:**

- [Evaluate a RAG Application](https://docs.langchain.com/langsmith/evaluate-rag-tutorial)
- [Application-specific Evaluation Approaches](https://docs.langchain.com/langsmith/evaluation-approaches)
- [Build a Custom RAG Agent with LangGraph](https://docs.langchain.com/oss/python/langgraph/agentic-rag)