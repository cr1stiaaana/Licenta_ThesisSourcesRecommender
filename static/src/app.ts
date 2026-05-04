/**
 * Thesis Sources Recommender — Main Application (TypeScript)
 * 
 * Handles:
 * - Language toggle (RO / EN)
 * - Form submission → POST /recommend
 * - Rendering article and web-resource cards
 * - Quality-warning badges
 * - Star rating controls
 * - Authentication
 * - Saved items
 */

import type {
  FeedbackQueryResult,
  RecommendationItem,
  UserInfo,
  Language,
  Theme,
  AppState,
  QueryData,
  Article,
  WebResource,
  I18nStrings,
  I18nDictionary
} from './types.js';

import {
  fetchRecommendations,
  submitFeedback,
  getFeedback,
  getCurrentUser,
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  getSavedItems as apiGetSavedItems,
  saveItem as apiSaveItem,
  unsaveItem as apiUnsaveItem,
  isItemSaved as apiIsItemSaved
} from './api.js';

import {
  SESSION_STORAGE_KEY,
  STATE_KEY,
  SAVED_ITEMS_KEY,
  THEME_KEY,
  ITEMS_PER_PAGE,
  STATE_EXPIRY_MS
} from './types.js';

/* ── Session ID ─────────────────────────────────────────────── */

const SESSION_ID: string = (() => {
  let id = sessionStorage.getItem(SESSION_STORAGE_KEY);
  if (!id) {
    id = crypto.randomUUID
      ? crypto.randomUUID()
      : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
          const r = (Math.random() * 16) | 0;
          return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
        });
    sessionStorage.setItem(SESSION_STORAGE_KEY, id);
  }
  return id;
})();

/* ── Application State ──────────────────────────────────────── */

let currentQuery = '';
let currentQueryData: QueryData | null = null;
let allArticles: Article[] = [];
let allWebResources: WebResource[] = [];
let displayedArticles = 0;
let displayedWebResources = 0;
let hasMoreArticles = true;
let hasMoreWebResources = true;
let currentUser: UserInfo | null = null;

/* ── i18n strings ───────────────────────────────────────────── */

