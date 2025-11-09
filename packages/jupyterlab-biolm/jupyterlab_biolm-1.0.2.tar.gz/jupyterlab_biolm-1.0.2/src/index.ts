/**
 * BioLM JupyterLab Extension
 */
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ICommandPalette } from '@jupyterlab/apputils';
import { BioLMWidget } from './widget';

/**
 * Initialization data for the jupyterlab-biolm extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-biolm:plugin',
  autoStart: true,
  requires: [INotebookTracker],
  optional: [ICommandPalette],
  activate: async (
    app: JupyterFrontEnd,
    notebookTracker: INotebookTracker,
    palette: ICommandPalette | null
  ) => {
    console.log('JupyterLab extension jupyterlab-biolm is activated!');

    // Create widget - no settings dependency
    console.log('BioLM: Creating widget...');
    const widget = new BioLMWidget(notebookTracker);
    console.log('BioLM: Widget created with ID:', widget.id);

    // Add to left sidebar
    console.log('BioLM: Adding widget to left sidebar...');
    app.shell.add(widget, 'left', { rank: 1000 });
    console.log('BioLM: Widget added to sidebar. Title:', widget.title.label);

    // Add command to open widget
    app.commands.addCommand('biolm:open', {
      label: 'Open BioLM',
      execute: () => {
        app.shell.activateById(widget.id);
      },
    });

    // Add to command palette if available
    if (palette) {
      palette.addItem({
        command: 'biolm:open',
        category: 'BioLM',
      });
    }
  },
};

export default plugin;

