from flask import Blueprint, request, jsonify
from app.models.analysis import db, Analysis, Vulnerability
from app.services.analyzer import analyze_code
from datetime import datetime, timezone

# POST /api/analyze : 코드 받아서 Claude 분석 -> DB 저장 -> id 반환
api_bp = Blueprint('api', __name__)

@api_bp.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    code = data.get('code')
    language = data.get('language')

    # 검증 로직
    if not code or not language:
        return jsonify({'status': 'error', 'message': '코드와 언어를 입력해주세요.'}), 400

    # 요청(code, language) 받음
    result = analyze_code(code, language)
    
    # fallback이면 DB 저장 안하고 에러 메시지 출력
    if result['is_fallback']:
        return jsonify({'status': "error", "message": "AI 분석 서버에 문제가 발생했습니다. 다시 시도해주세요."}), 500

    # 결과를 Analysis, Vulnerability 모델로 DB에 저장
    analysis = Analysis(
        language=language,
        code=code,
        total_risk=result['total_risk'],
        elapsed_time=result['elapsed_time'],
        created_at = datetime.now(timezone.utc)
    )
    # DB에 데이터 추가
    db.session.add(analysis)
    # 트랜잭션 변경사항 반영
    db.session.commit()

    for vul in result['vulnerabilities']:
        vulnerability = Vulnerability(
            analysis_id=analysis.id,
            name=vul['name'],
            severity=vul['severity'],
            line=vul.get('line'),
            description=vul['description'],
            recommendation=vul['recommendation']
        )
        db.session.add(vulnerability)
    
    db.session.commit()
    # 저장된 analysis.id 반환 (GET /api/analysis/<id>로 넘기기 위해)
    return jsonify({'status': "success", 'id': analysis.id})


# GET /api/analysis : 히스토리 목록 조회
@api_bp.route('/analysis', methods=['GET'])
def get_analysis_list():
    # Analysis 전체 최신순 조회
    analyses = Analysis.query.order_by(Analysis.created_at.desc()).all()
    
    return jsonify([analysis.to_dict() for analysis in analyses])


# GET /api/analysis/<id> : 특정 분석 결과 상세 조회
@api_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    # analysis_id로 Analysis 테이블 조회    
    analysis = Analysis.query.get_or_404(analysis_id)
    # 연결된 Vulnerability 목록도 같이 조회
    return jsonify(analysis.to_dict())