const STRINGS: I18nDictionary = {
  ro: {
    page_title: 'Thesis Sources Recommender',
    site_title: 'Thesis Sources Recommender',
    form_heading: 'Introduceți titlul tezei',
    label_title: 'Titlul tezei',
    label_abstract: 'Rezumat',
    label_keywords: 'Cuvinte cheie',
    optional: '(opțional)',
    placeholder_title: 'ex. Rețele neuronale pentru procesarea limbajului natural',
    placeholder_abstract: 'Introduceți rezumatul tezei...',
    placeholder_keywords: 'ex. machine learning, NLP, transformers',
    hint_title: 'Minim 3 caractere, maxim 500.',
    hint_abstract: 'Adăugați rezumatul pentru rezultate mai precise.',
    hint_keywords: 'Separați cuvintele cheie prin virgulă.',
    btn_submit: 'Caută',
    loading: 'Se încarcă...',
    heading_articles: 'Articole',
    heading_web: 'Resurse Web',
    no_articles: 'Nu au fost găsite articole suficient de relevante.',
    no_web: 'Nu au fost găsite resurse web suficient de relevante.',
    footer_text: 'Thesis Sources Recommender — Universitate',
    badge_article: 'Articol',
    badge_web: 'Web',
    label_score: 'Scor',
    label_authors: 'Autori',
    label_year: 'An',
    label_doi: 'DOI',
    label_url: 'URL',
    label_keywords_card: 'Cuvinte cheie',
    label_usefulness: 'Utilitate',
    rating_submitted: 'Evaluare salvată.',
    rating_error: 'Eroare la salvarea evaluării.',
    avg_rating: 'Medie',
    ratings_count: 'evaluări',
    btn_save: 'Salvează',
    btn_unsave: 'Șterge',
    btn_load_more: 'Încarcă mai multe',
    no_more_articles: 'Nu am mai găsit articole relevante.',
    no_more_web: 'Nu am mai găsit surse relevante.',
    saved_items: 'Salvate',
    no_saved_items: 'Nu aveți articole sau resurse salvate.',
    view_saved: 'Vezi salvate',
    btn_login: 'Autentificare',
    btn_register: 'Înregistrare',
    btn_logout: 'Deconectare',
    login_title: 'Autentificare',
    register_title: 'Înregistrare',
    label_username: 'Nume utilizator',
    label_email: 'Email',
    label_password: 'Parolă',
    no_account: 'Nu ai cont?',
    have_account: 'Ai deja cont?',
    register_link: 'Înregistrează-te',
    login_link: 'Autentifică-te',
    btn_about: 'Despre',
    about_title: 'Despre Sistem',
    about_heading: 'Thesis Sources Recommender',
    about_description: 'Un sistem hibrid de recomandare pentru cercetarea academică care combină căutarea semantică, potrivirea cuvintelor cheie și căutarea web pentru a sugera articole și resurse relevante pentru teza ta.',
    about_features_title: 'Caracteristici Principale',
    about_feature_hybrid: '🔍 Căutare Hibridă: Combină căutarea semantică (FAISS) cu potrivirea cuvintelor cheie (BM25) pentru rezultate precise',
    about_feature_web: '🌐 Integrare Web: Căutare DuckDuckGo și API-uri academice (Semantic Scholar, arXiv) pentru resurse actualizate',
    about_feature_quality: '✓ Verificare Calitate: Detectează și marchează conținut de calitate scăzută sau clickbait',
    about_feature_feedback: '⭐ Sistem de Feedback: Evaluează utilitatea rezultatelor pentru a îmbunătăți recomandările',
    about_feature_bilingual: '🌍 Suport Bilingv: Interfață în română și engleză cu detectare automată a limbii',
    about_how_title: 'Cum Funcționează',
    about_how_step1: '1. Introduceți titlul tezei (obligatoriu) și opțional rezumatul și cuvintele cheie',
    about_how_step2: '2. Sistemul analizează cererea și caută în baza de date locală și pe web',
    about_how_step3: '3. Rezultatele sunt clasificate folosind algoritmi hibrizi și verificate pentru calitate',
    about_how_step4: '4. Navigați prin rezultate, evaluați-le și salvați cele mai relevante pentru referință ulterioară'
  },
  en: {
    page_title: 'Thesis Sources Recommender',
    site_title: 'Thesis Sources Recommender',
    form_heading: 'Enter your thesis title',
    label_title: 'Thesis title',
    label_abstract: 'Abstract',
    label_keywords: 'Keywords',
    optional: '(optional)',
    placeholder_title: 'e.g. Neural networks for natural language processing',
    placeholder_abstract: 'Enter your thesis abstract...',
    placeholder_keywords: 'e.g. machine learning, NLP, transformers',
    hint_title: 'Minimum 3 characters, maximum 500.',
    hint_abstract: 'Adding an abstract improves result accuracy.',
    hint_keywords: 'Separate keywords with commas.',
    btn_submit: 'Search',
    loading: 'Loading...',
    heading_articles: 'Articles',
    heading_web: 'Web Resources',
    no_articles: 'No sufficiently relevant articles were found.',
    no_web: 'No sufficiently relevant web resources were found.',
    footer_text: 'Thesis Sources Recommender — University',
    badge_article: 'Article',
    badge_web: 'Web',
    label_score: 'Score',
    label_authors: 'Authors',
    label_year: 'Year',
    label_doi: 'DOI',
    label_url: 'URL',
    label_keywords_card: 'Keywords',
    label_usefulness: 'Usefulness',
    rating_submitted: 'Rating saved.',
    rating_error: 'Error saving rating.',
    avg_rating: 'Avg',
    ratings_count: 'ratings',
    btn_save: 'Save',
    btn_unsave: 'Remove',
    btn_load_more: 'Load more',
    no_more_articles: 'No more relevant articles found.',
    no_more_web: 'No more relevant sources found.',
    saved_items: 'Saved',
    no_saved_items: 'You have no saved articles or resources.',
    view_saved: 'View saved',
    btn_login: 'Login',
    btn_register: 'Register',
    btn_logout: 'Logout',
    login_title: 'Login',
    register_title: 'Register',
    label_username: 'Username',
    label_email: 'Email',
    label_password: 'Password',
    no_account: "Don't have an account?",
    have_account: 'Already have an account?',
    register_link: 'Register',
    login_link: 'Login',
    btn_about: 'About',
    about_title: 'About the System',
    about_heading: 'Thesis Sources Recommender',
    about_description: 'A hybrid recommendation system for academic research that combines semantic search, keyword matching, and web retrieval to suggest relevant articles and resources for your thesis.',
    about_features_title: 'Key Features',
    about_feature_hybrid: '🔍 Hybrid Search: Combines semantic search (FAISS) with keyword matching (BM25) for precise results',
    about_feature_web: '🌐 Web Integration: DuckDuckGo search and academic APIs (Semantic Scholar, arXiv) for up-to-date resources',
    about_feature_quality: '✓ Quality Verification: Detects and flags low-quality content or clickbait',
    about_feature_feedback: '⭐ Feedback System: Rate result usefulness to improve recommendations',
    about_feature_bilingual: '🌍 Bilingual Support: Romanian and English interface with automatic language detection',
    about_how_title: 'How It Works',
    about_how_step1: '1. Enter your thesis title (required) and optionally abstract and keywords',
    about_how_step2: '2. The system analyzes your request and searches the local database and web',
    about_how_step3: '3. Results are ranked using hybrid algorithms and verified for quality',
    about_how_step4: '4. Browse results, rate them, and save the most relevant ones for later reference'
  }
};

/* ── Language state ─────────────────────────────────────────── */

let currentLang: Language = 'ro';

function t(key: keyof I18nStrings): string {
  return (STRINGS[currentLang] || STRINGS.ro)[key] || key;
}

/* ── DOM references ─────────────────────────────────────────── */

