Profiling of referee reports
============================

Planned steps:

- extract array of chunks (e.g. paragraphs) from ref reports
- extract array of chunks (e.g. paragraphs) from article full text or article subsection (eg. Introduction or Materials & Methods)
- for each chunk, obtain an embedding
- calculate distance matrix (e.g. dot product) between ref report chunk and article chunk, for each chunk in paper for each chunk in ref report
- obtain null distribution by calculating distance matrix for unrelated referee report-article pairs
- obtain distance matrci from related report-article pairs
- threshold individual distance to level of confidence and or use a computed score

Note: maybe think of learned score based on attention, with dot product-based weights to derive a value that can be later re-aligned with human preference

https://docs.pinecone.io/docs/openai

https://github.com/openai/openai-cookbook/blob/main/examples/Semantic_text_search_using_embeddings.ipynb

https://github.com/openai/openai-cookbook/blob/main/examples/Embedding_long_inputs.ipynb