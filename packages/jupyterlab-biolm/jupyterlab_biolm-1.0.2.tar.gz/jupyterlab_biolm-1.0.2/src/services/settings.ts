/**
 * Settings service for managing API keys and profiles
 */
import { ISettingRegistry } from '@jupyterlab/settingregistry';

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

const DEFAULT_SETTINGS: SettingsData = {
  profiles: [],
  activeProfile: undefined,
  defaultModel: undefined,
  defaultAction: 'predict',
};

/**
 * Get the active API key from settings or environment
 */
export function getActiveAPIKey(settings?: ISettingRegistry.ISettings): string | undefined {
  // First check environment variable
  if (typeof process !== 'undefined' && process.env && process.env.BIOLM_API_KEY) {
    return process.env.BIOLM_API_KEY;
  }

  // Then check settings
  if (settings) {
    const data = (settings.get('profiles').composite as unknown as APIProfile[]) || [];
    const activeProfileName = settings.get('activeProfile').composite as string | undefined;
    
    if (activeProfileName && data) {
      const activeProfile = data.find(p => p.name === activeProfileName);
      if (activeProfile) {
        return activeProfile.apiKey;
      }
    }
  }

  return undefined;
}

/**
 * Get all profiles from settings
 */
export function getProfiles(settings?: ISettingRegistry.ISettings): APIProfile[] {
  if (!settings) {
    return [];
  }
  
  const profiles = (settings.get('profiles').composite as unknown as APIProfile[]) || [];
  return Array.isArray(profiles) ? profiles : [];
}

/**
 * Get active profile name
 */
export function getActiveProfileName(settings?: ISettingRegistry.ISettings): string | undefined {
  if (!settings) {
    return undefined;
  }
  
  return settings.get('activeProfile').composite as string | undefined;
}

/**
 * Save profiles to settings
 */
export async function saveProfiles(
  settings: ISettingRegistry.ISettings,
  profiles: APIProfile[]
): Promise<void> {
  await settings.set('profiles', profiles as any);
}

/**
 * Set active profile
 */
export async function setActiveProfile(
  settings: ISettingRegistry.ISettings,
  profileName: string | undefined
): Promise<void> {
  await settings.set('activeProfile', (profileName ?? null) as any);
}

/**
 * Get default model
 */
export function getDefaultModel(settings?: ISettingRegistry.ISettings): string | undefined {
  if (!settings) {
    return undefined;
  }
  
  const value = settings.get('defaultModel').composite;
  return value ? (value as string) : undefined;
}

/**
 * Get default action
 */
export function getDefaultAction(settings?: ISettingRegistry.ISettings): string {
  if (!settings) {
    return DEFAULT_SETTINGS.defaultAction || 'predict';
  }
  
  const value = settings.get('defaultAction').composite;
  return (value ? (value as string) : null) || 'predict';
}

/**
 * Set default model
 */
export async function setDefaultModel(
  settings: ISettingRegistry.ISettings,
  modelId: string | undefined
): Promise<void> {
  await settings.set('defaultModel', (modelId ?? null) as any);
}

/**
 * Set default action
 */
export async function setDefaultAction(
  settings: ISettingRegistry.ISettings,
  action: string
): Promise<void> {
  await settings.set('defaultAction', action as any);
}

