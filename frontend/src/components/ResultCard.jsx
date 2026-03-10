import './ResultCard.css'

const SECTIONS = [
  { key: 'summary', label: '総合', icon: '✦' },
  { key: 'life_line', label: '生命線', icon: '◇' },
  { key: 'head_line', label: '知能線', icon: '◆' },
  { key: 'heart_line', label: '感情線', icon: '○' },
  { key: 'fate_line', label: '運命線', icon: '□' },
  { key: 'advice', label: 'アドバイス', icon: '★' },
]

export function ResultCard({ data, onReset }) {
  return (
    <div className="result-card">
      <div className="result-card-inner">
        <h2 className="result-title">診断結果</h2>
        {SECTIONS.map(({ key, label, icon }) => {
          const value = data[key]
          if (value == null || value === '') return null
          return (
            <section key={key} className="result-section">
              <h3 className="result-section-title">
                <span className="result-section-icon" aria-hidden>{icon}</span>
                {label}
              </h3>
              <p className="result-section-text">{value}</p>
            </section>
          )
        })}
        <button type="button" className="result-reset" onClick={onReset}>
          もう一度診断する
        </button>
      </div>
    </div>
  )
}
