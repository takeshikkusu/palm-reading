import { useState, useRef } from 'react'
import { diagnosePalm } from '../services/api'
import './DiagnosisForm.css'

const ACCEPT = 'image/jpeg,image/png,image/webp,image/gif'
const MAX_SIZE_MB = 5
const MAX_BYTES = MAX_SIZE_MB * 1024 * 1024

export function DiagnosisForm({ onSuccess, onError, onLoadingChange, loading, error }) {
  const [prompt, setPrompt] = useState('')
  const [preview, setPreview] = useState(null)
  const [file, setFile] = useState(null)
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    const f = e.target.files?.[0]
    if (!f) {
      setFile(null)
      setPreview(null)
      return
    }
    if (f.size > MAX_BYTES) {
      onError(`画像は${MAX_SIZE_MB}MB以下にしてください`)
      setFile(null)
      setPreview(null)
      return
    }
    if (!ACCEPT.split(',').includes(f.type)) {
      onError('対応形式: JPEG, PNG, WebP, GIF')
      setFile(null)
      setPreview(null)
      return
    }
    setFile(f)
    setPreview(URL.createObjectURL(f))
    onError(null)
  }

  const fileToBase64 = (f) =>
    new Promise((resolve, reject) => {
      const r = new FileReader()
      r.onload = () => resolve(r.result)
      r.onerror = () => reject(new Error('画像の読み込みに失敗しました'))
      r.readAsDataURL(f)
    })

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      onError('手のひらの画像を選んでください')
      return
    }
    onLoadingChange(true)
    onError(null)
    try {
      const dataUrl = await fileToBase64(file)
      const data = await diagnosePalm(dataUrl, prompt || '')
      onSuccess(data)
    } catch (err) {
      onError(err.message || '診断に失敗しました')
    } finally {
      onLoadingChange(false)
    }
  }

  const handleClear = () => {
    setFile(null)
    setPreview(null)
    setPrompt('')
    if (fileInputRef.current) fileInputRef.current.value = ''
    onError(null)
  }

  return (
    <form className="diagnosis-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label className="form-label">手のひらの写真</label>
        <div className="file-area">
          <input
            ref={fileInputRef}
            type="file"
            accept={ACCEPT}
            onChange={handleFileChange}
            className="file-input"
            aria-label="画像を選択"
          />
          {preview ? (
            <div className="preview-wrap">
              <img src={preview} alt="手のひらプレビュー" className="preview-img" />
              <button type="button" className="preview-clear" onClick={handleClear} aria-label="画像を解除">
                ×
              </button>
            </div>
          ) : (
            <div className="file-placeholder">
              <span className="file-placeholder-text">タップして画像を選択</span>
              <span className="file-placeholder-hint">JPEG / PNG / WebP（{MAX_SIZE_MB}MB以下）</span>
            </div>
          )}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="prompt">
          質問（任意）
        </label>
        <input
          id="prompt"
          type="text"
          className="form-input"
          placeholder="例：恋愛運について知りたい"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={loading}
        />
      </div>

      {error && (
        <div className="form-error" role="alert">
          {error}
        </div>
      )}

      <button type="submit" className="form-submit" disabled={loading || !file}>
        {loading ? (
          <>
            <span className="spinner" aria-hidden />
            <span>診断中…</span>
          </>
        ) : (
          '手相を診断する'
        )}
      </button>
    </form>
  )
}
