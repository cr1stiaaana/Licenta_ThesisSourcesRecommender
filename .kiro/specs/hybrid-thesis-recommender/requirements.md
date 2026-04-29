# Requirements Document

## Introduction

The Hybrid Thesis Recommender is a web application that accepts a thesis title (and optionally an abstract or keywords) as input and returns a ranked list of academic articles and relevant web resources that would be useful for writing that thesis. The application is built on a Flask (Python) backend that serves both the REST API and the static frontend files. The frontend is implemented in plain HTML, CSS, and JavaScript — no frontend framework is used.

The backend combines multiple recommendation strategies — such as semantic similarity via LLM/NLP embeddings and keyword/metadata-based retrieval — into a hybrid pipeline to maximize relevance and coverage. In addition to indexed academic articles, the system retrieves relevant web resources (such as blog posts, documentation pages, educational resources, research institution pages, and encyclopedic references) via a web search API. The goal is to help researchers and students quickly discover relevant literature and online resources without manually searching multiple databases or websites.

The system supports bilingual operation in Romanian and English. Queries may be submitted in either language, the article corpus and web search results may contain content in both languages, and system messages are returned in the detected language of the Query. The Web_UI adapts its labels, placeholders, and messages to the detected Query_Language or a user-selectable language toggle.

## Glossary

- **System**: The Hybrid Thesis Recommender application as a whole.
- **User**: A researcher, student, or academic who submits a thesis title to receive article recommendations.
- **Query**: The input provided by the User, consisting of at minimum a thesis title, and optionally an abstract or keywords.
- **Article**: An academic paper or publication stored in or retrieved from a connected data source, characterized by a title, abstract, authors, publication year, and optionally a DOI or URL.
- **Recommendation**: A ranked Article returned by the System in response to a Query.
- **Embedding**: A dense vector representation of text produced by an NLP or LLM model, used for semantic similarity computation.
- **Semantic_Retriever**: The component responsible for computing Embeddings and retrieving Articles by semantic similarity.
- **Keyword_Retriever**: The component responsible for retrieving Articles using keyword or BM25-style matching.
- **Hybrid_Ranker**: The component that merges and re-ranks results from the Semantic_Retriever and Keyword_Retriever into a single ordered list.
- **Article_Store**: The data store (vector database and/or inverted index) that holds indexed Articles available for retrieval.
- **Ingestion_Pipeline**: The component responsible for loading, parsing, and indexing Articles into the Article_Store.
- **Score**: A numerical relevance value in the range [0.0, 1.0] assigned to each Recommendation by the Hybrid_Ranker.
- **Top-K**: The maximum number of Recommendations returned for a single Query, configurable by the User or operator.
- **Supported_Language**: One of the two languages the System is designed to operate in: Romanian (`ro`) or English (`en`).
- **Query_Language**: The Supported_Language detected in the Query submitted by the User.
- **Language_Detector**: The component responsible for identifying the Supported_Language of a given text input.
- **Web_Resource**: A publicly accessible web page (such as a blog post, documentation page, educational resource, research institution page, or encyclopedic reference) retrieved in response to a Query via a web search API.
- **Web_Retriever**: The component responsible for querying a web search API and returning a ranked list of Web_Resources relevant to the Query.
- **Web_Search_API**: An external search service (such as Google Custom Search, Bing Search API, or DuckDuckGo Search API) used by the Web_Retriever to discover Web_Resources.
- **Resource_Type**: A label attached to each item in the response that identifies whether it is an Article or a Web_Resource.
- **Web_Score**: A numerical relevance value in the range [0.0, 1.0] assigned to each Web_Resource by the Hybrid_Ranker based on the ranking signal returned by the Web_Search_API and any additional re-ranking applied by the System.
- **Page_Keywords**: An optional list of significant terms extracted from a Web_Resource page by the Web_Retriever, included in the Web_Resource Recommendation to help the User assess relevance without visiting the page.
- **REST_API**: The HTTP application programming interface exposed by the Flask backend, through which the Web_UI and any external clients submit Queries and receive Recommendations as JSON responses.
- **Web_UI**: The browser-based user interface served by the Flask backend, implemented in plain HTML, CSS, and JavaScript, through which the User interacts with the System.
- **Content_Verifier**: The component responsible for checking that the actual content of a Web_Resource or Article is genuinely relevant to the Query, not just its title, by comparing the semantic similarity of the title against the semantic similarity of the snippet, description, or abstract.
- **Title_Content_Mismatch**: A condition where the title of a Web_Resource or Article appears relevant to the Query (high title similarity score) but the body content — represented by the snippet, description, or abstract — does not support that relevance (significantly lower content similarity score).
- **Quality_Score**: A secondary score computed by the Content_Verifier that penalizes items where the title relevance significantly exceeds the content relevance, used to down-rank or filter clickbait candidates before they are returned to the User.
- **Domain_Blocklist**: A configurable list of domain names associated with low-quality or content-farm sources; Web_Resources whose URLs belong to a blocklisted domain are excluded from results by the Content_Verifier.
- **User_Rating**: A numerical score submitted by the User to indicate how useful a specific Recommendation was to their research, on a scale of 1 to 5.
- **Feedback_Store**: The persistent data store that records User_Ratings alongside the associated Query, Recommendation identifier, and timestamp.
- **Feedback_Signal**: Aggregated User_Rating data associated with a Recommendation item, used optionally to influence future ranking.

