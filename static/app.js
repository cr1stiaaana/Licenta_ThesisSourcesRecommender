/**
 * Thesis Sources Recommender — app.js
 *
 * Plain vanilla JS. No framework, no build step.
 * Handles:
 *   - Language toggle (RO / EN)
 *   - Form submission → POST /recommend
 *   - Rendering article and web-resource cards
 *   - Quality-warning badges
 *   - Star rating controls (POST /feedback, GET /feedback/{id})
 */

/* ── Session ID ─────────────────────────────────────────────── */
// Generate once per page load; persist in sessionStorage so it
// survives soft navigations but resets on a new tab/window.
const SESSION_ID = (() => {
  const key = 'thesis_recommender_session_id';
  let id = sessionStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID
      ? crypto.randomUUID()
      : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
          const r = (Math.random() * 16) | 0;
          return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
        });
    sessionStorage.setItem(key, id);
  }
  return id;
})();

/* ── Current query (title) ──────────────────────────────────── */
// Stored after each successful submission so feedback requests
// can include the query text.
let currentQuery = '';
let currentQueryData = null; // Store full query data for "load more"
let allArticles = []; // All fetched articles
let allWebResources = []; // All fetched web resources
let displayedArticles = 0;
let displayedWebResources = 0;
const ITEMS_PER_PAGE = 5; // Show 5 items at a time
let hasMoreArticles = true; // Track if there are more articles to load
let hasMoreWebResources = true; // Track if there are more web resources to load

// Session storage keys
const STATE_KEY = 'thesis_recommender_state';

