export interface PersonalitySettings {
  drama_level: number;
  temperature: number;
  language: string;
}

export interface AppConfig {
  project_path: string | null;
  provider: string;
  model_name: string;
  api_base_url: string | null;
  api_key: string | null;
  api_key_configured: boolean;
  personality: PersonalitySettings;
}
