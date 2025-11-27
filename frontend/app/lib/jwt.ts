export async function generateWebSocketToken(clientId: string): Promise<string> {
  try {
    const response = await fetch('/api/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ clientId }),
    });

    if (!response.ok) {
      throw new Error('Error generating jwt token');
    }

    const data = await response.json();
    return data.token;
  } catch (error) {
    console.error('Error generating token:', error);
    throw error;
  }
}