const langToggleBtn = document.getElementById('lang-toggle') as HTMLButtonElement;
const themeToggleBtn = document.getElementById('theme-toggle') as HTMLButtonElement;
const queryForm = document.getElementById('query-form') as HTMLFormElement;
const titleInput = document.getElementById('title-input') as HTMLInputElement;
const abstractInput = document.getElementById('abstract-input') as HTMLTextAreaElement;
const keywordsInput = document.getElementById('keywords-input') as HTMLInputElement;
const submitBtn = document.getElementById('submit-btn') as HTMLButtonElement;
const loadingSpinner = document.getElementById('loading-spinner') as HTMLElement;
const errorContainer = document.getElementById('error-container') as HTMLElement;
const errorMessage = document.getElementById('error-message') as HTMLElement;
const noticesContainer = document.getElementById('notices-container') as HTMLElement;
const resultsWrapper = document.getElementById('results-wrapper') as HTMLElement;
const articlesList = document.getElementById('articles-list') as HTMLElement;
const articlesEmpty = document.getElementById('articles-empty') as HTMLElement;
const articlesLoadMore = document.getElementById('articles-load-more') as HTMLButtonElement;
const webList = document.getElementById('web-list') as HTMLElement;
const webEmpty = document.getElementById('web-empty') as HTMLElement;
const webLoadMore = document.getElementById('web-load-more') as HTMLButtonElement;
const savedBtn = document.getElementById('saved-btn') as HTMLButtonElement;
const savedModal = document.getElementById('saved-modal') as HTMLElement;
const savedModalClose = document.getElementById('saved-modal-close') as HTMLButtonElement;
const savedList = document.getElementById('saved-list') as HTMLElement;
const tabArticles = document.getElementById('tab-articles') as HTMLButtonElement;
const tabWeb = document.getElementById('tab-web') as HTMLButtonElement;
const panelArticles = document.getElementById('panel-articles') as HTMLElement;
const panelWeb = document.getElementById('panel-web') as HTMLElement;
const articlesCount = document.getElementById('articles-count') as HTMLElement;
const webCount = document.getElementById('web-count') as HTMLElement;

/* ── State Management ───────────────────────────────────────── */

function saveState(): void {
  try {
    const state: AppState = {
      currentQuery,
      currentQueryData,
      allArticles,
      allWebResources,
      displayedArticles,
      displayedWebResources,
      hasMoreArticles,
      hasMoreWebResources,
      currentLang,
      timestamp: Date.now()
    };
    sessionStorage.setItem(STATE_KEY, JSON.stringify(state));
  } catch (err) {
    console.warn('Failed to save state:', err);
  }
}

function loadState(): AppState | null {
  try {
    const saved = sessionStorage.getItem(STATE_KEY);
    if (!saved) return null;

    const state: AppState = JSON.parse(saved);
    const now = Date.now();

    if (now - state.timestamp > STATE_EXPIRY_MS) {
      sessionStorage.removeItem(STATE_KEY);
      return null;
    }

    return state;
  } catch (err) {
    console.warn('Failed to load state:', err);
    return null;
  }
}

function clearState(): void {
  sessionStorage.removeItem(STATE_KEY);
}

function updateTabCounts(): void {
  if (articlesCount) {
    articlesCount.textContent = allArticles.length > 0 ? `(${allArticles.length})` : '';
  }
  if (webCount) {
    webCount.textContent = allWebResources.length > 0 ? `(${allWebResources.length})` : '';
  }
}

/* ── Utility Functions ──────────────────────────────────────── */

function showError(msg: string): void {
  errorMessage.textContent = msg;
  errorContainer.hidden = false;
}

function hideError(): void {
  errorContainer.hidden = true;
  errorMessage.textContent = '';
}

function showLoading(): void {
  loadingSpinner.hidden = false;
  const spinnerLabel = loadingSpinner.querySelector('.spinner-label');
  if (spinnerLabel) spinnerLabel.textContent = t('loading');
}

function hideLoading(): void {
  loadingSpinner.hidden = true;
}

function setSubmitDisabled(disabled: boolean): void {
  submitBtn.disabled = disabled;
}

function showNotices(notices: string[]): void {
  noticesContainer.innerHTML = '';
  if (!notices || notices.length === 0) {
    noticesContainer.hidden = true;
    return;
  }
  notices.forEach((msg) => {
    const div = document.createElement('div');
    div.className = 'notice-item';
    div.setAttribute('role', 'status');
    div.textContent = msg;
    noticesContainer.appendChild(div);
  });
  noticesContainer.hidden = false;
}

function makeScoreBadge(score: number, label?: string): HTMLSpanElement {
  const pct = Math.round(score * 100);
  const span = document.createElement('span');
  span.className = 'badge badge-score';
  if (pct >= 70) span.classList.add('badge-score-high');
  else if (pct >= 40) span.classList.add('badge-score-mid');
  else span.classList.add('badge-score-low');
  span.textContent = (label ? label + ': ' : '') + pct + '%';
  span.setAttribute('aria-label', (label || t('label_score')) + ': ' + pct + '%');
  return span;
}

function makeTypeBadge(type: 'article' | 'web'): HTMLSpanElement {
  const span = document.createElement('span');
  span.className = 'badge ' + (type === 'article' ? 'badge-article' : 'badge-web');
  span.textContent = type === 'article' ? t('badge_article') : t('badge_web');
  return span;
}

function makeWarningBadge(warningText: string): HTMLSpanElement {
  const span = document.createElement('span');
  span.className = 'badge badge-warning';
  span.setAttribute('role', 'img');
  span.setAttribute('aria-label', warningText);
  span.textContent = warningText;
  return span;
}

function deriveItemId(item: RecommendationItem): string {
  if ('doi' in item && item.doi) return 'doi:' + item.doi;
  if (item.url) return 'url:' + item.url;
  const title = (item.title || '').trim().toLowerCase();
  return 'title:' + simpleHash(title);
}

