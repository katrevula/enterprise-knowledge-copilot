import type { StreamEvent } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function parseEventBlock(block: string): StreamEvent | null {
  const lines = block.split('\n');
  const eventLine = lines.find((line) => line.startsWith('event: '));
  const dataLines = lines.filter((line) => line.startsWith('data: '));

  if (!eventLine || dataLines.length === 0) {
    return null;
  }

  const event = eventLine.replace('event: ', '').trim();
  const rawData = dataLines.map((line) => line.replace('data: ', '')).join('\n');

  try {
    return { event, data: JSON.parse(rawData) } as StreamEvent;
  } catch {
    return null;
  }
}

export async function streamChat(
  message: string,
  conversationId: string | null,
  onEvent: (event: StreamEvent) => void
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream'
    },
    body: JSON.stringify({ message, conversation_id: conversationId })
  });

  if (!response.ok || !response.body) {
    throw new Error(`Chat request failed with status ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const blocks = buffer.split('\n\n');
    buffer = blocks.pop() || '';

    for (const block of blocks) {
      const parsed = parseEventBlock(block);
      if (parsed) {
        onEvent(parsed);
      }
    }
  }

  if (buffer.trim()) {
    const parsed = parseEventBlock(buffer);
    if (parsed) {
      onEvent(parsed);
    }
  }
}

export async function submitFeedback(
  messageId: string,
  rating: 'up' | 'down',
  comment?: string
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message_id: messageId, rating, comment })
  });

  if (!response.ok) {
    throw new Error('Feedback request failed');
  }
}

