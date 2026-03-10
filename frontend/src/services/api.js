/**
 * Backend API クライアント
 * 環境に応じてベースURLを切り替え可能（将来の拡張用）
 */

const getBaseUrl = () => {
  if (import.meta.env.PROD && import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '')
  }
  return '' // Vite proxy で /api → localhost:5000 に転送
}

/**
 * 手相診断APIを呼び出す
 * @param {string} imageBase64 - Base64エンコードされた画像（data URL可）
 * @param {string} [prompt] - オプションの質問
 * @returns {Promise<{ summary: string, life_line: string, head_line: string, heart_line: string, fate_line?: string, advice?: string }>}
 */
export async function diagnosePalm(imageBase64, prompt = '') {
  const base = getBaseUrl()
  const res = await fetch(`${base}/api/diagnose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image: imageBase64,
      prompt: prompt || undefined,
    }),
  })
  const data = await res.json()
  if (!res.ok) {
    const err = new Error(data.error || '診断に失敗しました')
    err.status = res.status
    throw err
  }
  return data
}

/**
 * ヘルスチェック
 * @returns {Promise<{ status: string }>}
 */
export async function healthCheck() {
  const base = getBaseUrl()
  const res = await fetch(`${base}/api/health`)
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || 'APIに接続できません')
  return data
}