---

## Requirements

### Requirement 1: Query Input and Validation

**User Story:** As a User, I want to submit a thesis title as my query, so that I can receive relevant article recommendations without needing to formulate a complex search expression.

#### Acceptance Criteria

1. THE System SHALL accept a Query containing at minimum a thesis title string of 3 to 500 characters.
2. WHERE an abstract is provided alongside the title, THE System SHALL incorporate the abstract text into the Query representation used for retrieval.
3. WHERE keywords are provided alongside the title, THE System SHALL incorporate those keywords into the Query representation used for retrieval.
4. IF the thesis title is fewer than 3 characters or exceeds 500 characters, THEN THE System SHALL return a validation error message describing the constraint violation.
5. IF the Query contains only whitespace or punctuation, THEN THE System SHALL return a validation error indicating that a meaningful title is required.
6. WHEN a Query is received, THE Language_Detector SHALL identify the Query_Language as either Romanian (`ro`) or English (`en`).
7. IF the Language_Detector cannot determine a Supported_Language from the Query text, THEN THE System SHALL default the Query_Language to English (`en`) and proceed with retrieval.

---

### Requirement 2: Semantic Retrieval

**User Story:** As a User, I want the system to understand the meaning of my thesis title, so that I receive articles that are conceptually related even when they do not share exact keywords.

#### Acceptance Criteria

1. WHEN a valid Query is received, THE Semantic_Retriever SHALL generate an Embedding for the Query using a pre-configured NLP or LLM embedding model.
2. THE Semantic_Retriever SHALL use an embedding model that natively supports both Romanian and English text without requiring separate models per language.
3. WHEN the Query Embedding is generated, THE Semantic_Retriever SHALL retrieve the top-K Articles from the Article_Store whose Embeddings have the highest cosine similarity to the Query Embedding.
4. THE Semantic_Retriever SHALL assign each retrieved Article a similarity Score in the range [0.0, 1.0].
5. IF the embedding model is unavailable or returns an error, THEN THE Semantic_Retriever SHALL propagate a structured error to the System so that the System can fall back to keyword-only retrieval.

---

### Requirement 3: Keyword-Based Retrieval

**User Story:** As a User, I want the system to also match articles by exact and near-exact terms from my thesis title, so that highly relevant articles with precise terminology are not missed.

#### Acceptance Criteria

1. WHEN a valid Query is received, THE Keyword_Retriever SHALL extract significant terms from the Query title and any provided keywords.
2. WHEN terms are extracted, THE Keyword_Retriever SHALL retrieve Articles from the Article_Store using a BM25 or equivalent term-frequency-based ranking method.
3. THE Keyword_Retriever SHALL assign each retrieved Article a relevance Score normalized to the range [0.0, 1.0].
4. IF no Articles match the extracted terms, THEN THE Keyword_Retriever SHALL return an empty result set without raising an error.

