/**
 * LocalStorage-based settings service (replaces JupyterLab settings)
 */
export interface APIProfile {
  name: string;
  apiKey: string;
}

export interface SettingsData {
  profiles: APIProfile[];
  activeProfile?: string;
  defaultModel?: string;
  defaultAction?: string;
}

const STORAGE_KEY = 'jupyterlab-biolm:settings';
const DEFAULT_SETTINGS: SettingsData = {
  profiles: [],
  activeProfile: undefined,
  defaultModel: undefined,
  defaultAction: 'predict',
};

function getStoredSettings(): SettingsData {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return { ...DEFAULT_SETTINGS, ...JSON.parse(stored) };
    }
  } catch (e) {
    console.warn('Failed to load settings from localStorage:', e);
  }
  return { ...DEFAULT_SETTINGS };
}

function saveStoredSettings(settings: SettingsData): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  } catch (e) {
    console.warn('Failed to save settings to localStorage:', e);
  }
}

export function getProfiles(): APIProfile[] {
  return getStoredSettings().profiles || [];
}

export function getActiveProfileName(): string | undefined {
  return getStoredSettings().activeProfile;
}

export function getActiveAPIKey(): string | undefined {
  // Check environment variable first
  if (typeof process !== 'undefined' && process.env && process.env.BIOLM_API_KEY) {
    return process.env.BIOLM_API_KEY;
  }
  
  const settings = getStoredSettings();
  const activeProfile = settings.activeProfile;
  if (activeProfile) {
    const profile = settings.profiles.find(p => p.name === activeProfile);
    if (profile) {
      return profile.apiKey;
    }
  }
  return undefined;
}

export function getDefaultModel(): string | undefined {
  return getStoredSettings().defaultModel;
}

export function getDefaultAction(): string {
  return getStoredSettings().defaultAction || 'predict';
}

export async function saveProfiles(profiles: APIProfile[]): Promise<void> {
  const settings = getStoredSettings();
  settings.profiles = profiles;
  saveStoredSettings(settings);
}

export async function setActiveProfile(profileName: string | undefined): Promise<void> {
  const settings = getStoredSettings();
  settings.activeProfile = profileName;
  saveStoredSettings(settings);
}

export async function setDefaultModel(modelId: string | undefined): Promise<void> {
  const settings = getStoredSettings();
  settings.defaultModel = modelId;
  saveStoredSettings(settings);
}

export async function setDefaultAction(action: string): Promise<void> {
  const settings = getStoredSettings();
  settings.defaultAction = action;
  saveStoredSettings(settings);
}

