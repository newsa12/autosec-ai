// ================================================
// 1. DOM 요소 선택 (자주 쓰는 요소들 미리 변수에 저장)
// ================================================
const newAnalysisBtn = document.getElementById('new-analysis-btn')
const analyzeBtn = document.getElementById('analyze-btn')
const codeInput = document.getElementById('code-input')
const languageSelect = document.getElementById('language-select')
const loadingOverlay = document.getElementById('loading-overlay')
const inputSection = document.getElementById('input-section')
const resultSection = document.getElementById('result-section')
const historyList = document.getElementById('history-list')
const vulnList = document.getElementById('vuln-list')

// Chart.js 인스턴스 (도넛 차트)
let riskChart = null

// ================================================
// 2. 화면 전환 함수
// ================================================
function showInputSection() {
    inputSection.style.display = 'block'
    resultSection.style.display = 'none'
}

function showResultSection() {
    inputSection.style.display = 'none'
    resultSection.style.display = 'block'
}

// ================================================
// 3. 히스토리 목록 불러오기
// ================================================
async function loadHistory() {
    const response = await fetch('/api/analysis')
    const analyses = await response.json()

    // 히스토리 목록 초기화
    historyList.innerHTML = ''

    analyses.forEach(analysis => {
        // 위험도별 색상
        const riskColor = {
            'HIGH': '#ff4444',
            'MEDIUM': '#ffaa00',
            'LOW': '#44bb44'
        }

        // 히스토리 카드 동적 생성
        const card = document.createElement('div')
        card.className = 'history-card'
        card.innerHTML = `
            <div>날짜: ${new Date(analysis.created_at).toLocaleString('ko-KR')}</div>
            <div>언어: ${analysis.language}</div>
            <div style="color: ${riskColor[analysis.total_risk]}">
                위험도: ${analysis.total_risk} | 발견: ${analysis.vul_count}건
            </div>
        `

        // 카드 클릭 시 해당 분석 결과 조회
        card.addEventListener('click', () => {
            loadResult(analysis.id)
        })

        historyList.appendChild(card)
    })
}

// ================================================
// 4. 분석 결과 렌더링
// ================================================
async function loadResult(analysisId) {
    const response = await fetch(`/api/analysis/${analysisId}`)
    const data = await response.json()

    // 요약 정보 렌더링
    document.getElementById('result-language').textContent = data.language
    document.getElementById('result-code').textContent = data.code
    document.getElementById('result-elapsed').textContent = data.elapsed_time.toFixed(2)
    document.getElementById('result-risk').textContent = data.total_risk
    document.getElementById('result-count').textContent = data.vul_count

    const lines = data.code.split('\n')
    const lineNumbers = document.getElementById('line-numbers')
    lineNumbers.innerHTML = lines.map((_, i) => `<span>${i+1}</span>`).join('')

    // 도넛 차트 렌더링
    renderChart(data.vulnerabilities)

    // 취약점 목록 렌더링
    renderVulnList(data.vulnerabilities)

    // 결과 화면으로 전환
    showResultSection()
}

// ================================================
// 5. 도넛 차트 렌더링 (Chart.js)
// ================================================
function renderChart(vulnerabilities) {
    const counts = { HIGH: 0, MEDIUM: 0, LOW: 0 }

    vulnerabilities.forEach(vuln => {
        counts[vuln.severity]++
    })

    // 기존 차트 있으면 제거 (히스토리 클릭할 때마다 새로 그려야 해서)
    if (riskChart) {
        riskChart.destroy()
    }

    const ctx = document.getElementById('risk-chart').getContext('2d')
    riskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['HIGH', 'MEDIUM', 'LOW'],
            datasets: [{
                data: [counts.HIGH, counts.MEDIUM, counts.LOW],
                backgroundColor: ['#ff4444', '#ffaa00', '#44bb44']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    })
}

// ================================================
// 6. 취약점 목록 렌더링 (아코디언)
// ================================================
function escapeHtml(str) {
    // XSS 방지: 사용자 입력값의 HTML 특수문자 이스케이프
    if (!str) return ''
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
}

function renderVulnList(vulnerabilities) {
    vulnList.innerHTML = ''

    vulnerabilities.forEach((vuln, index) => {
        const severityColor = {
            'HIGH': '#ff4444',
            'MEDIUM': '#ffaa00',
            'LOW': '#44bb44'
        }

        const item = document.createElement('div')
        item.className = 'vuln-item'
        item.innerHTML = `
            <div class="vuln-header" onclick="toggleVuln(${index})">
                <span>${escapeHtml(vuln.name)}</span>
                <span style="color: ${severityColor[vuln.severity]}">${vuln.severity}</span>
                <span>${vuln.line ? `line: ${vuln.line}` : '라인 불명'}</span>
            </div>
            <div class="vuln-body" id="vuln-body-${index}" style="display:none;">
                <p><strong>설명:</strong> ${escapeHtml(vuln.description)}</p>
                <p><strong>권고사항:</strong> ${escapeHtml(vuln.recommendation)}</p>
            </div>
        `
        vulnList.appendChild(item)
    })
}

// 아코디언 토글
function toggleVuln(index) {
    const body = document.getElementById(`vuln-body-${index}`)
    body.style.display = body.style.display === 'none' ? 'block' : 'none'
}

// ================================================
// 7. 분석 요청 (핵심 로직)
// ================================================
analyzeBtn.addEventListener('click', async () => {
    const code = codeInput.value.trim()
    const language = languageSelect.value

    // 입력값 검증
    if (!code) {
        alert('코드를 입력해주세요.')
        return
    }

    // 로딩 오버레이 표시
    loadingOverlay.style.display = 'flex'

    try {
        // POST /api/analyze 요청
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, language })
        })

        const data = await response.json()

        if (data.status === 'success') {
            // 히스토리 갱신
            await loadHistory()
            // 결과 화면 렌더링
            await loadResult(data.id)
        } else {
            alert(data.message)
        }

    } catch (error) {
        alert('서버 연결에 실패했습니다. 다시 시도해주세요.')
    } finally {
        // 성공/실패 관계없이 로딩 오버레이 숨김
        loadingOverlay.style.display = 'none'
    }
})

// ================================================
// 8. 새 분석 버튼
// ================================================
newAnalysisBtn.addEventListener('click', () => {
    codeInput.value = ''
    showInputSection()
})

// ================================================
// 9. 페이지 로드 시 히스토리 불러오기
// ================================================
document.addEventListener('DOMContentLoaded', () => {
    loadHistory()
})