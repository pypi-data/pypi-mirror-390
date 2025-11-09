/**
 * Settings Tab Component
 */
import React, { useState, useEffect } from 'react';
import {
  getProfiles,
  getActiveProfileName,
  saveProfiles,
  setActiveProfile,
  getDefaultModel,
  getDefaultAction,
  setDefaultModel,
  setDefaultAction,
  APIProfile,
} from '../services/localStorage';
import { testConnection } from '../api/client';
import { showErrorMessage } from '@jupyterlab/apputils';

interface SettingsTabProps {
}

export const SettingsTab: React.FC<SettingsTabProps> = () => {
  const [profiles, setProfiles] = useState<APIProfile[]>([]);
  const [activeProfile, setActiveProfileState] = useState<string | undefined>();
  const [defaultModel, setDefaultModelState] = useState<string>('');
  const [defaultAction, setDefaultActionState] = useState<string>('predict');
  const [newProfileName, setNewProfileName] = useState('');
  const [newProfileKey, setNewProfileKey] = useState('');
  const [editingProfile, setEditingProfile] = useState<string | null>(null);
  const [editProfileName, setEditProfileName] = useState('');
  const [editProfileKey, setEditProfileKey] = useState('');
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<{ valid: boolean; message?: string } | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = () => {
    const loadedProfiles = getProfiles();
    const loadedActiveProfile = getActiveProfileName();
    const loadedDefaultModel = getDefaultModel() || '';
    const loadedDefaultAction = getDefaultAction();

    setProfiles(loadedProfiles);
    setActiveProfileState(loadedActiveProfile);
    setDefaultModelState(loadedDefaultModel);
    setDefaultActionState(loadedDefaultAction);
  };

  const handleAddProfile = async () => {
    if (!newProfileName.trim() || !newProfileKey.trim()) {
      showErrorMessage('Invalid Input', 'Please provide both profile name and API key');
      return;
    }

    if (profiles.some(p => p.name === newProfileName)) {
      showErrorMessage('Duplicate Profile', 'A profile with this name already exists');
      return;
    }

    const newProfile: APIProfile = {
      name: newProfileName.trim(),
      apiKey: newProfileKey.trim(),
    };

    const updatedProfiles = [...profiles, newProfile];
    await saveProfiles(updatedProfiles);
    setProfiles(updatedProfiles);
    setNewProfileName('');
    setNewProfileKey('');
    console.log(`Profile "${newProfile.name}" has been added`);
  };

  const handleEditProfile = (profile: APIProfile) => {
    setEditingProfile(profile.name);
    setEditProfileName(profile.name);
    setEditProfileKey(profile.apiKey);
  };

  const handleSaveEdit = async () => {
    if (!editingProfile || !editProfileName.trim() || !editProfileKey.trim()) {
      return;
    }

    const updatedProfiles = profiles.map(p =>
      p.name === editingProfile
        ? { name: editProfileName.trim(), apiKey: editProfileKey.trim() }
        : p
    );

    await saveProfiles(updatedProfiles);
    setProfiles(updatedProfiles);
    
    // Update active profile if it was edited
    if (activeProfile === editingProfile) {
      await setActiveProfile(editProfileName.trim());
      setActiveProfileState(editProfileName.trim());
    }

    setEditingProfile(null);
    setEditProfileName('');
    setEditProfileKey('');
    console.log('Profile has been updated');
  };

  const handleDeleteProfile = async (profileName: string) => {

    const updatedProfiles = profiles.filter(p => p.name !== profileName);
    await saveProfiles(updatedProfiles);
    setProfiles(updatedProfiles);

    // Clear active profile if it was deleted
    if (activeProfile === profileName) {
      await setActiveProfile(undefined);
      setActiveProfileState(undefined);
    }

    console.log(`Profile "${profileName}" has been deleted`);
  };

  const handleSetActiveProfile = async (profileName: string | undefined) => {

      await setActiveProfile(profileName);
    setActiveProfileState(profileName);
    console.log(profileName ? `Active profile: ${profileName}` : 'Using environment variable');
  };

  const handleTestConnection = async (apiKey: string) => {
    setTestingConnection(true);
    setConnectionStatus(null);

    try {
      const result = await testConnection(apiKey);
      setConnectionStatus(result);
      
      if (result.valid) {
        console.log(result.message || 'API key is valid');
      } else {
        showErrorMessage('Connection Failed', result.message || 'Invalid API key');
      }
    } catch (error: any) {
      const errorMessage = error.message || 'Connection test failed';
      setConnectionStatus({ valid: false, message: errorMessage });
      showErrorMessage('Connection Failed', errorMessage);
    } finally {
      setTestingConnection(false);
    }
  };

  const handleSaveDefaults = async () => {

    await setDefaultModel(defaultModel.trim() || undefined);
    await setDefaultAction(defaultAction);
    console.log('Default preferences have been saved');
  };

  // Check for environment variable
  const hasEnvKey = typeof process !== 'undefined' && process.env && !!process.env.BIOLM_API_KEY;

  return (
    <div className="biolm-settings-tab">
      <div className="biolm-settings-section">
        <h3>API Key Profiles</h3>
        
        {hasEnvKey && (
          <div className="biolm-env-notice">
            <p>BIOLM_API_KEY environment variable is set and will be used if no profile is selected.</p>
          </div>
        )}

        <div className="biolm-profile-list">
          {profiles.length === 0 && (
            <div className="biolm-empty">No profiles configured. Add one below.</div>
          )}

          {profiles.map(profile => (
            <div key={profile.name} className="biolm-profile-card">
              {editingProfile === profile.name ? (
                <div className="biolm-profile-edit">
                  <input
                    type="text"
                    className="jp-mod-styled jp-InputGroup-input"
                    value={editProfileName}
                    onChange={(e) => setEditProfileName(e.target.value)}
                    placeholder="Profile name"
                    style={{ marginBottom: '4px' }}
                  />
                  <input
                    type="password"
                    className="jp-mod-styled jp-InputGroup-input"
                    value={editProfileKey}
                    onChange={(e) => setEditProfileKey(e.target.value)}
                    placeholder="API Key"
                    style={{ marginBottom: '4px' }}
                  />
                  <div>
                    <button
                      className="jp-mod-styled jp-mod-accept"
                      onClick={handleSaveEdit}
                    >
                      Save
                    </button>
                    <button
                      className="jp-mod-styled jp-mod-minimal"
                      onClick={() => {
                        setEditingProfile(null);
                        setEditProfileName('');
                        setEditProfileKey('');
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="biolm-profile-header">
                    <strong>{profile.name}</strong>
                    <div>
                      <button
                        className={`jp-mod-styled jp-mod-minimal ${activeProfile === profile.name ? 'jp-mod-active' : ''}`}
                        onClick={() => handleSetActiveProfile(profile.name)}
                        title="Set as active"
                      >
                        {activeProfile === profile.name ? 'Active' : 'Set Active'}
                      </button>
                      <button
                        className="jp-mod-styled jp-mod-minimal"
                        onClick={() => handleTestConnection(profile.apiKey)}
                        disabled={testingConnection}
                      >
                        Test
                      </button>
                      <button
                        className="jp-mod-styled jp-mod-minimal"
                        onClick={() => handleEditProfile(profile)}
                      >
                        Edit
                      </button>
                      <button
                        className="jp-mod-styled jp-mod-minimal"
                        onClick={() => handleDeleteProfile(profile.name)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                  {connectionStatus && activeProfile === profile.name && (
                    <div className={`biolm-connection-status ${connectionStatus.valid ? 'valid' : 'invalid'}`}>
                      {connectionStatus.message}
                    </div>
                  )}
                </>
              )}
            </div>
          ))}
        </div>

        <div className="biolm-add-profile">
          <h4>Add New Profile</h4>
          <input
            type="text"
            className="jp-mod-styled jp-InputGroup-input"
            value={newProfileName}
            onChange={(e) => setNewProfileName(e.target.value)}
            placeholder="Profile name"
            style={{ marginBottom: '4px' }}
          />
          <input
            type="password"
            className="jp-mod-styled jp-InputGroup-input"
            value={newProfileKey}
            onChange={(e) => setNewProfileKey(e.target.value)}
            placeholder="API Key"
            style={{ marginBottom: '4px' }}
          />
          <button
            className="jp-mod-styled jp-mod-accept"
            onClick={handleAddProfile}
          >
            Add Profile
          </button>
        </div>

        <div className="biolm-env-option">
          <button
            className={`jp-mod-styled jp-mod-minimal ${!activeProfile ? 'jp-mod-active' : ''}`}
            onClick={() => handleSetActiveProfile(undefined)}
            disabled={!hasEnvKey}
          >
            Use Environment Variable {hasEnvKey ? '(Available)' : '(Not Set)'}
          </button>
        </div>
      </div>

      <div className="biolm-settings-section">
        <h3>Default Preferences</h3>
        <div className="biolm-defaults">
          <label>
            Default Model ID:
            <input
              type="text"
              className="jp-mod-styled jp-InputGroup-input"
              value={defaultModel}
              onChange={(e) => setDefaultModelState(e.target.value)}
              placeholder="Optional"
              style={{ marginLeft: '8px', width: '200px' }}
            />
          </label>
          <label style={{ marginTop: '8px', display: 'block' }}>
            Default Action:
            <select
              className="jp-mod-styled"
              value={defaultAction}
              onChange={(e) => setDefaultActionState(e.target.value)}
              style={{ marginLeft: '8px' }}
            >
              <option value="predict">predict</option>
              <option value="generate">generate</option>
              <option value="embed">embed</option>
              <option value="encode">encode</option>
              <option value="classify">classify</option>
            </select>
          </label>
          <button
            className="jp-mod-styled jp-mod-accept"
            onClick={handleSaveDefaults}
            style={{ marginTop: '8px' }}
          >
            Save Defaults
          </button>
        </div>
      </div>
    </div>
  );
};

