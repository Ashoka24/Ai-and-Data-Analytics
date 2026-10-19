# Privacy and Data Handling Notes

Only add documents that you are permitted to process. Research files can contain personal information, unpublished findings, confidential company material or licence-restricted content. Check the relevant consent, institutional policy, contract and licence before indexing or sharing them.

In local retrieval mode, the app reads documents from the project folder and computes a TF-IDF index in the running Python process. The local retrieval path does not send document text to an external model service.

If optional OpenAI answer generation is enabled by setting OPENAI_API_KEY, retrieved passages and the question are sent to the configured OpenAI API. Do not use this mode with confidential, personal or restricted data unless the data handling is approved for that purpose. API usage may incur charges.

Keep API keys in environment variables or an approved secrets manager. Do not hard-code keys, commit them to Git, or paste them into logs. Keep large, sensitive or licensed datasets out of version control.

For a shared or production deployment, add access controls, retention rules, document-level permissions, audit logging and a process for removing documents from the index. This sample is intended for local portfolio demonstration and does not implement those controls.
