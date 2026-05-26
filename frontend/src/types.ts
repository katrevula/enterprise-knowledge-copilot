export type Role = 'user' | 'assistant';

export interface Citation {
  source_id: string;
  chunk_id: string;
  title: string;
  section: string;
  excerpt: string;
  score?: number | null;
}

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  citations?: Citation[];
  status?: 'streaming' | 'complete' | 'error';
}

export interface ActivityItem {
  id: string;
  label: string;
}

export type StreamEvent =
  | { event: 'status'; data: Record<string, unknown> }
  | { event: 'tool_call'; data: { name: string; arguments?: Record<string, unknown> } }
  | { event: 'token'; data: { text: string } }
  | { event: 'citations'; data: { citations: Citation[] } }
  | { event: 'done'; data: { answer: string; citations: Citation[]; status: string } }
  | { event: 'complete'; data: { conversation_id: string; message_id: string; status: string; latency_ms: number } }
  | { event: 'error'; data: { message: string; detail?: string; hint?: string } };

