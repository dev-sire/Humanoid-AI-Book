/**
 * API client for RAG chatbot backend.
 *
 * Provides functions to interact with the FastAPI backend.
 */

const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://humanoid-ai-book.onrender.com'
  : 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  session_id?: string;
  selected_text?: string;
}

export interface Source {
  title: string;
  file_path: string;
  relevance_score: number;
  excerpt: string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  sources: Source[];
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  services: {
    qdrant: string;
    postgres: string;
    openai: string;
  };
}

/**
 * Send a chat message to the backend.
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send message');
    }

    return await response.json();
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}

/**
 * Check backend health status.
 */
export async function checkHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
}

/**
 * Get session history.
 */
export async function getSessionHistory(sessionId: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/history`);

    if (!response.ok) {
      throw new Error('Failed to get session history');
    }

    return await response.json();
  } catch (error) {
    console.error('Session history error:', error);
    throw error;
  }
}
