/**
 * Operations Tab Component
 */
import React, { useState, useMemo } from 'react';
import { INotebookTracker } from '@jupyterlab/notebook';
import { operations, Operation } from '../data/operations';
import { insertCode } from '../services/codeInsertion';
import { showErrorMessage } from '@jupyterlab/apputils';

interface OperationsTabProps {
  notebookTracker: INotebookTracker;
}

export const OperationsTab: React.FC<OperationsTabProps> = ({ notebookTracker }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Get unique categories
  const categories = useMemo(() => {
    const categorySet = new Set<string>();
    operations.forEach(op => categorySet.add(op.category));
    return Array.from(categorySet).sort();
  }, []);

  // Filter operations
  const filteredOperations = useMemo(() => {
    let filtered = operations;

    // Filter by category
    if (selectedCategory) {
      filtered = filtered.filter(op => op.category === selectedCategory);
    }

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(op => {
        const title = op.title.toLowerCase();
        const description = op.description.toLowerCase();
        const category = op.category.toLowerCase();
        return title.includes(query) || description.includes(query) || category.includes(query);
      });
    }

    return filtered;
  }, [searchQuery, selectedCategory]);

  const handleInsert = async (operation: Operation) => {
    const success = await insertCode(notebookTracker, operation.code, true);
    if (success) {
      console.log(`Inserted ${operation.title} example`);
    }
  };

  const handleCopy = async (code: string) => {
    try {
      await navigator.clipboard.writeText(code);
      console.log('Code snippet copied to clipboard');
    } catch (err) {
      showErrorMessage('Copy Failed', 'Failed to copy code snippet to clipboard');
    }
  };

  return (
    <div className="biolm-operations-tab">
      <div className="biolm-tab-header">
        <input
          type="text"
          className="jp-mod-styled jp-InputGroup-input"
          placeholder="Search operations..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ width: '100%', marginBottom: '8px' }}
        />
        <div className="biolm-category-filter">
          <button
            className={`jp-mod-styled jp-mod-minimal ${!selectedCategory ? 'jp-mod-active' : ''}`}
            onClick={() => setSelectedCategory(null)}
            style={{ marginRight: '4px', marginBottom: '4px' }}
          >
            All
          </button>
          {categories.map(category => (
            <button
              key={category}
              className={`jp-mod-styled jp-mod-minimal ${selectedCategory === category ? 'jp-mod-active' : ''}`}
              onClick={() => setSelectedCategory(category === selectedCategory ? null : category)}
              style={{ marginRight: '4px', marginBottom: '4px' }}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      <div className="biolm-operations-list">
        {filteredOperations.length === 0 && (
          <div className="biolm-empty">
            {searchQuery || selectedCategory ? 'No operations match your filters' : 'No operations available'}
          </div>
        )}

        {filteredOperations.map((operation, index) => (
          <div key={index} className="biolm-operation-card">
            <div className="biolm-operation-header">
              <h3 className="biolm-operation-title">{operation.title}</h3>
              <span className="biolm-operation-category">{operation.category}</span>
            </div>
            
            <p className="biolm-operation-description">{operation.description}</p>

            {operation.parameters && operation.parameters.length > 0 && (
              <div className="biolm-operation-parameters">
                <strong>Parameters:</strong> {operation.parameters.join(', ')}
              </div>
            )}

            <div className="biolm-operation-code">
              <pre><code>{operation.code}</code></pre>
            </div>

            <div className="biolm-operation-actions">
              <button
                className="jp-mod-styled jp-mod-accept"
                onClick={() => handleInsert(operation)}
              >
                Insert
              </button>
              <button
                className="jp-mod-styled jp-mod-minimal"
                onClick={() => handleCopy(operation.code)}
              >
                Copy
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