function simpleHash(str: string): string {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return (hash >>> 0).toString(16);
}

/* ── Language Toggle ────────────────────────────────────────── */

function updateLanguageUI(): void {
  const langOptions = langToggleBtn.querySelectorAll('.lang-option');
  langOptions.forEach((option) => {
    const lang = option.getAttribute('data-lang') as Language;
    if (lang === currentLang) {
      option.classList.add('active');
    } else {
      option.classList.remove('active');
    }
  });
}

function applyI18n(): void {
  document.documentElement.lang = currentLang;
  document.title = t('page_title');

  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n') as keyof I18nStrings;
    el.textContent = t(key);
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    const key = el.getAttribute('data-i18n-placeholder') as keyof I18nStrings;
    (el as HTMLInputElement | HTMLTextAreaElement).placeholder = t(key);
  });
}

langToggleBtn.addEventListener('click', () => {
  currentLang = currentLang === 'ro' ? 'en' : 'ro';
  updateLanguageUI();
  applyI18n();
  saveState();
});

/* ── Theme Toggle ───────────────────────────────────────────── */

let currentTheme: Theme = (localStorage.getItem(THEME_KEY) as Theme) || 'light';

function applyTheme(theme: Theme): void {
  currentTheme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);

  const themeIcon = themeToggleBtn.querySelector('.theme-icon');
  if (themeIcon) {
    themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
  }
}

themeToggleBtn.addEventListener('click', () => {
  const newTheme: Theme = currentTheme === 'dark' ? 'light' : 'dark';
  applyTheme(newTheme);
});

applyTheme(currentTheme);

/* ── Initialize ─────────────────────────────────────────────── */

updateLanguageUI();
applyI18n();

// Check auth status on load
getCurrentUser().then((user) => {
  currentUser = user;
  updateAuthUI();
});

// Restore state on load
window.addEventListener('DOMContentLoaded', () => {
  const state = loadState();
  if (state) {
    console.log('Restoring state from sessionStorage');
    // Restore state logic here...
  }
});

/* ── Export for debugging ───────────────────────────────────── */

declare global {
  interface Window {
    app: {
      currentLang: Language;
      currentUser: UserInfo | null;
      SESSION_ID: string;
    };
  }
}

window.app = {
  currentLang,
  currentUser,
  SESSION_ID
};

/* ── Star Rating Control ────────────────────────────────────── */

async function fetchExistingRating(
  itemId: string,
  aggregateEl: HTMLElement
): Promise<number> {
  try {
    const data = await getFeedback(itemId, SESSION_ID);
    updateAggregateDisplay(aggregateEl, data);
    return data.user_rating || 0;
  } catch {
    return 0;
  }
}

async function submitRating(
  itemId: string,
  query: string,
  rating: number,
  aggregateEl: HTMLElement
): Promise<void> {
  try {
    await submitFeedback({
      item_id: itemId,
      query: query,
      rating: rating,
      session_id: SESSION_ID
    });
    
    const data = await getFeedback(itemId, SESSION_ID);
    updateAggregateDisplay(aggregateEl, data);
  } catch (err) {
    console.warn('Feedback error:', err);
  }
}

function updateAggregateDisplay(
  aggregateEl: HTMLElement,
  data: FeedbackQueryResult
): void {
  const count = data.rating_count || 0;
  if (count === 0) {
    aggregateEl.hidden = true;
    return;
  }
  const parts: string[] = [];
  if (data.average_rating != null) {
    parts.push(t('avg_rating') + ': ' + Number(data.average_rating).toFixed(1) + ' ★');
  }
  parts.push('(' + count + ' ' + t('ratings_count') + ')');
  aggregateEl.textContent = parts.join(' ');
  aggregateEl.hidden = false;
}

function buildRatingControl(
  card: HTMLElement,
  itemId: string,
  query: string
): HTMLElement {
  const wrapper = document.createElement('div');
  wrapper.className = 'rating-control';
  wrapper.setAttribute('aria-label', t('label_usefulness'));

  const label = document.createElement('span');
  label.className = 'rating-label';
  label.textContent = t('label_usefulness') + ':';
  wrapper.appendChild(label);

  const starsEl = document.createElement('span');
  starsEl.className = 'stars';
  starsEl.setAttribute('role', 'group');
  starsEl.setAttribute('aria-label', t('label_usefulness'));

  let currentRating = 0;
  const starButtons: HTMLButtonElement[] = [];

  function renderStars(highlightUpTo: number): void {
    starButtons.forEach((btn, idx) => {
      const filled = idx < highlightUpTo;
      btn.classList.toggle('filled', filled);
      btn.textContent = filled ? '★' : '☆';
    });
  }

  for (let i = 1; i <= 5; i++) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'star';
    btn.textContent = '☆';
    btn.setAttribute('aria-label', i + ' ' + (i === 1 ? 'stea' : 'stele'));
    btn.dataset.value = String(i);

    btn.addEventListener('mouseenter', () => renderStars(i));
    btn.addEventListener('mouseleave', () => renderStars(currentRating));
    btn.addEventListener('focus', () => renderStars(i));
    btn.addEventListener('blur', () => renderStars(currentRating));

    btn.addEventListener('click', async () => {
      currentRating = i;
      renderStars(currentRating);
      await submitRating(itemId, query, i, aggregateEl);
    });

    starsEl.appendChild(btn);
    starButtons.push(btn);
  }

  wrapper.appendChild(starsEl);

  const aggregateEl = document.createElement('span');
  aggregateEl.className = 'rating-aggregate';
  aggregateEl.hidden = true;
  wrapper.appendChild(aggregateEl);

  card.appendChild(wrapper);

  fetchExistingRating(itemId, aggregateEl).then((rating) => {
    currentRating = rating;
    renderStars(currentRating);
  });

  return wrapper;
}

