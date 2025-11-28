import React, { useEffect, useState, useRef } from 'react';
import { FaProjectDiagram } from 'react-icons/fa';

interface AiSummaryProps {
    query: string;
    context: { title: string; snippet: string }[];
}

const AiSummary: React.FC<AiSummaryProps> = ({ query, context }) => {
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);
    const hasFetched = useRef(false);

    useEffect(() => {
        if (!query || context.length === 0 || hasFetched.current) return;

        const fetchAnswer = async () => {
            hasFetched.current = true;
            setLoading(true);
            setError(false);

            try {
                const response = await fetch('http://localhost:5001/answer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, context }),
                });

                if (!response.ok) throw new Error('Failed to fetch AI answer');
                if (!response.body) return;

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                setLoading(false);

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    const chunk = decoder.decode(value, { stream: true });
                    setAnswer((prev) => prev + chunk);
                }
            } catch (err) {
                console.error(err);
                setError(true);
                setLoading(false);
            }
        };

        fetchAnswer();
    }, [query, context]);

    if (error) return null;

    return (
        <div className="w-full max-w-4xl px-4 mb-8 animate-fade-in">
            <div className="bg-sky-100 rounded-xl p-6 border border-sky-200 shadow-[0_0_30px_rgba(56,189,248,0.2)]">
                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg bg-sky-200 border border-sky-300">
                        <FaProjectDiagram className="w-5 h-5 text-sky-700" />
                    </div>
                    <h2 className="text-lg font-semibold text-sky-900">Perceive AI</h2>
                </div>

                <div className="prose prose-sm max-w-none text-slate-800 leading-relaxed">
                    {loading ? (
                        <div className="flex items-center gap-2 text-sky-700 animate-pulse">
                            <span className="w-2 h-2 bg-sky-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                            <span className="w-2 h-2 bg-sky-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                            <span className="w-2 h-2 bg-sky-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                            <span>Thinking...</span>
                        </div>
                    ) : (
                        <p className="whitespace-pre-wrap">{answer}</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AiSummary;
