import React, { useState } from 'react';
import StarBackground from './components/StarBackground';
import AiSummary from './components/AiSummary';

interface SearchResult {
  title: string;
  link: string;
  snippet: string;
  display_url: string;
}

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [aiContext, setAiContext] = useState<{ title: string; snippet: string }[]>([]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);
    setResults([]);
    setAiContext([]); // Clear AI context at the start of a new search

    try {
      // Assuming backend is running on port 5001
      // We need to use the search endpoint that returns JSON
      // The Whoogle backend returns HTML by default, but we can parse it or use the json format if supported.
      // Looking at the backend code, `search()` supports `format=json`.

      const response = await fetch(`http://localhost:5001/search?q=${encodeURIComponent(query)}&format=json`);
      const data = await response.json();

      if (data.results && Array.isArray(data.results)) {
        const mappedResults = data.results.map((r: any) => ({
          title: r.title || r.text || 'No Title',
          link: r.href,
          snippet: r.content || '',
          display_url: r.href
        }));

        setResults(mappedResults);

        // Prepare context for AI (top 2 results for speed)
        const topResults = mappedResults.slice(0, 2).map((r: any) => ({
          title: r.title,
          snippet: r.snippet
        }));
        setAiContext(topResults);
      } else {
        setResults([]);
        setAiContext([]);
      }

    } catch (error) {
      console.error('Error fetching search results:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleHomeClick = () => {
    setSearched(false);
    setQuery('');
    setResults([]);
    setAiContext([]);
  };

  return (
    <div className="min-h-screen flex flex-col items-center bg-black text-white font-sans selection:bg-sky-500/30 selection:text-sky-200 relative overflow-hidden">

      <StarBackground />

      {/* Header / Logo Area */}
      <div
        onClick={handleHomeClick}
        className={`flex flex-col items-center transition-all duration-700 ease-out relative z-10 cursor-pointer ${searched ? 'mt-8 mb-8 scale-75' : 'mt-[42vh] mb-8'}`}
      >
        <h1 className="font-bold tracking-widest perceive-3d text-7xl select-none drop-shadow-[0_0_15px_rgba(56,189,248,0.3)] hover:opacity-90 transition-opacity">
          perceive
        </h1>
      </div>

      {/* Search Bar */}
      <div className={`w-full max-w-4xl relative z-10 px-4 transition-all duration-700 ${searched ? 'translate-y-0' : 'translate-y-4'}`}>
        <form onSubmit={handleSearch} className="relative group">
          <div className="neon-moving-border">
            <div className="relative bg-black/40 backdrop-blur-xl rounded-2xl overflow-hidden">
              <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none z-10">
                <svg className="h-5 w-5 text-gray-400 group-focus-within:text-sky-400 transition-colors duration-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="block w-full pl-14 pr-12 py-4 bg-transparent border-none text-lg text-white placeholder:text-gray-500 focus:ring-0 outline-none"
                placeholder="What do you seek?"
              />
              {loading && (
                <div className="absolute inset-y-0 right-0 pr-6 flex items-center z-10">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white/10 border-t-sky-400"></div>
                </div>
              )}
            </div>
          </div>
        </form>
      </div>

      {/* Results */}
      <div className={`w-full max-w-4xl mt-12 px-4 pb-20 relative z-10 transition-all duration-700 ${searched ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10 pointer-events-none'}`}>

        {/* AI Summary Block */}
        {searched && aiContext.length > 0 && (
          <AiSummary key={query} query={query} context={aiContext} />
        )}

        <div className="grid gap-6">
          {results.map((result, index) => (
            <div
              key={index}
              className="group bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/5 hover:bg-white/10 hover:border-white/10 hover:-translate-y-0.5 transition-all duration-300 animate-fade-in"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <a href={result.link} target="_blank" rel="noopener noreferrer" className="block">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-0.5 rounded-md bg-white/5 text-xs font-medium text-gray-400 group-hover:bg-sky-500/10 group-hover:text-sky-300 transition-colors duration-300 truncate max-w-[300px]">
                    {new URL(result.link).hostname.replace('www.', '')}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-sky-300 group-hover:text-sky-200 transition-colors duration-200 mb-2 leading-tight">
                  {result.title}
                </h3>
                <p className="text-gray-400 leading-relaxed text-sm line-clamp-3 group-hover:text-gray-300">
                  {result.snippet}
                </p>
              </a>
            </div>
          ))}
        </div>

        {searched && !loading && results.length === 0 && (
          <div className="text-center py-20">
            <p className="text-gray-500 text-lg font-light">No results found.</p>
          </div>
        )}
      </div>

    </div>
  );
}

export default App;
