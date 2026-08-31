import { StrictMode, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const scenarios = [
  { key: 'listing', label: '商品上架', request: '请生成商品标题和详情页文案' },
  { key: 'customer-service', label: '客服话术', request: '客户想申请退货，请整理客服话术' },
  { key: 'sales-report', label: '销售日报', request: '生成 2026-08-30 的销售日报' },
  { key: 'inventory-alert', label: '库存预警', request: '请输出库存预警和补货建议' },
]

function App() {
  const [request, setRequest] = useState(scenarios[3].request)
  const [mode, setMode] = useState('auto')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [running, setRunning] = useState(false)

  async function runWorkflow(event) {
    event.preventDefault()
    if (request.trim().length < 2) {
      setError('请输入至少两个字符的业务问题。')
      return
    }
    setRunning(true)
    setError('')
    setResult(null)
    try {
      const response = await fetch(`${API_BASE_URL}/api/workflows`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request: request.trim(), mode }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail || '服务返回了未知错误。')
      setResult(payload)
    } catch (networkError) {
      setError(`无法连接本地 API：${networkError.message}`)
    } finally {
      setRunning(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">LOCAL / SIMULATED DATA / LANGGRAPH</p>
          <h1>电商运营 <span>Multi-Agent</span></h1>
          <p className="subtitle">路由、规则检索、只读数据查询、内容生成、审核与结果整合。</p>
        </div>
        <div className="runtime-chip">API 本地运行</div>
      </header>

      <section className="workspace" aria-label="任务运行区">
        <form className="task-panel" onSubmit={runWorkflow}>
          <div className="panel-heading"><h2>业务任务</h2><span>4 个可验证场景</span></div>
          <div className="scenario-list" aria-label="预设任务">
            {scenarios.map((scenario) => (
              <button type="button" key={scenario.key} className="scenario-button" onClick={() => setRequest(scenario.request)}>
                {scenario.label}
              </button>
            ))}
          </div>
          <label htmlFor="request">输入运营问题</label>
          <textarea id="request" value={request} onChange={(event) => setRequest(event.target.value)} rows="6" maxLength="500" />
          <fieldset>
            <legend>内容生成方式</legend>
            <label className="radio-label"><input type="radio" name="mode" value="auto" checked={mode === 'auto'} onChange={() => setMode('auto')} /> 自动：已配置模型时调用，未配置时回退</label>
            <label className="radio-label"><input type="radio" name="mode" value="deterministic" checked={mode === 'deterministic'} onChange={() => setMode('deterministic')} /> 确定性：不访问外部模型</label>
          </fieldset>
          <button className="run-button" type="submit" disabled={running}>{running ? '正在执行...' : '运行工作流'}</button>
          {error && <p className="error" role="alert">{error}</p>}
        </form>

        <section className="result-panel" aria-live="polite">
          {!result && !running && <div className="empty-state"><p>选择一个业务场景并运行。</p><small>所有订单、商品与库存均为本地模拟数据。</small></div>}
          {running && <div className="empty-state"><p>Router 正在分流任务...</p><small>随后将依次执行规则检索、数据查询、内容生成和审核。</small></div>}
          {result && <Result result={result} />}
        </section>
      </section>

      <footer>该演示不连接真实店铺、广告平台或用户数据。模型密钥仅保存在后端环境变量中。</footer>
    </main>
  )
}

function Result({ result }) {
  const sources = result.knowledge.length ? result.knowledge.map((item) => item.source).join('、') : '本地结构化模拟数据'
  return (
    <>
      <div className="result-title"><div><p className="eyebrow">{result.review_passed ? 'REVIEW PASSED' : 'REVIEW BLOCKED'}</p><h2>{result.route || '未支持的请求'}</h2></div><span className={`status ${result.review_passed ? 'pass' : 'blocked'}`}>{result.review_passed ? '已审核' : '已拦截'}</span></div>
      <article className="answer"><h3>最终结果</h3><pre>{result.final_answer}</pre></article>
      <div className="detail-grid">
        <article><h3>执行轨迹</h3><ol>{result.trace.map((item) => <li key={item}>{item}</li>)}</ol></article>
        <article><h3>证据与边界</h3><p>来源：{sources}</p><p>执行模式：{result.execution_mode}</p>{result.model_error && <p>模型回退：{result.model_error}</p>}<p>边界：仅使用本地模拟数据与示例规则。</p></article>
      </div>
      {result.warnings.length > 0 && <article className="warnings"><h3>审核提示</h3><ul>{result.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul></article>}
    </>
  )
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>)
