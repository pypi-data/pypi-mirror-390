/**
 * Main BioLM Sidebar Widget
 */
import React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ModelsTab } from './components/ModelsTab';
import { OperationsTab } from './components/OperationsTab';
import { SettingsTab } from './components/SettingsTab';

interface BioLMWidgetProps {
  notebookTracker: INotebookTracker;
}

class BioLMWidgetComponent extends React.Component<BioLMWidgetProps, { activeTab: string }> {
  constructor(props: BioLMWidgetProps) {
    super(props);
    this.state = { activeTab: 'models' };
  }

  render() {
    const { activeTab } = this.state;
    const { notebookTracker } = this.props;

    return (
      <div className="biolm-widget">
        <div className="biolm-tabs">
          <button
            className={`biolm-tab-button ${activeTab === 'models' ? 'active' : ''}`}
            onClick={() => this.setState({ activeTab: 'models' })}
          >
            🧠 Models
          </button>
          <button
            className={`biolm-tab-button ${activeTab === 'operations' ? 'active' : ''}`}
            onClick={() => this.setState({ activeTab: 'operations' })}
          >
            ⚙️ Operations
          </button>
          <button
            className={`biolm-tab-button ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => this.setState({ activeTab: 'settings' })}
          >
            🔑 Settings
          </button>
        </div>

        <div className="biolm-tab-content">
          {activeTab === 'models' && (
            <ModelsTab notebookTracker={notebookTracker} />
          )}
          {activeTab === 'operations' && (
            <OperationsTab notebookTracker={notebookTracker} />
          )}
          {activeTab === 'settings' && (
            <SettingsTab />
          )}
        </div>
      </div>
    );
  }
}

export class BioLMWidget extends ReactWidget {
  private _notebookTracker: INotebookTracker;

  constructor(notebookTracker: INotebookTracker) {
    super();
    this._notebookTracker = notebookTracker;
    this.addClass('biolm-widget-container');
    this.id = 'biolm-widget';
    this.title.label = 'BioLM';
    this.title.caption = 'BioLM Model Browser';
    this.title.iconClass = 'jp-MaterialIcon jp-Icon jp-Icon-16';
    this.title.closable = true;
  }

  render(): JSX.Element {
    return (
      <BioLMWidgetComponent
        notebookTracker={this._notebookTracker}
      />
    );
  }
}

