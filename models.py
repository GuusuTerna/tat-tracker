from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from sla_config import get_sla_hours
from datetime import datetime
import json

db = SQLAlchemy()

class Case(db.Model):
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.String(50))
    case_id = db.Column(db.String(20), unique=True)
    patient_name = db.Column(db.String(100))
    department = db.Column(db.String(50))
    test_name = db.Column(db.String(100))
    test_category = db.Column(db.String(50))
    status = db.Column(db.String(50), default='Not Started')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    result_ready_at = db.Column(db.DateTime)
    
    # Lab phases - Pre Analytical
    sample_collection_start = db.Column(db.DateTime)
    sample_collection_end = db.Column(db.DateTime)
    sample_labeling_start = db.Column(db.DateTime)
    sample_labeling_end = db.Column(db.DateTime)
    sample_transport_start = db.Column(db.DateTime)
    sample_transport_end = db.Column(db.DateTime)
    sample_reception_start = db.Column(db.DateTime)
    sample_reception_end = db.Column(db.DateTime)
    sample_processing_start = db.Column(db.DateTime)
    sample_processing_end = db.Column(db.DateTime)
    
    # Lab phases - Analytical
    analysis_start = db.Column(db.DateTime)
    analysis_end = db.Column(db.DateTime)
    
    # Lab phases - Post Analytical
    review_start = db.Column(db.DateTime)
    review_end = db.Column(db.DateTime)
    validation_start = db.Column(db.DateTime)
    validation_end = db.Column(db.DateTime)
    result_upload_start = db.Column(db.DateTime)
    result_upload_end = db.Column(db.DateTime)
    
    # Radiology phases
    exam_start = db.Column(db.DateTime)
    exam_end = db.Column(db.DateTime)
    post_exam_start = db.Column(db.DateTime)
    post_exam_end = db.Column(db.DateTime)
    
    # Mobile phases
    register_start = db.Column(db.DateTime)
    register_end = db.Column(db.DateTime)
    mobile_collect_start = db.Column(db.DateTime)
    mobile_collect_end = db.Column(db.DateTime)
    transport_to_lab_start = db.Column(db.DateTime)
    transport_to_lab_end = db.Column(db.DateTime)
    deliver_results_start = db.Column(db.DateTime)
    deliver_results_end = db.Column(db.DateTime)
    
    # Histology weekly checkpoints
    fixation_done = db.Column(db.Boolean, default=False)
    fixation_date = db.Column(db.DateTime)
    embedding_done = db.Column(db.Boolean, default=False)
    embedding_date = db.Column(db.DateTime)
    cutting_done = db.Column(db.Boolean, default=False)
    cutting_date = db.Column(db.DateTime)
    staining_done = db.Column(db.Boolean, default=False)
    staining_date = db.Column(db.DateTime)
    histology_notes = db.Column(db.Text)
    
    # Manual durations (JSON)
    manual_durations = db.Column(db.Text, default='{}')
    
    # Calculated fields
    tat_hours = db.Column(db.Float)
    sla_status = db.Column(db.String(20), default='PENDING')
    
    def get_manual_durations_dict(self):
        if self.manual_durations:
            return json.loads(self.manual_durations)
        return {}
    
    def set_manual_duration(self, phase, minutes):
        durations = self.get_manual_durations_dict()
        durations[phase] = minutes
        self.manual_durations = json.dumps(durations)
        db.session.commit()
    
    def get_phase_duration(self, start_field, end_field):
        """Calculate duration in minutes for a phase"""
        start = getattr(self, start_field)
        end = getattr(self, end_field)
        if start and end:
            return (end - start).total_seconds() / 60
        return None
    
    def update_sla_status(self):
        """Update SLA status based on test SLA and current time"""
        if self.result_ready_at:
            end_time = self.result_ready_at
        else:
            end_time = datetime.utcnow()
        
        tat = (end_time - self.created_at).total_seconds() / 3600
        self.tat_hours = round(tat, 2)
        
        sla_hours = get_sla_hours(self.test_name)
        
        if self.result_ready_at:
            if tat <= sla_hours:
                self.sla_status = "ON TIME"
            elif tat <= sla_hours * 1.2:
                self.sla_status = "NEAR DELAY"
            else:
                self.sla_status = "DELAYED"
        else:
            # In progress
            if tat <= sla_hours:
                self.sla_status = "IN PROGRESS"
            else:
                self.sla_status = "DELAYED (ONGOING)"
        
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'visit_id': self.visit_id,
            'case_id': self.case_id,
            'patient_name': self.patient_name,
            'department': self.department,
            'test_name': self.test_name,
            'status': self.status,
            'tat_hours': self.tat_hours,
            'sla_status': self.sla_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'result_ready_at': self.result_ready_at.isoformat() if self.result_ready_at else None
        }
    

# Add these new model classes AFTER your existing Case class

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    action = db.Column(db.String(100))  # e.g., "START_PHASE", "END_PHASE", "MANUAL_DURATION", "CREATE_CASE"
    phase = db.Column(db.String(50))
    details = db.Column(db.Text)  # JSON string with extra info
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'action': self.action,
            'phase': self.phase,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PhaseComment(db.Model):
    __tablename__ = 'phase_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    phase = db.Column(db.String(50))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'phase': self.phase,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SLAConfig(db.Model):
    __tablename__ = 'sla_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(100), unique=True)
    sla_hours = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'test_name': self.test_name,
            'sla_hours': self.sla_hours,
            'is_active': self.is_active
        }    