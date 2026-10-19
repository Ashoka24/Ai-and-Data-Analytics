# Retrieval-Augmented Generation: Practical Notes

Retrieval-augmented generation (RAG) combines a retrieval step with an answer-generation step. Rather than relying only on information encoded in model parameters, a system searches a selected document collection and passes relevant passages to a language model as context.

A typical pipeline has five stages: load documents, split text into chunks, encode or index chunks, retrieve passages for a question, and generate an answer that references the retrieved evidence. A useful implementation preserves source metadata during ingestion so retrieved passages can be traced back to a file and, for PDFs, a page.

Chunk size is a trade-off. Very short chunks can lose context; very long chunks can include irrelevant material and consume more context space. Overlap can preserve meaning across chunk boundaries, but too much overlap creates duplicate passages. The right settings depend on document type and question.

TF-IDF is a lexical baseline. It represents documents and queries using weighted terms, making it fast and transparent for small collections. It can struggle with synonyms and questions whose wording differs from the source. Dense embedding retrieval can improve semantic matching in some settings, but it introduces model and deployment choices that should be evaluated rather than assumed to be better.

RAG does not guarantee correctness. A system may retrieve irrelevant text, omit a key passage, misunderstand evidence, or produce a plausible answer unsupported by the source. Citations are useful only when they point to the actual material used and readers can verify that the cited text supports the claim.

For a practical evaluation, create realistic questions with expected supporting documents, then measure whether relevant evidence appears in the top retrieved passages. Separately review answer faithfulness, completeness, citation accuracy, latency and failure cases. Do not treat a high similarity score as a probability that an answer is true.
