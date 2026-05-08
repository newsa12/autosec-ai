from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Analysis(db.Model):
    __tablename__ = 'analysis'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    elapsed_time = db.Column(db.Float, nullable=False)
    language = db.Column(db.String(50), nullable=False)
    code = db.Column(db.Text, nullable=False)
    total_risk = db.Column(db.String(10), nullable=False)

    vulnerabilities = db.relationship('Vulnerability', backref='analysis', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'elapsed_time': self.elapsed_time,
            'language': self.language,
            'code': self.code,
            'total_risk': self.total_risk,
            'vul_count': len(self.vulnerabilities),
            'vulnerabilities': [v.to_dict() for v in self.vulnerabilities]
        }

class Vulnerability(db.Model):
    __tablename__ = 'vulnerability'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(10), nullable=False)
    line = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=False)
    recommendation = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'name': self.name,
            'severity': self.severity,
            'line': self.line,
            'description': self.description,
            'recommendation': self.recommendation
        }