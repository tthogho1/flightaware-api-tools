import React, { useState, FormEvent } from 'react';

const App: React.FC = () => {
  const [input, setInput] = useState<string>('');
  const [response, setResponse] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResponse('');
    try {
      // 仮のAPIエンドポイント
      const res = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input }),
      });
      const data = await res.json();
      setResponse(data.output || JSON.stringify(data));
    } catch (err) {
      setResponse('エラーが発生しました');
    }
    setLoading(false);
  };

  return (
    <div
      style={{
        maxWidth: 600,
        margin: '40px auto',
        padding: 24,
        border: '1px solid #ddd',
        borderRadius: 8,
      }}
    >
      <h2>エージェント テスト画面</h2>
      <form onSubmit={handleSubmit} style={{ marginBottom: 16 }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="質問を入力してください"
          style={{ width: '80%', padding: 8, fontSize: 16 }}
        />
        <button type="submit" style={{ padding: '8px 16px', marginLeft: 8 }} disabled={loading}>
          送信
        </button>
      </form>
      <div style={{ minHeight: 80, background: '#fafafa', padding: 12, borderRadius: 4 }}>
        {loading ? '送信中...' : response}
      </div>
    </div>
  );
};

export default App;