function saveState() {
  try {
    const state = {
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

function loadState() {
  try {
    const saved = sessionStorage.getItem(STATE_KEY);
    if (!saved) return null;
    
    const state = JSON.parse(saved);
    const now = Date.now();
    
    // State expires after 1 hour
    if (now - state.timestamp > 1000 * 60 * 60) {
      sessionStorage.removeItem(STATE_KEY);
      return null;
    }
    
    return state;
  } catch (err) {
    console.warn('Failed to load state:', err);
    return null;
  }
}

function clearState() {
  sessionStorage.removeItem(STATE_KEY);
}

/* ── i18n strings ───────────────────────────────────────────── */
const STRINGS = {
  ro: {
    page_title:        'Thesis Sources Recommender',
    site_title:        'Thesis Sources Recommender',
    form_heading:      'Introduceți titlul tezei',
    label_title:       'Titlul tezei',
    label_abstract:    'Rezumat',
    label_keywords:    'Cuvinte cheie',
    optional:          '(opțional)',
    placeholder_title: 'ex. Rețele neuronale pentru procesarea limbajului natural',
    placeholder_abstract: 'Introduceți rezumatul tezei...',
    placeholder_keywords: 'ex. machine learning, NLP, transformers',
    hint_title:        'Minim 3 caractere, maxim 500.',
    hint_abstract:     'Adăugați rezumatul pentru rezultate mai precise.',
    hint_keywords:     'Separați cuvintele cheie prin virgulă.',
    btn_submit:        'Caută',
    loading:           'Se încarcă...',
    heading_articles:  'Articole',
    heading_web:       'Resurse Web',
    no_articles:       'Nu au fost găsite articole suficient de relevante.',
    no_web:            'Nu au fost găsite resurse web suficient de relevante.',
    footer_text:       'Thesis Sources Recommender — Universitate',
    badge_article:     'Articol',
    badge_web:         'Web',
    label_score:       'Scor',
    label_authors:     'Autori',
    label_year:        'An',
    label_doi:         'DOI',
    label_url:         'URL',
    label_keywords_card: 'Cuvinte cheie',
    label_usefulness:  'Utilitate',
    rating_submitted:  'Evaluare salvată.',
    rating_error:      'Eroare la salvarea evaluării.',
    avg_rating:        'Medie',
    ratings_count:     'evaluări',
    btn_save:          'Salvează',
    btn_unsave:        'Șterge',
    btn_load_more:     'Încarcă mai multe',
    saved_items:       'Salvate',
    no_saved_items:    'Nu aveți articole sau resurse salvate.',
    view_saved:        'Vezi salvate',
    btn_login:         'Autentificare',
    btn_register:      'Înregistrare',
    btn_logout:        'Deconectare',
    login_title:       'Autentificare',
    register_title:    'Înregistrare',
    label_username:    'Nume utilizator',
    label_email:       'Email',
    label_password:    'Parolă',
    no_account:        'Nu ai cont?',
    have_account:      'Ai deja cont?',
    register_link:     'Înregistrează-te',
    login_link:        'Autentifică-te',
  },
  en: {
    page_title:        'Thesis Sources Recommender',
    site_title:        'Thesis Sources Recommender',
    form_heading:      'Enter your thesis title',
    label_title:       'Thesis title',
    label_abstract:    'Abstract',
    label_keywords:    'Keywords',
    optional:          '(optional)',
    placeholder_title: 'e.g. Neural networks for natural language processing',
    placeholder_abstract: 'Enter your thesis abstract...',
    placeholder_keywords: 'e.g. machine learning, NLP, transformers',
    hint_title:        'Minimum 3 characters, maximum 500.',
    hint_abstract:     'Adding an abstract improves result accuracy.',
    hint_keywords:     'Separate keywords with commas.',
    btn_submit:        'Search',
    loading:           'Loading...',
    heading_articles:  'Articles',
    heading_web:       'Web Resources',
    no_articles:       'No sufficiently relevant articles were found.',
    no_web:            'No sufficiently relevant web resources were found.',
    footer_text:       'Thesis Sources Recommender — University',
    badge_article:     'Article',
    badge_web:         'Web',
    label_score:       'Score',
    label_authors:     'Authors',
    label_year:        'Year',
    label_doi:         'DOI',
    label_url:         'URL',
    label_keywords_card: 'Keywords',
    label_usefulness:  'Usefulness',
    rating_submitted:  'Rating saved.',
    rating_error:      'Error saving rating.',
    avg_rating:        'Avg',
    ratings_count:     'ratings',
    btn_save:          'Save',
    btn_unsave:        'Remove',
    btn_load_more:     'Load more',
    saved_items:       'Saved',
    no_saved_items:    'You have no saved articles or resources.',
    view_saved:        'View saved',
    btn_login:         'Login',
    btn_register:      'Register',
    btn_logout:        'Logout',
    login_title:       'Login',
    register_title:    'Register',
    label_username:    'Username',
    label_email:       'Email',
    label_password:    'Password',
    no_account:        'Don\'t have an account?',
    have_account:      'Already have an account?',
    register_link:     'Register',
    login_link:        'Login',
  },
};

/* ── Language state ─────────────────────────────────────────── */
let currentLang = 'ro';

function t(key) {
  return (STRINGS[currentLang] || STRINGS.ro)[key] || key;
}

/* ── DOM references ─────────────────────────────────────────── */
const langToggleBtn    = document.getElementById('lang-toggle');
const themeToggleBtn   = document.getElementById('theme-toggle');
const queryForm        = document.getElementById('query-form');
const titleInput       = document.getElementById('title-input');
const abstractInput    = document.getElementById('abstract-input');
const keywordsInput    = document.getElementById('keywords-input');
const submitBtn        = document.getElementById('submit-btn');
const loadingSpinner   = document.getElementById('loading-spinner');
const errorContainer   = document.getElementById('error-container');
const errorMessage     = document.getElementById('error-message');
const noticesContainer = document.getElementById('notices-container');
const resultsWrapper   = document.getElementById('results-wrapper');
const articlesList     = document.getElementById('articles-list');
const articlesEmpty    = document.getElementById('articles-empty');
const articlesLoadMore = document.getElementById('articles-load-more');
const webList          = document.getElementById('web-list');
const webEmpty         = document.getElementById('web-empty');
const webLoadMore      = document.getElementById('web-load-more');
const savedBtn         = document.getElementById('saved-btn');
const savedModal       = document.getElementById('saved-modal');
const savedModalClose  = document.getElementById('saved-modal-close');
const savedList        = document.getElementById('saved-list');
const tabArticles      = document.getElementById('tab-articles');
const tabWeb           = document.getElementById('tab-web');
const panelArticles    = document.getElementById('panel-articles');
const panelWeb         = document.getElementById('panel-web');
const articlesCount    = document.getElementById('articles-count');
const webCount         = document.getElementById('web-count');

/* ── Authentication state ───────────────────────────────────── */

let currentUser = null; // { id, username, email } or null

async function checkAuthStatus() {
  try {
    const resp = await fetch('/auth/me');
    if (resp.ok) {
      const data = await resp.json();
      currentUser = data.user;
      updateAuthUI();
      return currentUser;
    }
  } catch (err) {
    console.warn('Auth check failed:', err);
  }
  currentUser = null;
  updateAuthUI();
  return null;
}

function updateAuthUI() {
  const authBtn = document.getElementById('auth-btn');
  const userInfo = document.getElementById('user-info');
  const username = document.getElementById('username-display');
  const logoutBtn = document.getElementById('logout-btn');
  
  if (currentUser) {
    // User is logged in
    if (authBtn) authBtn.hidden = true;
    if (userInfo) {
      userInfo.hidden = false;
      if (username) username.textContent = currentUser.username;
    }
  } else {
    // User is not logged in
    if (authBtn) authBtn.hidden = false;
    if (userInfo) userInfo.hidden = true;
  }
}

/* ── Saved items (server + localStorage fallback) ──────────── */

const SAVED_ITEMS_KEY = 'thesis_recommender_saved_items';

async function getSavedItems() {
  if (currentUser) {
    // Fetch from server
    try {
      const resp = await fetch('/saved');
      if (resp.ok) {
        const data = await resp.json();
        return data.items || [];
      }
    } catch (err) {
      console.warn('Failed to fetch saved items:', err);
    }
    return [];
  } else {
    // Use localStorage for guests
    try {
      const json = localStorage.getItem(SAVED_ITEMS_KEY);
      return json ? JSON.parse(json) : [];
    } catch {
      return [];
    }
  }
}

async function saveItem(item) {
  const itemId = deriveItemId(item);
  
  if (currentUser) {
    // Save to server
    try {
      const resp = await fetch('/saved', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          item_id: itemId,
          item_data: item
        })
      });
      if (!resp.ok) {
        console.warn('Failed to save item to server');
      }
    } catch (err) {
      console.warn('Error saving item:', err);
    }
  } else {
    // Save to localStorage for guests
    const saved = await getSavedItems();
    if (saved.some(s => deriveItemId(s) === itemId)) return;
    saved.push(item);
    localStorage.setItem(SAVED_ITEMS_KEY, JSON.stringify(saved));
  }
}

