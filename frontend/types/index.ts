export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'student' | 'admin';
  auth_provider: 'email' | 'google';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  profile?: UserProfile;
}

export interface UserProfile {
  id: string;
  avatar_url?: string;
  bio?: string;
  institution?: string;
  course?: string;
  year_of_study?: number;
  preferences?: Record<string, unknown>;
}

export interface AuthResponse {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_verified: boolean;
  access_token: string;
  refresh_token: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Conversation {
  id: string;
  title: string;
  context?: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message?: string;
}

export interface Attachment {
  file_name: string;
  file_url: string;
  file_type: string;
  file_size: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: Record<string, unknown>;
  attachments?: Attachment[];
  tokens_used?: number;
  created_at: string;
}

export interface ResearchResponse {
  query: string;
  summary?: string;
  sources: ResearchSource[];
  citations?: Citation[];
}

export interface ResearchSource {
  title: string;
  url: string;
  authors?: string[];
  year?: number;
  journal?: string;
  abstract?: string;
  relevance_score: number;
}

export interface Citation {
  id?: string;
  style: string;
  citation_text: string;
  title: string;
  authors?: string;
  year?: number;
  created_at?: string;
}

export interface WritingResponse {
  title: string;
  content: string;
  word_count: number;
  type: string;
  generated_at: string;
}

export interface ParaphraseResponse {
  original_text: string;
  paraphrased_text: string;
  mode: string;
  word_count_original: number;
  word_count_paraphrased: number;
  changes_made: number;
}

export interface Quiz {
  id: string;
  title: string;
  topic: string;
  difficulty: string;
  question_count: number;
  score?: number;
  total_points?: number;
  questions: QuizQuestion[];
  created_at: string;
}

export interface QuizQuestion {
  id: string;
  question_type: string;
  question_text: string;
  options?: string[];
  correct_answer: string;
  explanation?: string;
  points: number;
  order: number;
}

export interface FlashcardSet {
  id: string;
  title: string;
  topic: string;
  flashcards: Flashcard[];
  created_at: string;
}

export interface Flashcard {
  id: string;
  front: string;
  back: string;
  difficulty: string;
}

export interface NoteSummary {
  original_length: number;
  summary_length: number;
  summary: string;
  key_points: string[];
}

export interface StudyPlan {
  id: string;
  title: string;
  subject: string;
  start_date: string;
  end_date: string;
  hours_per_day: number;
  tasks: StudyTask[];
  created_at: string;
}

export interface StudyTask {
  id: string;
  title: string;
  description?: string;
  scheduled_date: string;
  duration_minutes: number;
  is_completed: boolean;
  order: number;
}

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: string;
  content_preview?: string;
  chunk_count?: number;
  created_at: string;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}
