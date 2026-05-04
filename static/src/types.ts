/**
 * Type definitions for Hybrid Thesis Recommender
 * Based on OpenAPI 3.0.3 specification
 */

/* ── API Request/Response Types ─────────────────────────────── */

export interface RecommendRequest {
  title: string;
  abstract?: string;
  keywords?: string[];
  offset?: number;
  type?: 'both' | 'articles' | 'web';
}

export interface Article {
  resource_type: 'article';
  title: string;
  authors: string[];
  year: number | null;
  abstract_snippet: string | null;
  doi: string | null;
  url: string | null;
  keywords: string[];
  score: number;
  quality_warning: string | null;
  item_id: string;
}

export interface WebResource {
  resource_type: 'web';
  title: string;
  url: string;
  snippet: string;
  web_score: number;
  keywords: string[];
  quality_warning: string | null;
  item_id: string;
}

export type RecommendationItem = Article | WebResource;

export interface RecommendResponse {
  query_language: 'ro' | 'en';
  articles: Article[];
  web_resources: WebResource[];
  notices: string[];
  error: string | null;
}

export interface FeedbackRequest {
  item_id: string;
  query: string;
  rating: number; // 1-5
  session_id?: string;
}

export interface FeedbackResponse {
  message: string;
  error: string | null;
}

export interface FeedbackQueryResult {
  item_id: string;
  rating_count: number;
  user_rating: number | null;
  average_rating: number | null;
}

export interface UserInfo {
  id: number;
  username: string;
  email: string;
}

export interface AuthResponse {
  message: string;
  user: UserInfo;
  error?: string;
}

export interface SavedItemsResponse {
  items: RecommendationItem[];
}

/* ── Application State Types ────────────────────────────────── */

export interface QueryData {
  title: string;
  abstract: string | null;
  keywords: string[];
}

export interface AppState {
  currentQuery: string;
  currentQueryData: QueryData | null;
  allArticles: Article[];
  allWebResources: WebResource[];
  displayedArticles: number;
  displayedWebResources: number;
  hasMoreArticles: boolean;
  hasMoreWebResources: boolean;
  currentLang: Language;
  timestamp: number;
}

/* ── UI Types ───────────────────────────────────────────────── */

export type Language = 'ro' | 'en';

export type Theme = 'light' | 'dark';

export interface I18nStrings {
  page_title: string;
  site_title: string;
  form_heading: string;
  label_title: string;
  label_abstract: string;
  label_keywords: string;
  optional: string;
  placeholder_title: string;
  placeholder_abstract: string;
  placeholder_keywords: string;
  hint_title: string;
  hint_abstract: string;
  hint_keywords: string;
  btn_submit: string;
  loading: string;
  heading_articles: string;
  heading_web: string;
  no_articles: string;
  no_web: string;
  footer_text: string;
  badge_article: string;
  badge_web: string;
  label_score: string;
  label_authors: string;
  label_year: string;
  label_doi: string;
  label_url: string;
  label_keywords_card: string;
  label_usefulness: string;
  rating_submitted: string;
  rating_error: string;
  avg_rating: string;
  ratings_count: string;
  btn_save: string;
  btn_unsave: string;
  btn_load_more: string;
  no_more_articles: string;
  no_more_web: string;
  saved_items: string;
  no_saved_items: string;
  view_saved: string;
  btn_login: string;
  btn_register: string;
  btn_logout: string;
  login_title: string;
  register_title: string;
  label_username: string;
  label_email: string;
  label_password: string;
  no_account: string;
  have_account: string;
  register_link: string;
  login_link: string;
  btn_about: string;
  about_title: string;
  about_heading: string;
  about_description: string;
  about_features_title: string;
  about_feature_hybrid: string;
  about_feature_web: string;
  about_feature_quality: string;
  about_feature_feedback: string;
  about_feature_bilingual: string;
  about_how_title: string;
  about_how_step1: string;
  about_how_step2: string;
  about_how_step3: string;
  about_how_step4: string;
}

export type I18nDictionary = Record<Language, I18nStrings>;

/* ── DOM Element Types ──────────────────────────────────────── */

export interface DOMElements {
  langToggleBtn: HTMLButtonElement;
  themeToggleBtn: HTMLButtonElement;
  queryForm: HTMLFormElement;
  titleInput: HTMLInputElement;
  abstractInput: HTMLTextAreaElement;
  keywordsInput: HTMLInputElement;
  submitBtn: HTMLButtonElement;
  loadingSpinner: HTMLElement;
  errorContainer: HTMLElement;
  errorMessage: HTMLElement;
  noticesContainer: HTMLElement;
  resultsWrapper: HTMLElement;
  articlesList: HTMLElement;
  articlesEmpty: HTMLElement;
  articlesLoadMore: HTMLButtonElement;
  webList: HTMLElement;
  webEmpty: HTMLElement;
  webLoadMore: HTMLButtonElement;
  savedBtn: HTMLButtonElement;
  savedModal: HTMLElement;
  savedModalClose: HTMLButtonElement;
  savedList: HTMLElement;
  tabArticles: HTMLButtonElement;
  tabWeb: HTMLButtonElement;
  panelArticles: HTMLElement;
  panelWeb: HTMLElement;
  articlesCount: HTMLElement;
  webCount: HTMLElement;
}

/* ── Utility Types ──────────────────────────────────────────── */

export interface StarRatingElements {
  wrapper: HTMLElement;
  starsEl: HTMLElement;
  starButtons: HTMLButtonElement[];
  aggregateEl: HTMLElement;
}

export type ItemId = `doi:${string}` | `url:${string}` | `title:${string}`;

/* ── Constants ──────────────────────────────────────────────── */

export const ITEMS_PER_PAGE = 5;
export const SESSION_STORAGE_KEY = 'thesis_recommender_session_id';
export const STATE_KEY = 'thesis_recommender_state';
export const SAVED_ITEMS_KEY = 'thesis_recommender_saved_items';
export const THEME_KEY = 'theme';
export const STATE_EXPIRY_MS = 1000 * 60 * 60; // 1 hour