async function unsaveItem(item) {
  const itemId = deriveItemId(item);
  
  if (currentUser) {
    // Remove from server
    try {
      const resp = await fetch(`/saved/${encodeURIComponent(itemId)}`, {
        method: 'DELETE'
      });
      if (!resp.ok) {
        console.warn('Failed to remove item from server');
      }
    } catch (err) {
      console.warn('Error removing item:', err);
    }
  } else {
    // Remove from localStorage for guests
    const saved = await getSavedItems();
    const filtered = saved.filter(s => deriveItemId(s) !== itemId);
    localStorage.setItem(SAVED_ITEMS_KEY, JSON.stringify(filtered));
  }
}

async function isItemSaved(item) {
  const saved = await getSavedItems();
  const itemId = deriveItemId(item);
  return saved.some(s => deriveItemId(s) === itemId);
}

/* ── Tab switching ──────────────────────────────────────────────── */

function setupTabSwitching() {
  if (!tabArticles || !tabWeb || !panelArticles || !panelWeb) {
    console.error('Tab elements not found:', { tabArticles, tabWeb, panelArticles, panelWeb });
    return;
  }

  tabArticles.addEventListener('click', () => {
    console.log('Articles tab clicked');
    tabArticles.classList.add('active');
    tabArticles.setAttribute('aria-selected', 'true');
    tabWeb.classList.remove('active');
    tabWeb.setAttribute('aria-selected', 'false');
    panelArticles.hidden = false;
    panelWeb.hidden = true;
  });

  tabWeb.addEventListener('click', () => {
    console.log('Web tab clicked');
    tabWeb.classList.add('active');
    tabWeb.setAttribute('aria-selected', 'true');
    tabArticles.classList.remove('active');
    tabArticles.setAttribute('aria-selected', 'false');
    panelWeb.hidden = false;
    panelArticles.hidden = true;
  });
}