---

### Requirement 4: Hybrid Ranking and Fusion

**User Story:** As a User, I want the best results from both semantic and keyword retrieval combined into a single ranked list, so that I get comprehensive and relevant recommendations.

#### Acceptance Criteria

1. WHEN results are available from both the Semantic_Retriever and the Keyword_Retriever, THE Hybrid_Ranker SHALL merge the two result sets using a weighted fusion strategy (such as Reciprocal Rank Fusion or a configurable weighted sum of Scores).
2. THE Hybrid_Ranker SHALL produce a single ranked list of unique Articles ordered by descending combined Score.
3. WHERE only one retriever returns results (due to fallback or empty results), THE Hybrid_Ranker SHALL rank and return the available results without error.
4. THE Hybrid_Ranker SHALL deduplicate Articles that appear in both result sets, retaining the higher combined Score.
5. THE System SHALL return at most Top-K Recommendations, where Top-K is configurable and defaults to 10.
6. WHEN Web_Resources are retrieved by the Web_Retriever, THE Hybrid_Ranker SHALL assign each Web_Resource a Web_Score and produce a separately ranked Web_Resource result set ordered by descending Web_Score.
7. THE Hybrid_Ranker SHALL attach a Resource_Type label to each item in both result sets, distinguishing Articles from Web_Resources.
8. THE System SHALL apply Top-K limits independently to the Article result set and the Web_Resource result set; the Article Top-K and Web_Resource Top-K SHALL each be configurable and SHALL default to 10.

---

### Requirement 5: Recommendation Output

**User Story:** As a User, I want each recommended article or web resource to include enough metadata to evaluate its relevance and locate the source, so that I can decide which items to read.

#### Acceptance Criteria

1. THE System SHALL include the following fields in each Article Recommendation: article title, authors, publication year, abstract snippet (up to 300 characters), relevance Score, and Resource_Type set to `"article"`.
2. THE System SHALL include the following fields in each Web_Resource Recommendation: page title, URL, a snippet or description (up to 300 characters), Web_Score, and Resource_Type set to `"web"`.
3. WHERE a DOI or URL is available for an Article, THE System SHALL include it in the Article Recommendation.
4. THE System SHALL return the response as two distinct result sets: one containing Article Recommendations ordered by descending Score, and one containing Web_Resource Recommendations ordered by descending Web_Score; THE System SHALL NOT interleave Articles and Web_Resources into a single ranked list.
5. WHERE the Web_Retriever is able to extract keywords from a Web_Resource page, THE System SHALL include those keywords as an optional `keywords` field in the Web_Resource Recommendation to help the User assess relevance without visiting the page.
6. THE System SHALL return results within 5 seconds of receiving a valid Query under normal operating conditions.
7. IF no Articles meet a minimum Score threshold of 0.1, THEN THE System SHALL return an empty Article result set and a message indicating that no sufficiently relevant articles were found.
8. IF no Web_Resources meet a minimum Web_Score threshold of 0.1, THEN THE System SHALL return an empty Web_Resource result set and a message indicating that no sufficiently relevant web resources were found.
9. THE System SHALL return all user-facing messages (validation errors, fallback notices, empty-result messages, and error descriptions) in the Query_Language detected for that request.
10. THE System SHALL clearly label each item in the response with its Resource_Type so that the caller can distinguish Articles from Web_Resources without inspecting other fields.
11. WHERE the Content_Verifier has flagged an Article Recommendation as a potential clickbait candidate, THE System SHALL include an optional `quality_warning` field in that Article Recommendation containing a localized warning string.
12. WHERE the Content_Verifier has flagged a Web_Resource Recommendation as a potential clickbait candidate, THE System SHALL include an optional `quality_warning` field in that Web_Resource Recommendation containing a localized warning string.

---

### Requirement 5b: Content Quality and Clickbait Filtering

