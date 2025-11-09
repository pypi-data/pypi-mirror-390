/**
 * BioLM API Client
 */
import { BioLMModel, BioLMAPIModel, APIError } from './types';

// Use server-side proxy to avoid CORS issues
const MODELS_ENDPOINT = '/biolm/api/models';
const TEST_CONNECTION_ENDPOINT = '/biolm/api/test-connection';
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

interface CacheEntry {
  data: BioLMModel[];
  timestamp: number;
}

let cache: CacheEntry | null = null;

/**
 * Convert API model to internal model format
 */
function convertAPIModel(apiModel: BioLMAPIModel): BioLMModel {
  // Derive actions from boolean flags
  const actions: string[] = [];
  if (apiModel.predictor) actions.push('predict');
  if (apiModel.encoder) actions.push('encode');
  if (apiModel.generator) actions.push('generate');
  if (apiModel.classifier) actions.push('classify');
  if (apiModel.similarity) actions.push('similarity');
  if (apiModel.explainer) actions.push('explain');
  if (apiModel.transformer) actions.push('transform');
  
  // If no specific actions, default to predict
  if (actions.length === 0) {
    actions.push('predict');
  }

  return {
    id: apiModel.model_slug,
    name: apiModel.model_name,
    description: apiModel.description,
    tags: apiModel.tags || [],
    apiVersion: apiModel.api_version,
    communityModel: apiModel.community_model,
    companyModel: apiModel.company_model,
    actions: actions,
    apiDocsLink: apiModel.api_docs_link,
  };
}

/**
 * Fetch models from BioLM API
 */
export async function fetchModels(apiKey?: string): Promise<BioLMModel[]> {
  // Check cache first
  if (cache && Date.now() - cache.timestamp < CACHE_TTL) {
    return cache.data;
  }

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Build URL with API key as query parameter if provided
  let url = MODELS_ENDPOINT;
  if (apiKey) {
    url += `?api_key=${encodeURIComponent(apiKey)}`;
    // Also include in Authorization header for consistency
    headers['Authorization'] = `Bearer ${apiKey}`;
  }

  try {
    // Use regular fetch for same-origin requests to our proxy endpoint
    // This automatically includes JupyterLab session cookies for authentication
    const response = await fetch(url, {
      method: 'GET',
      headers,
      credentials: 'same-origin',
    });

    if (!response.ok) {
      const error: APIError = {
        message: `Failed to fetch models: ${response.statusText}`,
        status: response.status,
      };
      throw error;
    }

    const data: BioLMAPIModel[] = await response.json();
    
    // Convert API models to internal format
    const models: BioLMModel[] = Array.isArray(data)
      ? data.map(convertAPIModel)
      : [];

    // Update cache
    cache = {
      data: models,
      timestamp: Date.now(),
    };

    return models;
  } catch (error) {
    // If we have cached data, return it even if stale
    if (cache) {
      console.warn('Using cached models due to fetch error:', error);
      return cache.data;
    }
    
    // Re-throw with more helpful error message
    if (error instanceof Error) {
      // Check if it's a network/CORS error
      const errorMessage = error.message.includes('fetch') || error.message.includes('CORS') || error.message.includes('Failed to fetch')
        ? 'Unable to connect to BioLM API. Please check your internet connection and API endpoint configuration.'
        : error.message;
      
      const apiError: APIError = {
        message: errorMessage,
      };
      throw apiError;
    }
    throw error;
  }
}

/**
 * Clear the models cache
 */
export function clearCache(): void {
  cache = null;
}

/**
 * Test API connection with authentication
 */
export async function testConnection(apiKey: string): Promise<{ valid: boolean; message?: string; accountInfo?: any }> {
  try {
    // Use regular fetch for same-origin requests to our proxy endpoint
    // This automatically includes JupyterLab session cookies for authentication
    const response = await fetch(TEST_CONNECTION_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ api_key: apiKey }),
      credentials: 'same-origin',
    });

    if (response.ok) {
      const result = await response.json();
      return {
        valid: result.valid || false,
        message: result.message || 'Connection test completed',
      };
    } else {
      const error = await response.json().catch(() => ({}));
      return {
        valid: false,
        message: error.message || `HTTP ${response.status}: ${response.statusText}`,
      };
    }
  } catch (error) {
    return {
      valid: false,
      message: error instanceof Error ? error.message : 'Connection failed',
    };
  }
}