// Initialize tab switching
setupTabSwitching();

function updateTabCounts() {
  if (articlesCount) {
    articlesCount.textContent = allArticles.length > 0 ? `(${allArticles.length})` : '';
  }
  if (webCount) {
    webCount.textContent = allWebResources.length > 0 ? `(${allWebResources.length})` : '';
  }
}

/* ── Save button ────────────────────────────────────────────── */

function buildSaveButton(card, item) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'btn-save';
  
  async function updateButton() {
    const saved = await isItemSaved(item);
    btn.textContent = saved ? t('btn_unsave') : t('btn_save');
    btn.classList.toggle('saved', saved);
  }
  
  updateButton();
  
  btn.addEventListener('click', async () => {
    const saved = await isItemSaved(item);
    if (saved) {
      await unsaveItem(item);
    } else {
      await saveItem(item);
    }
    await updateButton();
  });
  
  card.appendChild(btn);
  return btn;
}

/* ── Saved items modal ──────────────────────────────────────── */

if (savedBtn && savedModal && savedModalClose && savedList) {
  savedBtn.addEventListener('click', async () => {
    await renderSavedItems();
    savedModal.hidden = false;
  });
  
  savedModalClose.addEventListener('click', () => {
    savedModal.hidden = true;
  });
  
  // Close on outside click
  savedModal.addEventListener('click', (e) => {
    if (e.target === savedModal) {
      savedModal.hidden = true;
    }
  });
}

async function renderSavedItems() {
  if (!savedList) return;
  
  savedList.innerHTML = '';
  const saved = await getSavedItems();
  
  if (saved.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'saved-empty';
    empty.textContent = t('no_saved_items');
    savedList.appendChild(empty);
    return;
  }
  
  saved.forEach(item => {
    const card = item.resource_type === 'article' 
      ? buildArticleCard(item) 
      : buildWebCard(item);
    savedList.appendChild(card);
  });
}

/* ── Language toggle ────────────────────────────────────────── */
langToggleBtn.addEventListener('click', () => {
  currentLang = currentLang === 'ro' ? 'en' : 'ro';
  updateLanguageUI();
  applyI18n();
  saveState(); // Save language preference
});

function updateLanguageUI() {
  const langOptions = langToggleBtn.querySelectorAll('.lang-option');
  langOptions.forEach(option => {
    const lang = option.getAttribute('data-lang');
    if (lang === currentLang) {
      option.classList.add('active');
    } else {
      option.classList.remove('active');
    }
  });
}

/* ── Theme toggle ───────────────────────────────────────────── */
let currentTheme = localStorage.getItem('theme') || 'light';

function applyTheme(theme) {
  currentTheme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  
  const themeIcon = themeToggleBtn.querySelector('.theme-icon');
  if (themeIcon) {
    themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
  }
}

themeToggleBtn.addEventListener('click', () => {
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  applyTheme(newTheme);
});

// Apply saved theme on load
applyTheme(currentTheme);

/**
 * Walk the DOM and update every element that carries a data-i18n or
 * data-i18n-placeholder attribute.
 */
function applyI18n() {
  document.documentElement.lang = currentLang;
  document.title = t('page_title');

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.textContent = t(key);
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    el.placeholder = t(key);
  });
}

// Apply on load so the initial RO strings are consistent.
updateLanguageUI();
applyI18n();