**User Story:** As a User, I want the system to detect when a result's title sounds relevant to my thesis but the actual content is unrelated or misleading, so that I am not misled by clickbait articles or low-quality web pages.

#### Acceptance Criteria

1. WHEN the Hybrid_Ranker produces a ranked result set, THE Content_Verifier SHALL compute a content similarity score for each item by comparing the Query Embedding against the Embedding of the item's snippet or description (for Web_Resources) or abstract (for Articles), using the same multilingual embedding model used by the Semantic_Retriever.
2. WHEN the Content_Verifier has computed both a title similarity score and a content similarity score for an item, THE Content_Verifier SHALL compute a Quality_Score that penalizes the item's overall Score in proportion to the magnitude of the Title_Content_Mismatch.
3. IF the difference between an item's title similarity score and its content similarity score exceeds a configurable mismatch threshold, THEN THE Content_Verifier SHALL flag that item as a potential clickbait candidate by setting a `quality_warning` field on the item.
4. THE System SHALL expose a configuration interface that allows the operator to set the mismatch threshold used by the Content_Verifier; the default mismatch threshold SHALL be 0.3 (i.e., title similarity exceeds content similarity by more than 0.3).
5. IF a flagged item's Quality_Score falls below the minimum Score threshold (0.1 for Articles) or minimum Web_Score threshold (0.1 for Web_Resources), THEN THE Content_Verifier SHALL exclude that item from the result set entirely.
6. WHERE a flagged item's Quality_Score remains at or above the applicable minimum threshold, THE Content_Verifier SHALL retain the item in the result set and set its `quality_warning` field to a localized warning string so that the User is informed rather than silently losing the result.
7. WHEN the Content_Verifier evaluates a Web_Resource, THE Content_Verifier SHALL use the snippet or description returned by the Web_Search_API as the content signal; THE Content_Verifier SHALL NOT make additional HTTP requests to fetch the full page content.
8. WHEN the Content_Verifier evaluates an Article, THE Content_Verifier SHALL use the Article's abstract as the content signal; IF an Article has no abstract, THEN THE Content_Verifier SHALL skip the mismatch check for that Article and retain it without a `quality_warning`.
9. THE Content_Verifier SHALL check each Web_Resource URL against the Domain_Blocklist; IF the URL's domain matches an entry in the Domain_Blocklist, THEN THE Content_Verifier SHALL exclude that Web_Resource from the result set without applying the mismatch check.
10. THE System SHALL expose a configuration interface that allows the operator to manage the Domain_Blocklist by adding or removing domain entries.
11. IF the Query_Language is Romanian, THEN THE Content_Verifier SHALL set the `quality_warning` field to "⚠ Verificați conținutul" for flagged items.
12. IF the Query_Language is English, THEN THE Content_Verifier SHALL set the `quality_warning` field to "⚠ Verify content" for flagged items.

---

### Requirement 6: Web Resource Retrieval

**User Story:** As a User, I want the system to search the web for pages related to my thesis title — such as official documentation sites, blogs, and community posts — so that I can learn from practitioners and authoritative sources beyond academic literature.

#### Acceptance Criteria

1. WHEN a valid Query is received, THE Web_Retriever SHALL issue a search query to the Web_Search_API using the thesis title (and any provided keywords) as the search expression.
2. THE Web_Retriever SHALL retrieve at most a configurable number of Web_Resources per Query, defaulting to 10.
3. THE Web_Retriever SHALL include the following metadata for each Web_Resource: page title, URL, a snippet or description of up to 300 characters, and the ranking position returned by the Web_Search_API.
4. THE Web_Retriever SHALL assign each Web_Resource a Web_Score in the range [0.0, 1.0] derived from the ranking signal provided by the Web_Search_API.
5. IF the Web_Search_API is unavailable or returns an error, THEN THE Web_Retriever SHALL return an empty Web_Resource result set and propagate a structured notice to the System so that the System can continue with Article-only results.
6. THE Web_Retriever SHALL operate independently of the Ingestion_Pipeline; Web_Resources SHALL be fetched live at Query time and SHALL NOT be stored in the Article_Store.
7. WHEN the Web_Retriever issues a search query, THE Web_Retriever SHALL formulate the query in the Query_Language so that returned Web_Resources are preferentially in the same language as the Query.
8. WHERE the operator enables bilingual web search, THE Web_Retriever SHALL issue parallel queries in both Romanian and English and merge the resulting Web_Resources, deduplicating by URL, before passing them to the Hybrid_Ranker.
9. THE System SHALL expose a configuration interface that allows the operator to select the Web_Search_API provider (such as Google Custom Search, Bing Search API, or DuckDuckGo Search API) and supply the required credentials.
10. IF the Web_Search_API returns a URL that is inaccessible or returns an HTTP error status, THEN THE Web_Retriever SHALL exclude that Web_Resource from the result set without raising an error.