/* ── Save Button ────────────────────────────────────────────── */

function buildSaveButton(card: HTMLElement, item: RecommendationItem): HTMLButtonElement {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'btn-save';

  async function updateButton(): Promise<void> {
    const saved = await apiIsItemSaved(deriveItemId(item));
    btn.textContent = saved ? t('btn_unsave') : t('btn_save');
    btn.classList.toggle('saved', saved);
  }

  updateButton();

  btn.addEventListener('click', async () => {
    const itemId = deriveItemId(item);
    const saved = await apiIsItemSaved(itemId);
    if (saved) {
      await apiUnsaveItem(itemId);
    } else {
      await apiSaveItem(itemId, item);
    }
    await updateButton();
  });

  card.appendChild(btn);
  return btn;
}

/* ── Card Rendering ─────────────────────────────────────────── */

function buildArticleCard(article: Article): HTMLElement {
  const card = document.createElement('article');
  card.className = 'result-card';
  card.setAttribute('role', 'listitem');

  const header = document.createElement('div');
  header.className = 'card-header';

  const titleEl = document.createElement('h3');
  titleEl.className = 'card-title';

  const link = article.doi
    ? 'https://doi.org/' + article.doi
    : article.url || null;

  if (link) {
    const a = document.createElement('a');
    a.href = link;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = article.title || '(no title)';
    titleEl.appendChild(a);
  } else {
    titleEl.textContent = article.title || '(no title)';
  }

  header.appendChild(titleEl);
  card.appendChild(header);

  const badges = document.createElement('div');
  badges.className = 'card-badges';
  badges.appendChild(makeTypeBadge('article'));
  if (article.score != null) {
    badges.appendChild(makeScoreBadge(article.score));
  }
  if (article.quality_warning) {
    badges.appendChild(makeWarningBadge(article.quality_warning));
  }
  card.appendChild(badges);

  const meta = document.createElement('div');
  meta.className = 'card-meta';

  if (article.authors && article.authors.length > 0) {
    const authorsSpan = document.createElement('span');
    authorsSpan.textContent = article.authors.join(', ');
    meta.appendChild(authorsSpan);
  }

  if (article.year) {
    if (meta.children.length > 0) {
      const sep = document.createElement('span');
      sep.className = 'card-meta-sep';
      sep.setAttribute('aria-hidden', 'true');
      sep.textContent = '·';
      meta.appendChild(sep);
    }
    const yearSpan = document.createElement('span');
    yearSpan.textContent = String(article.year);
    meta.appendChild(yearSpan);
  }

  if (meta.children.length > 0) {
    card.appendChild(meta);
  }

  if (article.abstract_snippet) {
    const snippet = document.createElement('p');
    snippet.className = 'card-snippet';
    snippet.textContent = article.abstract_snippet;
    card.appendChild(snippet);
  }

  if (link) {
    const linkEl = document.createElement('div');
    linkEl.className = 'card-meta';
    const a = document.createElement('a');
    a.href = link;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.className = 'card-link';
    a.textContent = article.doi ? (t('label_doi') + ': ' + article.doi) : link;
    linkEl.appendChild(a);
    card.appendChild(linkEl);
  }

  const itemId = deriveItemId(article);
  buildRatingControl(card, itemId, currentQuery);
  buildSaveButton(card, article);

  return card;
}

function buildWebCard(resource: WebResource): HTMLElement {
  const card = document.createElement('article');
  card.className = 'result-card';
  card.setAttribute('role', 'listitem');

  const header = document.createElement('div');
  header.className = 'card-header';

  const titleEl = document.createElement('h3');
  titleEl.className = 'card-title';

  if (resource.url) {
    const a = document.createElement('a');
    a.href = resource.url;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = resource.title || resource.url;
    titleEl.appendChild(a);
  } else {
    titleEl.textContent = resource.title || '(no title)';
  }

  header.appendChild(titleEl);
  card.appendChild(header);

  const badges = document.createElement('div');
  badges.className = 'card-badges';
  badges.appendChild(makeTypeBadge('web'));
  if (resource.web_score != null) {
    badges.appendChild(makeScoreBadge(resource.web_score));
  }
  if (resource.quality_warning) {
    badges.appendChild(makeWarningBadge(resource.quality_warning));
  }
  card.appendChild(badges);

  if (resource.url) {
    const urlRow = document.createElement('div');
    urlRow.className = 'card-meta';
    const a = document.createElement('a');
    a.href = resource.url;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.className = 'card-link';
    a.textContent = resource.url;
    urlRow.appendChild(a);
    card.appendChild(urlRow);
  }

  if (resource.snippet) {
    const snippet = document.createElement('p');
    snippet.className = 'card-snippet';
    snippet.textContent = resource.snippet;
    card.appendChild(snippet);
  }

  if (resource.keywords && resource.keywords.length > 0) {
    const kwContainer = document.createElement('div');
    kwContainer.className = 'card-keywords';
    kwContainer.setAttribute('aria-label', t('label_keywords_card'));
    resource.keywords.forEach((kw) => {
      const tag = document.createElement('span');
      tag.className = 'keyword-tag';
      tag.textContent = kw;
      kwContainer.appendChild(tag);
    });
    card.appendChild(kwContainer);
  }

  const itemId = deriveItemId(resource);
  buildRatingControl(card, itemId, currentQuery);
  buildSaveButton(card, resource);

  return card;
}