// Restore state on page load
window.addEventListener('DOMContentLoaded', () => {
  const state = loadState();
  if (state) {
    console.log('Restoring state from sessionStorage');
    
    // Restore variables
    currentQuery = state.currentQuery;
    currentQueryData = state.currentQueryData;
    allArticles = state.allArticles || [];
    allWebResources = state.allWebResources || [];
    displayedArticles = state.displayedArticles || 0;
    displayedWebResources = state.displayedWebResources || 0;
    hasMoreArticles = state.hasMoreArticles !== false;
    hasMoreWebResources = state.hasMoreWebResources !== false;
    
    // Restore language
    if (state.currentLang && state.currentLang !== currentLang) {
      currentLang = state.currentLang;
      updateLanguageUI();
      applyI18n();
    }
    
    // Restore form inputs
    if (currentQueryData) {
      titleInput.value = currentQueryData.title || '';
      abstractInput.value = currentQueryData.abstract || '';
      keywordsInput.value = (currentQueryData.keywords || []).join(', ');
    }
    
    // Restore results display
    if (allArticles.length > 0 || allWebResources.length > 0) {
      articlesList.innerHTML = '';
      webList.innerHTML = '';
      
      // Display all articles
      allArticles.forEach(article => {
        articlesList.appendChild(buildArticleCard(article));
      });
      
      // Display all web resources
      allWebResources.forEach(resource => {
        webList.appendChild(buildWebCard(resource));
      });
      
      // Update empty messages
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
      
      // Show/hide load more buttons
      articlesLoadMore.hidden = !hasMoreArticles;
      webLoadMore.hidden = !hasMoreWebResources;
      
      // Update tab counts
      updateTabCounts();
      
      // Show results
      resultsWrapper.hidden = false;
    }
  }
});

/* ── Helpers ────────────────────────────────────────────────── */

function showError(msg) {
  errorMessage.textContent = msg;
  errorContainer.hidden = false;
}

function hideError() {
  errorContainer.hidden = true;
  errorMessage.textContent = '';
}

function showLoading() {
  loadingSpinner.hidden = false;
  // Update spinner label to current language
  const spinnerLabel = loadingSpinner.querySelector('.spinner-label');
  if (spinnerLabel) spinnerLabel.textContent = t('loading');
}

function hideLoading() {
  loadingSpinner.hidden = true;
}

function setSubmitDisabled(disabled) {
  submitBtn.disabled = disabled;
}

function showNotices(notices) {
  noticesContainer.innerHTML = '';
  if (!notices || notices.length === 0) {
    noticesContainer.hidden = true;
    return;
  }
  notices.forEach(msg => {
    const div = document.createElement('div');
    div.className = 'notice-item';
    div.setAttribute('role', 'status');
    div.textContent = msg;
    noticesContainer.appendChild(div);
  });
  noticesContainer.hidden = false;
}

/**
 * Return a score badge element.
 * @param {number} score  0.0–1.0
 * @param {string} [label]
 */
function makeScoreBadge(score, label) {
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

/**
 * Return a resource-type badge element.
 * @param {'article'|'web'} type
 */
function makeTypeBadge(type) {
  const span = document.createElement('span');
  span.className = 'badge ' + (type === 'article' ? 'badge-article' : 'badge-web');
  span.textContent = type === 'article' ? t('badge_article') : t('badge_web');
  return span;
}

/**
 * Return a quality-warning badge element.
 * @param {string} warningText
 */
function makeWarningBadge(warningText) {
  const span = document.createElement('span');
  span.className = 'badge badge-warning';
  span.setAttribute('role', 'img');
  span.setAttribute('aria-label', warningText);
  span.textContent = warningText;
  return span;
}

/* ── Star rating control ────────────────────────────────────── */

/**
 * Build a star rating widget and attach it to a card.
 *
 * @param {HTMLElement} card       The card element to append the widget to.
 * @param {string}      itemId     Unique identifier for the result item.
 * @param {string}      query      The current query text (sent with feedback).
 */
function buildRatingControl(card, itemId, query) {
  const wrapper = document.createElement('div');
  wrapper.className = 'rating-control';
  wrapper.setAttribute('aria-label', t('label_usefulness'));

  // Label
  const label = document.createElement('span');
  label.className = 'rating-label';
  label.textContent = t('label_usefulness') + ':';
  wrapper.appendChild(label);

  // Stars container
  const starsEl = document.createElement('span');
  starsEl.className = 'stars';
  starsEl.setAttribute('role', 'group');
  starsEl.setAttribute('aria-label', t('label_usefulness'));

  let currentRating = 0; // user's submitted rating for this item

  const starButtons = [];

  function renderStars(highlightUpTo) {
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
      const rating = i;
      currentRating = rating;
      renderStars(currentRating);
      await submitRating(itemId, query, rating, aggregateEl);
    });

    starsEl.appendChild(btn);
    starButtons.push(btn);
  }

  wrapper.appendChild(starsEl);

  // Aggregate display (avg + count)
  const aggregateEl = document.createElement('span');
  aggregateEl.className = 'rating-aggregate';
  aggregateEl.hidden = true;
  wrapper.appendChild(aggregateEl);

  card.appendChild(wrapper);

  // Pre-populate from server
  fetchExistingRating(itemId, starsEl, starButtons, aggregateEl).then(rating => {
    currentRating = rating;
    renderStars(currentRating);
  });

  return wrapper;
}

