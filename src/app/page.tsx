'use client';

import { useState } from 'react';

export default function Home() {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);

    const handleAsk = async () => {
        if (!query) return;

        setLoading(true);
        setResponse('');

        try {
            const res = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
            });

            const data = await res.json();
            setResponse(data.answer || 'No response from the AI.');
        } catch (error) {
            console.error('Error:', error);
            setResponse('An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
            <h1 className="text-3xl font-bold mb-6">NirmAI - Budget Chatbot</h1>
            <div className="w-full max-w-2xl">
                <input
                    type="text"
                    placeholder="Ask something about the 2025 budget..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="w-full p-3 border rounded mb-4"
                />
                <button
                    onClick={handleAsk}
                    className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
                    disabled={loading}
                >
                    {loading ? 'Processing...' : 'Ask'}
                </button>
            </div>
            {response && (
                <div className="w-full max-w-2xl bg-white p-4 mt-6 rounded shadow">
                    <h2 className="text-xl font-semibold">Response:</h2>
                    <p className="mt-2">{response}</p>
                </div>
            )}
        </div>
    );
}