/**
 * Service for inserting code snippets into notebook cells
 */
import { INotebookTracker } from '@jupyterlab/notebook';
import { showErrorMessage } from '@jupyterlab/apputils';

/**
 * Generate a code snippet for a model and action
 * Based on BioLM SDK format: https://docs.biolm.ai/latest/python-client/usage.html
 */
export function generateSnippet(modelId: string, action: string): string {
  // Determine the type based on action
  let itemType = "sequence";
  let exampleItem = '"YOUR_SEQUENCE_HERE"';
  
  if (action === "generate") {
    itemType = "context";
    exampleItem = '"YOUR_CONTEXT_HERE"';
  }
  
  return `result = biolm(entity="${modelId}", action="${action}", type="${itemType}", items=${exampleItem})

print(result)`;
}

/**
 * Insert code into the active notebook cell
 */
export async function insertCode(
  notebookTracker: INotebookTracker,
  code: string,
  append: boolean = true
): Promise<boolean> {
  const current = notebookTracker.currentWidget;
  
  if (!current) {
    await showErrorMessage(
      'No Active Notebook',
      'Please open a notebook before inserting code.'
    );
    return false;
  }

  const notebook = current.content;
  const activeCell = notebook.activeCell;

  if (!activeCell) {
    await showErrorMessage(
      'No Active Cell',
      'Please select a cell in the notebook.'
    );
    return false;
  }

  const cellModel = activeCell.model;
  const sharedModel = cellModel.sharedModel;
  const currentText = sharedModel.getSource();

  if (append && currentText.trim()) {
    // Append with newline if cell has content
    sharedModel.setSource(currentText + '\n' + code);
  } else {
    // Replace or insert into empty cell
    sharedModel.setSource(code);
  }

  return true;
}