/* ── Tab Switching ──────────────────────────────────────────── */

function setupTabSwitching(): void {
  if (!tabArticles || !tabWeb || !panelArticles || !panelWeb) {
    console.error('Tab elements not found');
    return;
  }

  tabArticles.addEventListener('click', () => {
    tabArticles.classList.add('active');
    tabArticles.setAttribute('aria-selected', 'true');
    tabWeb.classList.remove('active');
    tabWeb.setAttribute('aria-selected', 'false');
    panelArticles.hidden = false;
    panelWeb.hidden = true;
  });

  tabWeb.addEventListener('click', () => {
    tabWeb.classList.add('active');
    tabWeb.setAttribute('aria-selected', 'true');
    tabArticles.classList.remove('active');
    tabArticles.setAttribute('aria-selected', 'false');
    panelWeb.hidden = false;
    panelArticles.hidden = true;
  });
}

setupTabSwitching();

/* ── About Modal ────────────────────────────────────────────── */

const aboutBtn = document.getElementById('about-btn') as HTMLButtonElement | null;
const aboutModal = document.getElementById('about-modal') as HTMLElement | null;
const aboutModalClose = document.getElementById('about-modal-close') as HTMLButtonElement | null;

if (aboutBtn && aboutModal && aboutModalClose) {
  aboutBtn.addEventListener('click', () => {
    aboutModal.hidden = false;
  });

  aboutModalClose.addEventListener('click', () => {
    aboutModal.hidden = true;
  });

  aboutModal.addEventListener('click', (e) => {
    if (e.target === aboutModal) {
      aboutModal.hidden = true;
    }
  });
}

/* ── Saved Items Modal ──────────────────────────────────────── */

if (savedBtn && savedModal && savedModalClose && savedList) {
  savedBtn.addEventListener('click', async () => {
    await renderSavedItems();
    savedModal.hidden = false;
  });

  savedModalClose.addEventListener('click', () => {
    savedModal.hidden = true;
  });

  savedModal.addEventListener('click', (e) => {
    if (e.target === savedModal) {
      savedModal.hidden = true;
    }
  });
}

async function renderSavedItems(): Promise<void> {
  if (!savedList) return;

  savedList.innerHTML = '';
  const saved = await apiGetSavedItems();

  if (saved.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'saved-empty';
    empty.textContent = t('no_saved_items');
    savedList.appendChild(empty);
    return;
  }

  saved.forEach((item) => {
    const card = item.resource_type === 'article' ? buildArticleCard(item as Article) : buildWebCard(item as WebResource);
    savedList.appendChild(card);
  });
}

/* ── Form Submission ────────────────────────────────────────── */

async function submitQuery(offset: number = 0): Promise<void> {
  const title = titleInput.value.trim();
  if (!title || title.length < 3) {
    showError(t('hint_title'));
    titleInput.focus();
    return;
  }

  const abstractVal = abstractInput.value.trim() || undefined;
  const keywordsRaw = keywordsInput.value.trim();
  const keywords = keywordsRaw
    ? keywordsRaw.split(',').map((k) => k.trim()).filter(Boolean)
    : undefined;

  currentQuery = title;
  currentQueryData = { title, abstract: abstractVal || null, keywords: keywords || [] };

  if (offset === 0) {
    clearState();
    allArticles = [];
    allWebResources = [];
    displayedArticles = 0;
    displayedWebResources = 0;
    hasMoreArticles = true;
    hasMoreWebResources = true;

    hideError();
    showNotices([]);
    resultsWrapper.hidden = true;
    articlesList.innerHTML = '';
    webList.innerHTML = '';
    articlesEmpty.hidden = true;
    webEmpty.hidden = true;
    articlesLoadMore.hidden = true;
    webLoadMore.hidden = true;
  }

  setSubmitDisabled(true);
  showLoading();

  try {
    const data = await fetchRecommendations({
      title,
      abstract: abstractVal,
      keywords,
      offset
    });

    if (offset === 0 && data.notices && data.notices.length > 0) {
      showNotices(data.notices);
    }

    if (offset === 0 && data.query_language && data.query_language !== currentLang) {
      currentLang = data.query_language === 'ro' ? 'ro' : 'en';
      updateLanguageUI();
      applyI18n();
    }

    const newArticles = data.articles || [];
    const newWebResources = data.web_resources || [];

    if (newArticles.length < ITEMS_PER_PAGE) {
      hasMoreArticles = false;
    }
    if (newWebResources.length < ITEMS_PER_PAGE) {
      hasMoreWebResources = false;
    }

    allArticles = allArticles.concat(newArticles);
    allWebResources = allWebResources.concat(newWebResources);

    newArticles.forEach((article) => {
      articlesList.appendChild(buildArticleCard(article));
    });
    displayedArticles += newArticles.length;

    newWebResources.forEach((resource) => {
      webList.appendChild(buildWebCard(resource));
    });
    displayedWebResources += newWebResources.length;

    if (displayedArticles === 0) {
      articlesEmpty.textContent = t('no_articles');
      articlesEmpty.hidden = false;
    } else {
      articlesEmpty.hidden = true;
    }

    if (displayedWebResources === 0) {
      webEmpty.textContent = t('no_web');
      webEmpty.hidden = false;
    } else {
      webEmpty.hidden = true;
    }

    articlesLoadMore.hidden = !hasMoreArticles || newArticles.length === 0;
    webLoadMore.hidden = !hasMoreWebResources || newWebResources.length === 0;

    updateTabCounts();
    resultsWrapper.hidden = false;
    saveState();
  } catch (err) {
    showError((err as Error).message || 'Network error');
  } finally {
    hideLoading();
    setSubmitDisabled(false);
  }
}