---

### Requirement 7: Article Ingestion and Indexing

**User Story:** As an operator, I want to load a corpus of academic articles into the system, so that the recommender has a knowledge base to search against.

> **Note:** Web resource retrieval is handled live at Query time by the Web_Retriever (see Requirement 6) and is intentionally separate from this ingestion pipeline.

#### Acceptance Criteria

1. THE Ingestion_Pipeline SHALL accept Articles in at least one structured format (such as JSON, CSV, or BibTeX).
2. WHEN an Article is ingested, THE Ingestion_Pipeline SHALL generate and store an Embedding for the Article's title and abstract in the Article_Store.
3. WHEN an Article is ingested, THE Ingestion_Pipeline SHALL index the Article's title, abstract, and keywords in the keyword index of the Article_Store.
4. IF an Article is missing a title or abstract, THEN THE Ingestion_Pipeline SHALL skip that Article and log a warning identifying the malformed record.
5. THE Ingestion_Pipeline SHALL support incremental ingestion, allowing new Articles to be added without re-indexing the entire Article_Store.
6. THE Ingestion_Pipeline SHALL accept Articles whose title and abstract are written in Romanian, English, or a mixture of both languages.
7. WHEN an Article is ingested, THE Ingestion_Pipeline SHALL store the detected language of the Article's title as metadata in the Article_Store to support language-aware retrieval.

---

### Requirement 8: Configuration and Tunability

**User Story:** As an operator, I want to configure the retrieval weights and model settings, so that I can tune the system's behavior for different corpora and use cases.

#### Acceptance Criteria

1. THE System SHALL expose a configuration interface that allows the operator to set the relative weight of semantic versus keyword retrieval scores used by the Hybrid_Ranker.
2. THE System SHALL expose a configuration interface that allows the operator to specify the embedding model name or endpoint used by the Semantic_Retriever.
3. THE System SHALL expose a configuration interface that allows the operator to set the Top-K value.
4. WHEN configuration values are changed, THE System SHALL apply the new values to subsequent Queries without requiring a full restart.
5. IF an invalid configuration value is provided (such as a negative weight or a Top-K of zero), THEN THE System SHALL reject the value and retain the previous valid configuration.

---

### Requirement 9: Error Handling and Resilience

**User Story:** As a User, I want the system to remain functional and informative when individual components fail, so that I still receive useful results or clear feedback.

#### Acceptance Criteria

1. IF the Semantic_Retriever fails, THEN THE System SHALL fall back to keyword-only retrieval and include a notice in the response indicating that semantic retrieval was unavailable.
2. IF the Keyword_Retriever fails, THEN THE System SHALL fall back to semantic-only retrieval and include a notice in the response indicating that keyword retrieval was unavailable.
3. IF both retrievers fail, THEN THE System SHALL return a structured error response with a human-readable message and an error code.
4. IF the Web_Retriever fails or the Web_Search_API is unavailable, THEN THE System SHALL continue processing and return Article Recommendations only, including a notice in the response indicating that web resource retrieval was unavailable.
5. WHEN an unexpected error occurs during processing, THE System SHALL log the error with sufficient context (Query identifier, timestamp, component name) to support diagnosis.
6. THE System SHALL return an error response within 10 seconds even when a component is unresponsive, rather than blocking indefinitely.

---

