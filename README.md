# 🛡️ AutoSec AI

> AI 기반 코드 보안 취약점 자동 분석 웹 플랫폼

![분석 결과 화면](https://github.com/user-attachments/assets/c8550be5-349a-4a0a-b1d1-2f233736adf9)

---

## 📌 프로젝트 소개

AutoSec AI는 사용자가 입력한 소스 코드를 Claude AI가 자동으로 분석하여 보안 취약점을 탐지하고, 시각화된 리포트를 제공하는 웹 기반 플랫폼입니다.

소프트웨어 보안 검증 자동화에 관심을 갖고, AI를 활용한 정적 분석(SAST) 도구를 직접 설계·구현한 개인 프로젝트입니다.

---

## ✨ 주요 기능

- **다중 언어 지원**: Python, C/C++, Java 코드 분석
- **AI 취약점 탐지**: Claude API 기반 프롬프트 엔지니어링으로 언어별 취약점 탐지
- **위험도 분류**: 취약점별 HIGH / MEDIUM / LOW 자동 분류
- **라인 하이라이팅**: 취약점 발생 라인을 위험도별 색상으로 표시
- **도넛 차트 시각화**: 위험도 분포 시각화
- **분석 히스토리**: 과거 분석 기록 저장 및 재조회

---

## 🖼️ 스크린샷

### 코드 입력 화면
![분석 결과](https://github.com/user-attachments/assets/c8550be5-349a-4a0a-b1d1-2f233736adf9)

### 분석 결과 - 코드 하이라이팅 및 차트
![코드 입력 화면](https://github.com/user-attachments/assets/8487426e-3029-4f17-9a31-9d8c6bbfce6f)

### 분석 결과 - 취약점 상세 목록
![취약점 상세](https://github.com/user-attachments/assets/6f4838b2-90b5-4a9b-910a-8bf235ec71a8)

---

## 🛠️ 기술 스택

| 분류 | 기술 |
|---|---|
| Backend | Python, Flask, SQLAlchemy |
| Database | SQLite |
| AI | Claude API, 프롬프트 엔지니어링 |
| Frontend | HTML/CSS, Vanilla JS, Chart.js |

---

## ⚙️ 실행 방법

```bash
# 1. 레포 클론
git clone https://github.com/newsa12/autosec-ai.git
cd autosec-ai

# 2. 가상환경 세팅
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. .env 파일 생성
ANTHROPIC_API_KEY=본인의_Claude_API_키
SECRET_KEY=임의의_랜덤_문자열

# 4. 실행
python run.py
```

> Claude API 키는 [console.anthropic.com](https://console.anthropic.com) 에서 발급받을 수 있습니다.