/**
 * Fetch the user's existing rating for an item and update the UI.
 * Returns the user_rating (0 if none).
 */
async function fetchExistingRating(itemId, starsEl, starButtons, aggregateEl) {
  try {
    const url = `/feedback/${encodeURIComponent(itemId)}?session_id=${encodeURIComponent(SESSION_ID)}`;
    const resp = await fetch(url);
    if (!resp.ok) return 0;
    const data = await resp.json();

    // Show aggregate if available
    updateAggregateDisplay(aggregateEl, data);

    return data.user_rating || 0;
  } catch {
    return 0;
  }
}

/**
 * Submit a rating to POST /feedback.
 */
async function submitRating(itemId, query, rating, aggregateEl) {
  try {
    const resp = await fetch('/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        item_id: itemId,
        query: query,
        rating: rating,
        session_id: SESSION_ID,
      }),
    });
    if (!resp.ok) {
      console.warn('Feedback submission failed:', resp.status);
      return;
    }
    // Refresh aggregate after submission
    const feedbackResp = await fetch(
      `/feedback/${encodeURIComponent(itemId)}?session_id=${encodeURIComponent(SESSION_ID)}`
    );
    if (feedbackResp.ok) {
      const data = await feedbackResp.json();
      updateAggregateDisplay(aggregateEl, data);
    }
  } catch (err) {
    console.warn('Feedback error:', err);
  }
}

/**
 * Update the aggregate rating display element.
 */
function updateAggregateDisplay(aggregateEl, data) {
  if (!data) return;
  const count = data.rating_count || 0;
  if (count === 0) {
    aggregateEl.hidden = true;
    return;
  }
  const parts = [];
  if (data.average_rating != null) {
    parts.push(t('avg_rating') + ': ' + Number(data.average_rating).toFixed(1) + ' ★');
  }
  parts.push('(' + count + ' ' + t('ratings_count') + ')');
  aggregateEl.textContent = parts.join(' ');
  aggregateEl.hidden = false;
}

/* ── Article card rendering ─────────────────────────────────── */

/**
 * Build and return a card element for an article recommendation.
 * @param {Object} article
 */
function buildArticleCard(article) {
  const card = document.createElement('article');
  card.className = 'result-card';
  card.setAttribute('role', 'listitem');

  // ── Header: title + badges ──
  const header = document.createElement('div');
  header.className = 'card-header';

  const titleEl = document.createElement('h3');
  titleEl.className = 'card-title';

  const link = article.doi
    ? 'https://doi.org/' + article.doi
    : (article.url || null);

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

  // ── Badges ──
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

  // ── Meta: authors, year ──
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
    yearSpan.textContent = article.year;
    meta.appendChild(yearSpan);
  }

  if (meta.children.length > 0) {
    card.appendChild(meta);
  }

  // ── Abstract snippet ──
  if (article.abstract_snippet) {
    const snippet = document.createElement('p');
    snippet.className = 'card-snippet';
    snippet.textContent = article.abstract_snippet;
    card.appendChild(snippet);
  }

  // ── DOI / URL link ──
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

  // ── Star rating ──
  const itemId = deriveItemId(article);
  buildRatingControl(card, itemId, currentQuery);

  // ── Save button ──
  buildSaveButton(card, article);

  return card;
}

/* ── Web resource card rendering ────────────────────────────── */

/**
 * Build and return a card element for a web resource recommendation.
 * @param {Object} resource
 */
