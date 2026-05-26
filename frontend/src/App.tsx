import { FormEvent, useMemo, useRef, useState } from 'react';
import {
  AlertCircle,
  Bot,
  CheckCircle2,
  Loader2,
  Send,
  ThumbsDown,
  ThumbsUp,
  User
} from 'lucide-react';
import { streamChat, submitFeedback } from './api';
import type { ActivityItem, ChatMessage, Citation, StreamEvent } from './types';

const EXAMPLE_QUESTIONS = [
  'Summarize our leave policy.',
  'What is the escalation process for incidents?',
  'Find information about onboarding steps.'
];

function newId(prefix: string): string {
  return `${prefix}-${crypto.randomUUID()}`;
}

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  const canSubmit = input.trim().length > 0 && !isStreaming;
  const emptyState = messages.length === 0;

  const latestStatus = useMemo(() => activity.at(-1)?.label || 'Ready', [activity]);

  async function handleSubmit(event?: FormEvent, override?: string) {
    event?.preventDefault();
    const text = (override ?? input).trim();
    if (!text || isStreaming) {
      return;
    }

    const userMessage: ChatMessage = {
      id: newId('user'),
      role: 'user',
      content: text,
      status: 'complete'
    };
    const assistantId = newId('assistant');
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      citations: [],
      status: 'streaming'
    };

    setMessages((current) => [...current, userMessage, assistantMessage]);
    setInput('');
    setError(null);
    setIsStreaming(true);
    setActivity([{ id: newId('activity'), label: 'Request received' }]);

    try {
      await streamChat(text, conversationId, (streamEvent) => {
        handleStreamEvent(streamEvent, assistantId);
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'The request failed.';
      setError(message);
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId
            ? { ...item, status: 'error', content: 'I could not complete the request.' }
            : item
        )
      );
    } finally {
      setIsStreaming(false);
      inputRef.current?.focus();
    }
  }

  function handleStreamEvent(streamEvent: StreamEvent, assistantId: string) {
    if (streamEvent.event === 'status') {
      const state = String(streamEvent.data.state || 'working');
      setActivity((current) => [...current, { id: newId('activity'), label: humanizeStatus(state) }]);
      return;
    }

    if (streamEvent.event === 'tool_call') {
      setActivity((current) => [
        ...current,
        { id: newId('activity'), label: `Calling MCP tool: ${streamEvent.data.name}` }
      ]);
      return;
    }

    if (streamEvent.event === 'token') {
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId ? { ...item, content: item.content + streamEvent.data.text } : item
        )
      );
      return;
    }

    if (streamEvent.event === 'citations') {
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId ? { ...item, citations: streamEvent.data.citations } : item
        )
      );
      return;
    }

    if (streamEvent.event === 'complete') {
      setConversationId(streamEvent.data.conversation_id);
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId
            ? { ...item, id: streamEvent.data.message_id, status: 'complete' }
            : item
        )
      );
      setActivity((current) => [
        ...current,
        {
          id: newId('activity'),
          label: `Completed in ${streamEvent.data.latency_ms} ms`
        }
      ]);
      return;
    }

    if (streamEvent.event === 'error') {
      const message = streamEvent.data.hint
        ? `${streamEvent.data.message} ${streamEvent.data.hint}`
        : streamEvent.data.message;
      setError(message);
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId ? { ...item, status: 'error', content: message } : item
        )
      );
    }
  }

  async function handleFeedback(messageId: string, rating: 'up' | 'down') {
    try {
      await submitFeedback(messageId, rating);
      setActivity((current) => [
        ...current,
        { id: newId('activity'), label: `Feedback recorded: ${rating}` }
      ]);
    } catch {
      setError('Feedback could not be submitted.');
    }
  }

  return (
    <main className="app-shell">
      <section className="chat-panel" aria-label="Enterprise Knowledge Copilot">
        <header className="topbar">
          <div>
            <h1>Enterprise Knowledge Copilot</h1>
            <p>Remote MCP + FastAPI controlled tool loop</p>
          </div>
          <div className="status-pill" aria-live="polite">
            {isStreaming ? <Loader2 className="spin" size={16} /> : <CheckCircle2 size={16} />}
            <span>{latestStatus}</span>
          </div>
        </header>

        <div className="content-grid">
          <section className="messages" aria-live="polite" aria-label="Conversation">
            {emptyState ? (
              <div className="empty-state">
                <Bot size={36} />
                <h2>Ask a policy question</h2>
                <div className="example-grid">
                  {EXAMPLE_QUESTIONS.map((question) => (
                    <button
                      key={question}
                      type="button"
                      onClick={() => void handleSubmit(undefined, question)}
                      disabled={isStreaming}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  onFeedback={handleFeedback}
                />
              ))
            )}
          </section>

          <aside className="activity-panel" aria-label="Agent activity">
            <h2>Activity</h2>
            <ol>
              {activity.map((item) => (
                <li key={item.id}>{item.label}</li>
              ))}
            </ol>
            {error ? (
              <div className="error-box" role="alert">
                <AlertCircle size={16} />
                <span>{error}</span>
              </div>
            ) : null}
          </aside>
        </div>

        <form className="composer" onSubmit={(event) => void handleSubmit(event)}>
          <label htmlFor="chat-input">Message</label>
          <textarea
            id="chat-input"
            ref={inputRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask about leave, onboarding, incidents, IT access..."
            rows={2}
            disabled={isStreaming}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                void handleSubmit();
              }
            }}
          />
          <button type="submit" disabled={!canSubmit} aria-label="Send message">
            <Send size={18} />
          </button>
        </form>
      </section>
    </main>
  );
}

function humanizeStatus(state: string): string {
  return state
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function MessageBubble({
  message,
  onFeedback
}: {
  message: ChatMessage;
  onFeedback: (messageId: string, rating: 'up' | 'down') => Promise<void>;
}) {
  const isAssistant = message.role === 'assistant';

  return (
    <article className={`message ${message.role}`}>
      <div className="avatar" aria-hidden="true">
        {isAssistant ? <Bot size={18} /> : <User size={18} />}
      </div>
      <div className="message-body">
        <div className="message-text">
          {message.content || (message.status === 'streaming' ? 'Thinking...' : '')}
        </div>
        {isAssistant && message.citations && message.citations.length > 0 ? (
          <CitationList citations={message.citations} />
        ) : null}
        {isAssistant && message.status === 'complete' ? (
          <div className="feedback-row" aria-label="Rate answer">
            <button type="button" onClick={() => void onFeedback(message.id, 'up')}>
              <ThumbsUp size={15} />
              Helpful
            </button>
            <button type="button" onClick={() => void onFeedback(message.id, 'down')}>
              <ThumbsDown size={15} />
              Needs work
            </button>
          </div>
        ) : null}
      </div>
    </article>
  );
}

function CitationList({ citations }: { citations: Citation[] }) {
  return (
    <div className="citations">
      <h3>Sources</h3>
      {citations.map((citation) => (
        <details key={`${citation.source_id}-${citation.chunk_id}`}>
          <summary>
            {citation.title}
            {citation.section ? ` · ${citation.section}` : ''}
          </summary>
          <p>{citation.excerpt}</p>
        </details>
      ))}
    </div>
  );
}

