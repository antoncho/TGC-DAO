"use client";

export default function Error({ error, reset }) {
  return (
    <div style={{ padding: 40, color: 'red', fontFamily: 'monospace' }}>
      <h1>Something went wrong</h1>
      <pre>{error?.message || 'An unknown error occurred.'}</pre>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}
