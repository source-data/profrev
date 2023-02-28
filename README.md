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
