/**
 * API client for Hybrid Thesis Recommender
 * Handles all HTTP requests to the Flask backend
 */

import type {
  RecommendRequest,
  RecommendResponse,
  FeedbackRequest,
  FeedbackResponse,
  FeedbackQueryResult,
  AuthResponse,
  SavedItemsResponse,
  RecommendationItem,
  UserInfo
} from './types.js';

/**
 * Helper function to derive item ID from a recommendation item
 * Must match the logic in app.ts
 */
function deriveItemIdFromItem(item: RecommendationItem): string {
  if ('doi' in item && item.doi) return 'doi:' + item.doi;
  if (item.url) return 'url:' + item.url;
  const title = (item.title || '').trim().toLowerCase();
  return 'title:' + simpleHash(title);
}

/**
 * Simple hash function (djb2)
 */
function simpleHash(str: string): string {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return (hash >>> 0).toString(16);
}

/**
 * Fetch recommendations from the backend
 */
export async function fetchRecommendations(
  request: RecommendRequest
): Promise<RecommendResponse> {
  const response = await fetch('/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });

  const data: RecommendResponse = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }

  return data;
}

/**
 * Submit a rating for an item
 */
export async function submitFeedback(
  request: FeedbackRequest
): Promise<FeedbackResponse> {
  const response = await fetch('/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });

  const data: FeedbackResponse = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }

  return data;
}

/**
 * Get ratings for a specific item
 */
export async function getFeedback(
  itemId: string,
  sessionId: string
): Promise<FeedbackQueryResult> {
  const url = `/feedback/${encodeURIComponent(itemId)}?session_id=${encodeURIComponent(sessionId)}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Register a new user
 */
export async function register(
  username: string,
  email: string,
  password: string
): Promise<AuthResponse> {
  const response = await fetch('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  });

  const data: AuthResponse = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Registration failed');
  }

  return data;
}

/**
 * Login user
 */
export async function login(
  username: string,
  password: string
): Promise<AuthResponse> {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  const data: AuthResponse = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Login failed');
  }

  return data;
}

/**
 * Logout user
 */
export async function logout(): Promise<void> {
  await fetch('/auth/logout', { method: 'POST' });
}

/**
 * Get current user info
 */
export async function getCurrentUser(): Promise<UserInfo | null> {
  const response = await fetch('/auth/me');

  if (!response.ok) {
    return null;
  }

  const data: { user: UserInfo | null } = await response.json();
  return data.user;
}

/**
 * Get saved items
 */
export async function getSavedItems(): Promise<RecommendationItem[]> {
  try {
    const response = await fetch('/saved');

    if (response.status === 401) {
      // User not authenticated - return from localStorage
      const saved = JSON.parse(localStorage.getItem('thesis_recommender_saved_items') || '[]');
      return saved;
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data: SavedItemsResponse = await response.json();
    return data.items || [];
  } catch (err) {
    console.warn('Failed to fetch saved items:', err);
    // Fallback to localStorage
    try {
      const saved = JSON.parse(localStorage.getItem('thesis_recommender_saved_items') || '[]');
      return saved;
    } catch (storageErr) {
      return [];
    }
  }
}

/**
 * Save an item
 */
export async function saveItem(
  itemId: string,
  itemData: RecommendationItem
): Promise<void> {
  try {
    const response = await fetch('/saved', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId, item_data: itemData })
    });

    if (response.status === 401) {
      // User not authenticated - save to localStorage
      const saved = JSON.parse(localStorage.getItem('thesis_recommender_saved_items') || '[]');
      if (!saved.some((item: RecommendationItem) => deriveItemIdFromItem(item) === itemId)) {
        saved.push(itemData);
        localStorage.setItem('thesis_recommender_saved_items', JSON.stringify(saved));
      }
      return;
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (err) {
    console.warn('Failed to save item:', err);
    // Fallback to localStorage
    try {
      const saved = JSON.parse(localStorage.getItem('thesis_recommender_saved_items') || '[]');
      if (!saved.some((item: RecommendationItem) => deriveItemIdFromItem(item) === itemId)) {
        saved.push(itemData);
        localStorage.setItem('thesis_recommender_saved_items', JSON.stringify(saved));
      }
    } catch (storageErr) {
      console.warn('Failed to save to localStorage:', storageErr);
    }
  }
}

/**
 * Remove a saved item
 */
export async function unsaveItem(itemId: string): Promise<void> {
  try {
    const response = await fetch(`/saved/${encodeURIComponent(itemId)}`, {
      method: 'DELETE'
    });

    if (response.status === 401) {
      // User not authenticated - remove from localStorage
      const saved = JSON.parse(localStorage.getItem('thesis_recommender_saved_items') || '[]');
      const filtered = saved.filter((item: RecommendationItem) => deriveItemIdFromItem(item) !== itemId);
      localStorage.setItem('thesis_recommender_saved_items', JSON.stringify(filtered));
      return;
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (err) {
    console.warn('Failed to remove item:', err);
    // Fallback to localStorage
    try {
      const saved = JSON.parse(localStorage.getItem('thesis_recommender_saved_items') || '[]');
      const filtered = saved.filter((item: RecommendationItem) => deriveItemIdFromItem(item) !== itemId);
      localStorage.setItem('thesis_recommender_saved_items', JSON.stringify(filtered));
    } catch (storageErr) {
      console.warn('Failed to remove from localStorage:', storageErr);
    }
  }
}

/**
 * Check if an item is saved
 */
export async function isItemSaved(itemId: string): Promise<boolean> {
  try {
    const response = await fetch(`/saved/${encodeURIComponent(itemId)}/check`);

    if (response.status === 401 || response.status === 404) {
      // User not authenticated or endpoint not found - check localStorage
      const saved = JSON.parse(localStorage.getItem('thesis_recommender_saved_items') || '[]');
      return saved.some((item: RecommendationItem) => deriveItemIdFromItem(item) === itemId);
    }

    if (!response.ok) {
      return false;
    }

    const data: { saved: boolean } = await response.json();
    return data.saved;
  } catch (err) {
    console.warn('Failed to check if item is saved:', err);
    // Fallback to localStorage
    try {
      const saved = JSON.parse(localStorage.getItem('thesis_recommender_saved_items') || '[]');
      return saved.some((item: RecommendationItem) => deriveItemIdFromItem(item) === itemId);
    } catch (storageErr) {
      return false;
    }
  }
}