function buildWebCard(resource) {
  const card = document.createElement('article');
  card.className = 'result-card';
  card.setAttribute('role', 'listitem');

  // ── Header: title ──
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

  // ── Badges ──
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

  // ── URL (clickable) ──
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

  // ── Snippet ──
  if (resource.snippet) {
    const snippet = document.createElement('p');
    snippet.className = 'card-snippet';
    snippet.textContent = resource.snippet;
    card.appendChild(snippet);
  }

  // ── Page keywords ──
  if (resource.keywords && resource.keywords.length > 0) {
    const kwContainer = document.createElement('div');
    kwContainer.className = 'card-keywords';
    kwContainer.setAttribute('aria-label', t('label_keywords_card'));
    resource.keywords.forEach(kw => {
      const tag = document.createElement('span');
      tag.className = 'keyword-tag';
      tag.textContent = kw;
      kwContainer.appendChild(tag);
    });
    card.appendChild(kwContainer);
  }

  // ── Star rating ──
  const itemId = deriveItemId(resource);
  buildRatingControl(card, itemId, currentQuery);

  // ── Save button ──
  buildSaveButton(card, resource);

  return card;
}

/* ── Item ID derivation ─────────────────────────────────────── */

/**
 * Derive a stable item ID from a recommendation object.
 * Prefers DOI for articles, URL for web resources, falls back to title hash.
 */
function deriveItemId(item) {
  if (item.doi) return 'doi:' + item.doi;
  if (item.url) return 'url:' + item.url;
  // Fallback: simple hash of title
  const title = (item.title || '').trim().toLowerCase();
  return 'title:' + simpleHash(title);
}

/**
 * Very simple non-cryptographic string hash (djb2).
 */
function simpleHash(str) {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i);
    hash |= 0; // Convert to 32-bit int
  }
  return (hash >>> 0).toString(16);
}

/* ── Form submission ────────────────────────────────────────── */

async function submitQuery(offset = 0) {
  const title = titleInput.value.trim();
  if (!title || title.length < 3) {
    showError(t('hint_title'));
    titleInput.focus();
    return;
  }

  const abstractVal = abstractInput.value.trim() || null;
  const keywordsRaw = keywordsInput.value.trim();
  const keywords = keywordsRaw
    ? keywordsRaw.split(',').map(k => k.trim()).filter(Boolean)
    : [];

  // Store query
  currentQuery = title;
  currentQueryData = { title, abstract: abstractVal, keywords };

  // If offset is 0, this is a new search - reset everything
  if (offset === 0) {
    clearState(); // Clear old state
    allArticles = [];
    allWebResources = [];
    displayedArticles = 0;
    displayedWebResources = 0;
    hasMoreArticles = true;
    hasMoreWebResources = true;

    // UI state: loading
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
    const requestBody = {
      ...currentQueryData,
      offset: offset
    };
    
    const resp = await fetch('/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    });

    const data = await resp.json();

    if (!resp.ok) {
      const msg = data.error || ('HTTP ' + resp.status);
      showError(msg);
      return;
    }

    // Show any notices (only on initial load)
    if (offset === 0 && data.notices && data.notices.length > 0) {
      showNotices(data.notices);
    }

    // Detect language from response (only on initial load)
    if (offset === 0 && data.query_language && data.query_language !== currentLang) {
      currentLang = data.query_language;
      langToggleBtn.textContent = currentLang === 'ro' ? 'EN' : 'RO';
      langToggleBtn.setAttribute('aria-pressed', currentLang === 'en' ? 'true' : 'false');
      applyI18n();
    }

    // Append new results
    const newArticles = data.articles || [];
    const newWebResources = data.web_resources || [];
    
    console.log('Received:', { articles: newArticles.length, webResources: newWebResources.length });
    
    // Check if we got fewer results than requested (means no more available)
    if (newArticles.length < ITEMS_PER_PAGE) {
      hasMoreArticles = false;
    }
    if (newWebResources.length < ITEMS_PER_PAGE) {
      hasMoreWebResources = false;
    }
    
    allArticles = allArticles.concat(newArticles);
    allWebResources = allWebResources.concat(newWebResources);

    // Display new results
    newArticles.forEach(article => {
      articlesList.appendChild(buildArticleCard(article));
    });
    displayedArticles += newArticles.length;
    
    newWebResources.forEach(resource => {
      webList.appendChild(buildWebCard(resource));
    });
    displayedWebResources += newWebResources.length;
    
    // Update empty messages
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
    
    // Show/hide load more buttons
    articlesLoadMore.hidden = !hasMoreArticles || newArticles.length === 0;
    webLoadMore.hidden = !hasMoreWebResources || newWebResources.length === 0;
    
    console.log('Load more buttons:', { 
      articles: articlesLoadMore.hidden ? 'hidden' : 'visible',
      web: webLoadMore.hidden ? 'hidden' : 'visible'
    });
    
    // Update tab counts
    updateTabCounts();

    resultsWrapper.hidden = false;
    
    // Save state after successful load
    saveState();

  } catch (err) {
    showError(err.message || 'Network error');
  } finally {
    hideLoading();
    setSubmitDisabled(false);
  }
}

function displayMoreArticles() {
  // This function is no longer used - results are displayed directly in submitQuery
}

function displayMoreWebResources() {
  // This function is no longer used - results are displayed directly in submitQuery
}

queryForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  await submitQuery();
});

