import { useState } from 'react'
import { DiagnosisForm } from './components/DiagnosisForm'
import { ResultCard } from './components/ResultCard'
import './App.css'

export default function App() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleDiagnosisComplete = (data) => {
    setResult(data)
    setError(null)
  }

  const handleDiagnosisError = (message) => {
    setError(message)
    setResult(null)
  }

  const setLoadingState = (value) => {
    setLoading(value)
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">Palm AI</h1>
        <p className="app-subtitle">手のひらを写して、AIがあなたの手相を読みます</p>
      </header>

      <main className="app-main">
        {!result ? (
          <DiagnosisForm
            onSuccess={handleDiagnosisComplete}
            onError={handleDiagnosisError}
            onLoadingChange={setLoadingState}
            loading={loading}
            error={error}
          />
        ) : (
          <ResultCard data={result} onReset={handleReset} />
        )}
      </main>

      <footer className="app-footer">
        <span>Palm AI — 手相診断はエンターテインメントです</span>
      </footer>
    </div>
  )
}