### Requirement 10: Multilingual Support (Romanian and English)

**User Story:** As a User, I want to submit my thesis query in Romanian or English and receive relevant recommendations regardless of the language of the articles in the corpus, so that I can find useful literature in both languages without switching interfaces or reformulating my query.

#### Acceptance Criteria

1. THE System SHALL accept Queries written in Romanian, English, or a mixture of both languages.
2. WHEN a Query is received, THE Language_Detector SHALL determine the Query_Language and attach it to the request context for use by all downstream components.
3. THE Semantic_Retriever SHALL produce semantically meaningful Embeddings for Query text in both Romanian and English using a single multilingual embedding model (such as a model from the `sentence-transformers` multilingual family or equivalent).
4. WHEN a Romanian-language Query is processed, THE Semantic_Retriever SHALL retrieve Articles from the Article_Store regardless of whether those Articles are in Romanian or English, based on cross-lingual semantic similarity.
5. WHEN an English-language Query is processed, THE Semantic_Retriever SHALL retrieve Articles from the Article_Store regardless of whether those Articles are in Romanian or English, based on cross-lingual semantic similarity.
6. THE Keyword_Retriever SHALL index and match terms from Article titles, abstracts, and keywords in both Romanian and English without requiring separate indexes per language.
7. THE Hybrid_Ranker SHALL produce a correctly ranked result list when the Query and the retrieved Articles are in different Supported_Languages.
8. THE System SHALL return all user-facing messages — including validation errors, fallback notices, empty-result messages, and structured error descriptions — in the Query_Language of the current request.
9. IF the Query_Language is Romanian, THEN THE System SHALL return the message "Nu au fost găsite articole suficient de relevante." when no Articles meet the minimum Score threshold, and the message "Nu au fost găsite resurse web suficient de relevante." when no Web_Resources meet the minimum Web_Score threshold.
10. IF the Query_Language is English, THEN THE System SHALL return the message "No sufficiently relevant articles were found." when no Articles meet the minimum Score threshold, and the message "No sufficiently relevant web resources were found." when no Web_Resources meet the minimum Web_Score threshold.
11. THE System SHALL expose a configuration option that allows the operator to restrict retrieval to Articles of a specific Supported_Language; WHERE this option is not set, THE System SHALL retrieve Articles in both languages.

---

### Requirement 11: Web Application Interface

**User Story:** As a User, I want to interact with the recommender through a web browser, so that I can submit queries and view results without installing any software or using a command-line interface.

#### Acceptance Criteria

1. THE Flask_Backend SHALL serve the Web_UI as static HTML, CSS, and JavaScript files from a dedicated static assets directory, making the application accessible via a standard web browser.
2. THE Web_UI SHALL present an input form containing at minimum a text field for the thesis title, optional fields for an abstract and keywords, and a submit button to trigger the recommendation request.
3. WHEN the User submits the form, THE Web_UI SHALL send the Query to the REST_API endpoint `POST /recommend` and display the returned results without a full page reload.
4. THE REST_API SHALL expose a `POST /recommend` endpoint that accepts a JSON request body containing the thesis title (required), abstract (optional), and keywords (optional), and returns a JSON response containing the Article result set and the Web_Resource result set as two distinct arrays.
5. THE Web_UI SHALL display the Article result set and the Web_Resource result set in two clearly separated sections, each with a visible section heading.
6. THE Web_UI SHALL render each Article Recommendation as a card showing: title, authors, publication year, abstract snippet, relevance Score, Resource_Type badge, and DOI or URL where available.
7. THE Web_UI SHALL render each Web_Resource Recommendation as a card showing: page title, URL (as a clickable link), snippet, Web_Score, Resource_Type badge, and Page_Keywords where available.
8. WHILE a recommendation request is in progress, THE Web_UI SHALL display a visible loading indicator and disable the submit button to prevent duplicate submissions.
9. IF the REST_API returns a validation error or a system error, THEN THE Web_UI SHALL display the error message inline on the page without navigating away from the form.
10. THE Web_UI SHALL support both Romanian and English: all labels, placeholders, section headings, and user-facing messages SHALL be rendered in the Query_Language detected for the most recent request, or in the language selected via a language toggle control available to the User before submission.
11. WHEN the User changes the language toggle, THE Web_UI SHALL immediately update all static labels and placeholder text to the selected Supported_Language without requiring a page reload.
12. THE Flask_Backend SHALL serve the Web_UI and the REST_API from the same origin so that no cross-origin configuration is required for standard deployments.
13. WHERE an Article Recommendation or Web_Resource Recommendation carries a `quality_warning` field, THE Web_UI SHALL render a visible warning badge on that result card displaying the localized warning string (Romanian: "⚠ Verificați conținutul", English: "⚠ Verify content").
14. THE Web_UI SHALL render the warning badge in a visually distinct style (such as a yellow or amber indicator) so that the User can immediately distinguish flagged results from unflagged results without reading the badge text.
15. THE Web_UI SHALL include a rating control (1–5 stars) on each Article and Web_Resource result card that the User can interact with to submit a User_Rating.
16. WHEN the User submits a User_Rating, THE Web_UI SHALL send it asynchronously to the REST_API endpoint `POST /feedback` without reloading the page or disrupting the results view.
17. THE rating control SHALL display the User's previously submitted User_Rating for that result card if one exists.
18. WHERE aggregate ratings are available for a result item, THE Web_UI SHALL display the average User_Rating and the total number of ratings on that result card.
19. THE rating control label SHALL be localized: Romanian SHALL display "Utilitate" and English SHALL display "Usefulness".