// Load more buttons
if (articlesLoadMore) {
  articlesLoadMore.addEventListener('click', async () => {
    console.log('Load more articles clicked, current offset:', displayedArticles);
    await submitQuery(displayedArticles);
  });
}

if (webLoadMore) {
  webLoadMore.addEventListener('click', async () => {
    console.log('Load more web resources clicked, current offset:', displayedWebResources);
    await submitQuery(displayedWebResources);
  });
}

/* ── Authentication modals ──────────────────────────────────── */

const authBtn = document.getElementById('auth-btn');
const authModal = document.getElementById('auth-modal');
const authModalClose = document.getElementById('auth-modal-close');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const showRegisterLink = document.getElementById('show-register');
const showLoginLink = document.getElementById('show-login');
const logoutBtn = document.getElementById('logout-btn');

if (authBtn && authModal) {
  authBtn.addEventListener('click', () => {
    authModal.hidden = false;
    showLoginForm();
  });
}

if (authModalClose) {
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

function showLoginForm() {
  if (loginForm) loginForm.hidden = false;
  if (registerForm) registerForm.hidden = true;
}

function showRegisterForm() {
  if (loginForm) loginForm.hidden = true;
  if (registerForm) registerForm.hidden = false;
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
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    
    try {
      const resp = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await resp.json();
      
      if (resp.ok) {
        currentUser = data.user;
        updateAuthUI();
        authModal.hidden = true;
        loginForm.reset();
        if (errorEl) errorEl.textContent = '';
        
        // Migrate localStorage saved items to server
        await migrateSavedItems();
      } else {
        if (errorEl) errorEl.textContent = data.error || 'Login failed';
      }
    } catch (err) {
      if (errorEl) errorEl.textContent = 'Network error';
    }
  });
}

if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const errorEl = document.getElementById('register-error');
    
    try {
      const resp = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      });
      
      const data = await resp.json();
      
      if (resp.ok) {
        currentUser = data.user;
        updateAuthUI();
        authModal.hidden = true;
        registerForm.reset();
        if (errorEl) errorEl.textContent = '';
        
        // Migrate localStorage saved items to server
        await migrateSavedItems();
      } else {
        if (errorEl) errorEl.textContent = data.error || 'Registration failed';
      }
    } catch (err) {
      if (errorEl) errorEl.textContent = 'Network error';
    }
  });
}

if (logoutBtn) {
  logoutBtn.addEventListener('click', async () => {
    try {
      await fetch('/auth/logout', { method: 'POST' });
      currentUser = null;
      updateAuthUI();
    } catch (err) {
      console.warn('Logout error:', err);
    }
  });
}

// Migrate localStorage saved items to server after login
async function migrateSavedItems() {
  try {
    const json = localStorage.getItem(SAVED_ITEMS_KEY);
    if (!json) return;
    
    const localItems = JSON.parse(json);
    if (localItems.length === 0) return;
    
    // Save each item to server
    for (const item of localItems) {
      await saveItem(item);
    }
    
    // Clear localStorage after migration
    localStorage.removeItem(SAVED_ITEMS_KEY);
  } catch (err) {
    console.warn('Failed to migrate saved items:', err);
  }
}

// Check auth status on page load
checkAuthStatus();