async function loadMoreArticles(): Promise<void> {
  if (!currentQueryData) return;

  // Disable button and show loading state
  articlesLoadMore.disabled = true;
  articlesLoadMore.textContent = t('loading');
  setSubmitDisabled(true);
  showLoading();

  try {
    const data = await fetchRecommendations({
      title: currentQueryData.title,
      abstract: currentQueryData.abstract || undefined,
      keywords: currentQueryData.keywords,
      offset: displayedArticles,
      type: 'articles'
    });

    const newArticles = data.articles || [];

    if (newArticles.length === 0) {
      hasMoreArticles = false;
      articlesLoadMore.hidden = true;

      const noMoreMsg = document.createElement('p');
      noMoreMsg.className = 'no-more-message';
      noMoreMsg.textContent = t('no_more_articles');
      articlesList.appendChild(noMoreMsg);

      saveState();
      return;
    }

    if (newArticles.length < ITEMS_PER_PAGE) {
      hasMoreArticles = false;
    }

    allArticles = allArticles.concat(newArticles);

    newArticles.forEach((article) => {
      articlesList.appendChild(buildArticleCard(article));
    });
    displayedArticles += newArticles.length;

    articlesLoadMore.hidden = !hasMoreArticles || newArticles.length === 0;
    updateTabCounts();
    saveState();
  } catch (err) {
    showError((err as Error).message || 'Network error');
  } finally {
    hideLoading();
    setSubmitDisabled(false);
    // Restore button state
    articlesLoadMore.disabled = false;
    articlesLoadMore.textContent = t('btn_load_more');
  }
}

async function loadMoreWebResources(): Promise<void> {
  if (!currentQueryData) return;

  // Disable button and show loading state
  webLoadMore.disabled = true;
  webLoadMore.textContent = t('loading');
  setSubmitDisabled(true);
  showLoading();

  try {
    const data = await fetchRecommendations({
      title: currentQueryData.title,
      abstract: currentQueryData.abstract || undefined,
      keywords: currentQueryData.keywords,
      offset: displayedWebResources,
      type: 'web'
    });

    const newWebResources = data.web_resources || [];

    if (newWebResources.length === 0) {
      hasMoreWebResources = false;
      webLoadMore.hidden = true;

      const noMoreMsg = document.createElement('p');
      noMoreMsg.className = 'no-more-message';
      noMoreMsg.textContent = t('no_more_web');
      webList.appendChild(noMoreMsg);

      saveState();
      return;
    }

    if (newWebResources.length < ITEMS_PER_PAGE) {
      hasMoreWebResources = false;
    }

    allWebResources = allWebResources.concat(newWebResources);

    newWebResources.forEach((resource) => {
      webList.appendChild(buildWebCard(resource));
    });
    displayedWebResources += newWebResources.length;

    webLoadMore.hidden = !hasMoreWebResources || newWebResources.length === 0;
    updateTabCounts();
    saveState();
  } catch (err) {
    showError((err as Error).message || 'Network error');
  } finally {
    hideLoading();
    setSubmitDisabled(false);
    // Restore button state
    webLoadMore.disabled = false;
    webLoadMore.textContent = t('btn_load_more');
  }
}

queryForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  await submitQuery();
});

if (articlesLoadMore) {
  articlesLoadMore.addEventListener('click', async () => {
    await loadMoreArticles();
  });
}

if (webLoadMore) {
  webLoadMore.addEventListener('click', async () => {
    await loadMoreWebResources();
  });
}

/* ── Authentication ─────────────────────────────────────────── */

const authBtn = document.getElementById('auth-btn') as HTMLButtonElement | null;
const authModal = document.getElementById('auth-modal') as HTMLElement | null;
const authModalClose = document.getElementById('auth-modal-close') as HTMLButtonElement | null;
const loginForm = document.getElementById('login-form') as HTMLFormElement | null;
const registerForm = document.getElementById('register-form') as HTMLFormElement | null;
const showRegisterLink = document.getElementById('show-register') as HTMLAnchorElement | null;
const showLoginLink = document.getElementById('show-login') as HTMLAnchorElement | null;
const logoutBtn = document.getElementById('logout-btn') as HTMLButtonElement | null;

