/**
 * Models Tab Component
 */
import React, { useState, useEffect, useMemo } from 'react';
import { BioLMModel } from '../api/types';
import { fetchModels, clearCache } from '../api/client';
import { getActiveAPIKey } from '../services/localStorage';
import { generateSnippet, insertCode } from '../services/codeInsertion';
import { showErrorMessage } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';

interface ModelsTabProps {
  notebookTracker: INotebookTracker;
}

export const ModelsTab: React.FC<ModelsTabProps> = ({ notebookTracker }) => {
  const [models, setModels] = useState<BioLMModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [expandedDescriptions, setExpandedDescriptions] = useState<Set<string>>(new Set());

  // Fetch models on mount and when settings change
  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    setError(null);
    try {
      const apiKey = getActiveAPIKey();
      const fetchedModels = await fetchModels(apiKey);
      setModels(fetchedModels);
    } catch (err: any) {
      setError(err.message || 'Failed to load models');
      console.error('Error loading models:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    clearCache();
    loadModels();
  };

  // Filter and search models
  const filteredModels = useMemo(() => {
    let filtered = models;

    // Filter by action tag
    if (selectedTag) {
      filtered = filtered.filter(model => 
        (model.actions && model.actions.includes(selectedTag)) ||
        (model.tags && model.tags.includes(selectedTag))
      );
    }

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(model => {
        const name = (model.name || model.id || '').toLowerCase();
        const description = (model.description || '').toLowerCase();
        const tags = (model.tags || []).join(' ').toLowerCase();
        return name.includes(query) || description.includes(query) || tags.includes(query);
      });
    }

    // Sort by name
    return filtered.sort((a, b) => {
      const nameA = (a.name || a.id || '').toLowerCase();
      const nameB = (b.name || b.id || '').toLowerCase();
      return nameA.localeCompare(nameB);
    });
  }, [models, searchQuery, selectedTag]);

  // Get all unique action tags (for filtering/buttons)
  const allActionTags = useMemo(() => {
    const tagSet = new Set<string>();
    models.forEach(model => {
      if (model.actions) {
        model.actions.forEach(action => tagSet.add(action));
      }
    });
    return Array.from(tagSet).sort();
  }, [models]);

  const toggleDescription = (modelId: string) => {
    const newExpanded = new Set(expandedDescriptions);
    if (newExpanded.has(modelId)) {
      newExpanded.delete(modelId);
    } else {
      newExpanded.add(modelId);
    }
    setExpandedDescriptions(newExpanded);
  };

  const handleTagClick = async (model: BioLMModel, tag: string) => {
    const snippet = generateSnippet(model.id, tag);
    const success = await insertCode(notebookTracker, snippet, true);
    if (success) {
      console.log(`Inserted ${tag} snippet for ${model.name || model.id}`);
    }
  };

  const handleCopyModelId = async (modelId: string) => {
    try {
      await navigator.clipboard.writeText(modelId);
      console.log('Model ID copied to clipboard');
    } catch (err) {
      showErrorMessage('Copy Failed', 'Failed to copy model ID to clipboard');
    }
  };

  return (
    <div className="biolm-models-tab">
      <div className="biolm-tab-header">
        <input
          type="text"
          className="jp-mod-styled jp-InputGroup-input"
          placeholder="Search models..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ width: '100%', marginBottom: '8px' }}
        />
        <div className="biolm-tag-filter">
          <button
            className={`jp-mod-styled jp-mod-minimal ${!selectedTag ? 'jp-mod-active' : ''}`}
            onClick={() => setSelectedTag(null)}
            style={{ marginRight: '4px', marginBottom: '4px' }}
          >
            All
          </button>
          {allActionTags.map(tag => (
            <button
              key={tag}
              className={`jp-mod-styled jp-mod-minimal ${selectedTag === tag ? 'jp-mod-active' : ''}`}
              onClick={() => setSelectedTag(tag === selectedTag ? null : tag)}
              style={{ marginRight: '4px', marginBottom: '4px' }}
            >
              {tag}
            </button>
          ))}
        </div>
        <button
          className="jp-mod-styled jp-mod-minimal"
          onClick={handleRefresh}
          style={{ marginTop: '8px' }}
        >
          Refresh
        </button>
      </div>

      <div className="biolm-models-list">
        {loading && (
          <div className="biolm-loading">Loading models...</div>
        )}

        {error && (
          <div className="biolm-error">
            <p>Error: {error}</p>
            <button
              className="jp-mod-styled jp-mod-minimal"
              onClick={loadModels}
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && filteredModels.length === 0 && (
          <div className="biolm-empty">
            {searchQuery || selectedTag ? 'No models match your filters' : 'No models available'}
          </div>
        )}

        {!loading && !error && filteredModels.map(model => {
          const isExpanded = expandedDescriptions.has(model.id);
          const description = model.description || '';
          const shouldTruncate = description.length > 150;
          const displayDescription = shouldTruncate && !isExpanded
            ? description.substring(0, 150) + '...'
            : description;

          return (
            <div key={model.id} className="biolm-model-card">
              <div className="biolm-model-header">
                <h3 className="biolm-model-name">{model.name || model.id}</h3>
                <button
                  className="jp-mod-styled jp-mod-minimal"
                  onClick={() => handleCopyModelId(model.id)}
                  title="Copy Model ID"
                >
                  Copy ID
                </button>
              </div>
              
              {description && (
                <div className="biolm-model-description">
                  <p>{displayDescription}</p>
                  {shouldTruncate && (
                    <button
                      className="jp-mod-styled jp-mod-minimal"
                      onClick={() => toggleDescription(model.id)}
                    >
                      {isExpanded ? 'Show less' : 'Show more'}
                    </button>
                  )}
                </div>
              )}

              {model.actions && model.actions.length > 0 && (
                <div className="biolm-model-tags">
                  {model.actions.map(action => (
                    <button
                      key={action}
                      className="biolm-tag-button"
                      onClick={() => handleTagClick(model, action)}
                      title={`Insert ${action} code for ${model.name || model.id}`}
                    >
                      {action}
                    </button>
                  ))}
                </div>
              )}
              {model.tags && model.tags.length > 0 && (
                <div className="biolm-model-meta-tags" style={{ marginTop: '8px', fontSize: '11px', color: 'var(--biolm-text-secondary)' }}>
                  <strong>Tags:</strong> {model.tags.join(', ')}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

