Query rewriting improves RAG retrieval quality by transforming the original user question into better search queries before hitting your retriever.

The core idea is that users often phrase questions conversationally or ambiguously, while vector stores work better with precise, keyword-rich queries. An LLM rewrites the input into 3-5 optimized variants, retrieves from each, then merges/reranks the results.

1. Multi-Query Rewriting - It generates multiple query variants and combines results
2. Hypothetical Document Embeddings - Generate hypothetical answer docs, embed those for retrieval
3. Contextual Compression (Post-retrieval) - Filter irrelevant chunks after retrieval.