function updateAuthUI(): void {
  const authBtnEl = document.getElementById('auth-btn');
  const userInfo = document.getElementById('user-info');
  const username = document.getElementById('username-display');

  if (currentUser) {
    if (authBtnEl) authBtnEl.hidden = true;
    if (userInfo) {
      userInfo.hidden = false;
      if (username) username.textContent = currentUser.username;
    }
  } else {
    if (authBtnEl) authBtnEl.hidden = false;
    if (userInfo) userInfo.hidden = true;
  }
}

function showLoginForm(): void {
  if (loginForm) loginForm.hidden = false;
  if (registerForm) registerForm.hidden = true;
}

function showRegisterForm(): void {
  if (loginForm) loginForm.hidden = true;
  if (registerForm) registerForm.hidden = false;
}

if (authBtn && authModal) {
  authBtn.addEventListener('click', () => {
    authModal.hidden = false;
    showLoginForm();
  });
}

if (authModalClose && authModal) {
  authModalClose.addEventListener('click', () => {
    authModal.hidden = true;
  });
}

if (authModal) {
  authModal.addEventListener('click', (e) => {
    if (e.target === authModal) {
      authModal.hidden = true;
    }
  });
}

if (showRegisterLink) {
  showRegisterLink.addEventListener('click', (e) => {
    e.preventDefault();
    showRegisterForm();
  });
}

if (showLoginLink) {
  showLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    showLoginForm();
  });
}

if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const usernameInput = document.getElementById('login-username') as HTMLInputElement;
    const passwordInput = document.getElementById('login-password') as HTMLInputElement;
    const errorEl = document.getElementById('login-error');

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    try {
      const data = await apiLogin(username, password);
      currentUser = data.user;
      updateAuthUI();
      if (authModal) authModal.hidden = true;
      loginForm.reset();
      if (errorEl) errorEl.textContent = '';
      await migrateSavedItems();
    } catch (err) {
      if (errorEl) errorEl.textContent = (err as Error).message || 'Login failed';
    }
  });
}

if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const usernameInput = document.getElementById('register-username') as HTMLInputElement;
    const emailInput = document.getElementById('register-email') as HTMLInputElement;
    const passwordInput = document.getElementById('register-password') as HTMLInputElement;
    const errorEl = document.getElementById('register-error');

    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    try {
      const data = await apiRegister(username, email, password);
      currentUser = data.user;
      updateAuthUI();
      if (authModal) authModal.hidden = true;
      registerForm.reset();
      if (errorEl) errorEl.textContent = '';
      await migrateSavedItems();
    } catch (err) {
      if (errorEl) errorEl.textContent = (err as Error).message || 'Registration failed';
    }
  });
}

if (logoutBtn) {
  logoutBtn.addEventListener('click', async () => {
    try {
      await apiLogout();
      currentUser = null;
      updateAuthUI();
    } catch (err) {
      console.warn('Logout error:', err);
    }
  });
}

async function migrateSavedItems(): Promise<void> {
  try {
    const json = localStorage.getItem(SAVED_ITEMS_KEY);
    if (!json) return;

    const localItems: RecommendationItem[] = JSON.parse(json);
    if (localItems.length === 0) return;

    for (const item of localItems) {
      await apiSaveItem(deriveItemId(item), item);
    }

    localStorage.removeItem(SAVED_ITEMS_KEY);
  } catch (err) {
    console.warn('Failed to migrate saved items:', err);
  }
}

/* ── State Restoration ──────────────────────────────────────── */

window.addEventListener('DOMContentLoaded', () => {
  const state = loadState();
  if (state) {
    console.log('Restoring state from sessionStorage');

    currentQuery = state.currentQuery;
    currentQueryData = state.currentQueryData;
    allArticles = state.allArticles || [];
    allWebResources = state.allWebResources || [];
    displayedArticles = state.displayedArticles || 0;
    displayedWebResources = state.displayedWebResources || 0;
    hasMoreArticles = state.hasMoreArticles !== false;
    hasMoreWebResources = state.hasMoreWebResources !== false;

    if (state.currentLang && state.currentLang !== currentLang) {
      currentLang = state.currentLang;
      updateLanguageUI();
      applyI18n();
    }

    if (currentQueryData) {
      titleInput.value = currentQueryData.title || '';
      abstractInput.value = currentQueryData.abstract || '';
      keywordsInput.value = (currentQueryData.keywords || []).join(', ');
    }

    if (allArticles.length > 0 || allWebResources.length > 0) {
      articlesList.innerHTML = '';
      webList.innerHTML = '';

      allArticles.forEach((article) => {
        articlesList.appendChild(buildArticleCard(article));
      });

      allWebResources.forEach((resource) => {
        webList.appendChild(buildWebCard(resource));
      });

      if (displayedArticles === 0) {
        articlesEmpty.textContent = t('no_articles');
        articlesEmpty.hidden = false;
      } else {
        articlesEmpty.hidden = true;
      }

      if (displayedWebResources === 0) {
        webEmpty.textContent = t('no_web');
        webEmpty.hidden = false;
      } else {
        webEmpty.hidden = true;
      }

      articlesLoadMore.hidden = !hasMoreArticles;
      webLoadMore.hidden = !hasMoreWebResources;

      updateTabCounts();
      resultsWrapper.hidden = false;
    }
  }
});
