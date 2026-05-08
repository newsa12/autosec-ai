from anthropic import Anthropic
from flask import current_app
import time
import json

def build_prompt(code: str, language: str) -> str:
    # 선택된 언어에 맞춰 시스템 프롬프트를 동적으로 생성

    traits = {
        "C/C++": "버퍼 오버플로우, 메모리 누수(Memory Leak), 잘못된 포인터 참조, UAF(Use-After-Free) 등 C/C++ 환경에서 발생할 수 있는 치명적인 메모리 손상 취약점과 권한 상승 위협을 철저히 검증하세요.",
        "Java": "NullPointerException, SQL Injection, 안전하지 않은 난수 생성, 동시성(Concurrency) 취약점 및 엔터프라이즈 환경의 보안 위협을 중점적으로 확인하세요.",
        "Python": "SQL Injection, 하드코딩된 비밀번호(Hardcoded Secrets), 안전하지 않은 역직렬화(Insecure Deserialization) 등 백엔드/웹 서비스 취약점을 중점적으로 확인하세요."
    }

    focus = traits.get(language, traits["Python"])

    prompt = f"""당신은 글로벌 IT 기업의 최고 수준 DevSecOps 엔지니어이자 다국어 코드 정적 분석(SAST) 시스템입니다.
    다음 {language} 코드를 분석하고, 발견된 취약점을 반드시 아래의 JSON 형식으로만 응답하세요.
    인사말이나 다른 부연 설명은 절대 출력하지 마세요.
    
    [언어별 분석 중점 사항]
    {focus}

    [입력 코드]
    {code}

    [응답 JSON 포맷 규칙]
    - total_risk: 전체 위험도. HIGH, MEDIUM, LOW 중 하나.
    - severity: 개별 취약점 위험도. HIGH, MEDIUM, LOW 중 하나.
    - line: 취약점 발생한 라인 번호. 모르면 null.

    반드시 아래 형식으로만 응답:
    {{
        "total_risk": "HIGH",
        "vulnerabilities": [
            {{
                "name": "취약점 명칭",
                "severity": "HIGH",
                "line": 15,
                "description": "상세 설명 및 발생 원리",
                "recommendation": "권고 사항"
            }}
        ]
    }}
    """
    return prompt

def analyze_code(code: str, language: str) -> dict:

    # 시작 시간 체크
    start = time.time()
    # API 클라이언트 초기화
    client = Anthropic(api_key=current_app.config['ANTHROPIC_API_KEY'])
    prompt = build_prompt(code, language)
    
    # Claude API 호출
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        result_text = response.content[0].text

        # JSON 파싱 처리
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].strip()

        result = json.loads(result_text)

        vulnerabilities = result.get("vulnerabilities", [])
        severities = [v["severity"] for v in vulnerabilities]
    
        if "HIGH" in severities:
            result["total_risk"] = "HIGH"
        elif "MEDIUM" in severities:
            result["total_risk"] = "MEDIUM"
        elif "LOW" in severities:
            result["total_risk"] = "LOW"
        else:
            result["total_risk"] = "LOW" # 취약점 없으면 LOW

        # 종료 시간 체크 -> elapsed 계산
        elapsed = time.time() - start
        result["elapsed_time"] = elapsed
        result["is_fallback"] = False
        return result


    except Exception as e:
        # Fallback (서버 다운 방지)
        print(f"Analyzer Error: {e}") # 에러 로그(터미널 확인용)
        
        result = {
            "total_risk": "MEDIUM",
            "vulnerabilities": [
                {
                    "name": "AI 분석 실패 (Fallback)",
                    "severity": "MEDIUM",
                    "line": None,
                    "description": f"분석 중 시스템 오류가 발생했습니다. 코드의 길이가 너무 길거나 일시적인 API 장애일 수 있습니다. (에러 원인: {str(e)})",
                    "recommendation": "코드를 분할하여 다시 제출하거나 잠시 후 다시 시도해주세요."
                }
            ]
        }
        elapsed = time.time() - start
        result["elapsed_time"] = elapsed
        result["is_fallback"] = True
        return result    