---

### Requirement 12: User Relevancy Rating

**User Story:** As a User, I want to rate how useful a recommended article or web resource was to my research, so that I can provide feedback and benefit from the collective ratings of other users.

#### Acceptance Criteria

1. THE System SHALL expose a REST_API endpoint `POST /feedback` that accepts a JSON request body containing a Recommendation identifier, the associated Query, a User_Rating value (integer in the range [1, 5]), and an optional user or session identifier.
2. WHEN a User_Rating is submitted to `POST /feedback`, THE System SHALL persist the rating in the Feedback_Store alongside the Recommendation identifier, the Query, and a timestamp.
3. IF the submitted User_Rating value is outside the range [1, 5] or is not an integer, THEN THE System SHALL return a validation error describing the constraint violation.
4. WHEN a User submits a User_Rating for a Recommendation for which they have already submitted a rating, THE System SHALL update the existing rating in the Feedback_Store rather than creating a duplicate entry.
5. THE System SHALL expose a REST_API endpoint `GET /feedback/{item_id}` that returns the current User_Rating submitted by the requesting user (if any) and the aggregate rating data (average score and total number of ratings) for the specified Recommendation item.
6. WHEN `GET /feedback/{item_id}` is called for an item with no ratings, THE System SHALL return a response indicating zero ratings and no average score, without raising an error.
7. THE Feedback_Store SHALL persist User_Ratings durably so that ratings are not lost between application restarts.
8. WHERE the operator enables Feedback_Signal-based re-ranking, THE Hybrid_Ranker SHALL apply a configurable boost to items whose Feedback_Signal (average User_Rating across similar Queries) exceeds a configurable threshold, so that consistently highly-rated items receive a small ranking advantage in future Queries.
9. WHERE the operator does not enable Feedback_Signal-based re-ranking, THE System SHALL return results using the standard ranking pipeline without applying any User_Rating boost.
10. THE System SHALL expose a configuration interface that allows the operator to enable or disable Feedback_Signal-based re-ranking and to set the boost magnitude and minimum rating threshold.
11. IF the Feedback_Store is unavailable when a rating submission is received, THEN THE System SHALL return a structured error response and SHALL NOT silently discard the submitted rating.
12. IF the Query_Language is Romanian, THEN THE System SHALL return user-facing feedback messages in Romanian (e.g., "Evaluarea a fost salvată." for a successful submission).
13. IF the Query_Language is English, THEN THE System SHALL return user-facing feedback messages in English (e.g., "Rating saved." for a successful submission).
