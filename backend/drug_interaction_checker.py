"""
Drug Interaction Checker - Core system for analyzing medication interactions
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session
from drug_interaction_models import Medication, DrugInteractionReport, UserMedication

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Drug interaction severity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CONTRAINDICATED = "contraindicated"


class InteractionType(Enum):
    """Types of drug interactions"""
    PHARMACOKINETIC = "pharmacokinetic"  # Affects absorption, distribution, metabolism, excretion
    PHARMACODYNAMIC = "pharmacodynamic"  # Affects drug action at receptor level
    PHARMACEUTICAL = "pharmaceutical"    # Physical/chemical incompatibility
    ADDITIVE = "additive"               # Combined effects
    SYNERGISTIC = "synergistic"         # Enhanced effects
    ANTAGONISTIC = "antagonistic"       # Opposing effects


@dataclass
class InteractionResult:
    """Result of drug interaction analysis"""
    medication_a: str
    medication_b: str
    severity: SeverityLevel
    severity_score: float
    interaction_type: InteractionType
    mechanism: str
    clinical_effects: List[str]
    management_recommendations: List[str]
    contraindicated: bool
    monitoring_required: bool
    evidence_level: str
    risk_factors: List[str]


@dataclass
class MedicationInfo:
    """Standardized medication information"""
    name: str
    generic_name: str
    brand_names: List[str]
    drug_class: str
    active_ingredients: List[str]
    rxcui: Optional[str] = None
    atc_code: Optional[str] = None


class DrugInteractionChecker:
    """
    Comprehensive drug interaction checking system
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.interaction_database = self._load_interaction_database()
        self.drug_classes = self._load_drug_classes()
        self.contraindicated_combinations = self._load_contraindicated_combinations()
        
    def _load_interaction_database(self) -> Dict[str, Any]:
        """Load comprehensive drug interaction database"""
        # In a production system, this would load from a comprehensive database
        # like DrugBank, RxNorm, or commercial interaction databases
        return {
            # High severity interactions
            "high_severity": {
                ("warfarin", "aspirin"): {
                    "mechanism": "Increased bleeding risk due to antiplatelet and anticoagulant effects",
                    "effects": ["Increased bleeding risk", "Hemorrhage", "Bruising"],
                    "management": ["Monitor INR closely", "Consider alternative pain relief", "Watch for bleeding signs"],
                    "evidence": "high"
                },
                ("metformin", "contrast_dye"): {
                    "mechanism": "Risk of lactic acidosis due to kidney function impairment",
                    "effects": ["Lactic acidosis", "Kidney dysfunction", "Metabolic acidosis"],
                    "management": ["Hold metformin 48h before contrast", "Check kidney function", "Resume after normal creatinine"],
                    "evidence": "high"
                },
                ("digoxin", "amiodarone"): {
                    "mechanism": "Amiodarone inhibits digoxin clearance leading to toxicity",
                    "effects": ["Digoxin toxicity", "Arrhythmias", "Nausea", "Visual disturbances"],
                    "management": ["Reduce digoxin dose by 50%", "Monitor digoxin levels", "Watch for toxicity signs"],
                    "evidence": "high"
                },
                ("simvastatin", "clarithromycin"): {
                    "mechanism": "CYP3A4 inhibition increases statin levels causing rhabdomyolysis risk",
                    "effects": ["Rhabdomyolysis", "Muscle pain", "Elevated CK", "Kidney damage"],
                    "management": ["Avoid combination", "Use alternative antibiotic", "Monitor CK levels"],
                    "evidence": "high"
                }
            },
            
            # Moderate severity interactions
            "moderate_severity": {
                ("lisinopril", "ibuprofen"): {
                    "mechanism": "NSAIDs reduce ACE inhibitor effectiveness and increase kidney risk",
                    "effects": ["Reduced blood pressure control", "Kidney function decline", "Fluid retention"],
                    "management": ["Monitor blood pressure", "Check kidney function", "Consider acetaminophen instead"],
                    "evidence": "moderate"
                },
                ("metoprolol", "verapamil"): {
                    "mechanism": "Additive effects on heart rate and blood pressure",
                    "effects": ["Bradycardia", "Hypotension", "Heart block"],
                    "management": ["Monitor heart rate and BP", "Start with lower doses", "Watch for symptoms"],
                    "evidence": "moderate"
                },
                ("levothyroxine", "calcium_carbonate"): {
                    "mechanism": "Calcium binds to levothyroxine reducing absorption",
                    "effects": ["Reduced thyroid hormone levels", "Hypothyroid symptoms"],
                    "management": ["Separate doses by 4 hours", "Monitor TSH levels", "Take levothyroxine on empty stomach"],
                    "evidence": "moderate"
                }
            },
            
            # Low severity interactions
            "low_severity": {
                ("omeprazole", "clopidogrel"): {
                    "mechanism": "PPI may reduce clopidogrel activation",
                    "effects": ["Potentially reduced antiplatelet effect"],
                    "management": ["Consider alternative PPI", "Monitor for cardiovascular events"],
                    "evidence": "low"
                },
                ("atorvastatin", "grapefruit_juice"): {
                    "mechanism": "Grapefruit inhibits CYP3A4 increasing statin levels",
                    "effects": ["Increased statin side effects", "Muscle pain"],
                    "management": ["Avoid large amounts of grapefruit", "Monitor for muscle symptoms"],
                    "evidence": "moderate"
                }
            }
        }
    
    def _load_drug_classes(self) -> Dict[str, List[str]]:
        """Load drug class interaction patterns"""
        return {
            "anticoagulants": ["warfarin", "heparin", "rivaroxaban", "apixaban", "dabigatran"],
            "antiplatelets": ["aspirin", "clopidogrel", "prasugrel", "ticagrelor"],
            "ace_inhibitors": ["lisinopril", "enalapril", "captopril", "ramipril"],
            "beta_blockers": ["metoprolol", "atenolol", "propranolol", "carvedilol"],
            "statins": ["atorvastatin", "simvastatin", "rosuvastatin", "pravastatin"],
            "nsaids": ["ibuprofen", "naproxen", "diclofenac", "celecoxib"],
            "ppis": ["omeprazole", "lansoprazole", "pantoprazole", "esomeprazole"],
            "calcium_channel_blockers": ["amlodipine", "verapamil", "diltiazem", "nifedipine"],
            "diuretics": ["furosemide", "hydrochlorothiazide", "spironolactone", "amiloride"],
            "antibiotics_macrolide": ["clarithromycin", "erythromycin", "azithromycin"]
        }
    
    def _load_contraindicated_combinations(self) -> List[Tuple[str, str]]:
        """Load absolutely contraindicated drug combinations"""
        return [
            ("warfarin", "aspirin_high_dose"),
            ("mao_inhibitors", "ssri_antidepressants"),
            ("simvastatin_high_dose", "clarithromycin"),
            ("metformin", "contrast_dye_high_risk"),
            ("digoxin", "quinidine")
        ]
    
    def standardize_medication_name(self, medication_name: str) -> str:
        """Standardize medication name for consistent matching"""
        # Convert to lowercase and remove common suffixes
        name = medication_name.lower().strip()
        
        # Remove common suffixes
        suffixes_to_remove = [
            " tablet", " capsule", " mg", " mcg", " ml", " extended release",
            " er", " xl", " sr", " cr", " la", " cd", " hcl", " sodium"
        ]
        
        for suffix in suffixes_to_remove:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()
        
        # Handle common name variations
        name_mappings = {
            "acetaminophen": "paracetamol",
            "ibuprofen": "ibuprofen",
            "tylenol": "acetaminophen",
            "advil": "ibuprofen",
            "motrin": "ibuprofen"
        }
        
        return name_mappings.get(name, name)
    
    def get_medication_info(self, medication_name: str) -> Optional[MedicationInfo]:
        """Get standardized medication information"""
        try:
            medication = self.db.query(Medication).filter(
                Medication.name.ilike(f"%{medication_name}%")
            ).first()
            
            if medication:
                return MedicationInfo(
                    name=medication.name,
                    generic_name=medication.name,
                    brand_names=medication.brand_names or [],
                    drug_class=medication.drug_class or "unknown",
                    active_ingredients=medication.active_ingredients or [],
                    rxcui=medication.rxcui,
                    atc_code=medication.atc_code
                )
            
            # If not found in database, create basic info
            standardized_name = self.standardize_medication_name(medication_name)
            return MedicationInfo(
                name=standardized_name,
                generic_name=standardized_name,
                brand_names=[],
                drug_class="unknown",
                active_ingredients=[standardized_name]
            )
            
        except Exception as e:
            logger.error(f"Error getting medication info for {medication_name}: {e}")
            return None
    
    def check_single_interaction(self, med_a: str, med_b: str) -> Optional[InteractionResult]:
        """Check interaction between two specific medications"""
        try:
            # Standardize medication names
            med_a_std = self.standardize_medication_name(med_a)
            med_b_std = self.standardize_medication_name(med_b)
            
            # Check both directions for interaction
            interaction_key = (med_a_std, med_b_std)
            reverse_key = (med_b_std, med_a_std)
            
            # Check high severity interactions first
            for severity, interactions in self.interaction_database.items():
                if interaction_key in interactions:
                    return self._create_interaction_result(
                        med_a, med_b, interactions[interaction_key], severity
                    )
                elif reverse_key in interactions:
                    return self._create_interaction_result(
                        med_a, med_b, interactions[reverse_key], severity
                    )
            
            # Check drug class interactions
            class_interaction = self._check_drug_class_interaction(med_a_std, med_b_std)
            if class_interaction:
                return class_interaction
            
            # No interaction found
            return None
            
        except Exception as e:
            logger.error(f"Error checking interaction between {med_a} and {med_b}: {e}")
            return None
    
    def _create_interaction_result(self, med_a: str, med_b: str, interaction_data: Dict, severity: str) -> InteractionResult:
        """Create InteractionResult from interaction data"""
        severity_mapping = {
            "high_severity": SeverityLevel.HIGH,
            "moderate_severity": SeverityLevel.MODERATE,
            "low_severity": SeverityLevel.LOW
        }
        
        severity_scores = {
            "high_severity": 8.0,
            "moderate_severity": 5.0,
            "low_severity": 2.0
        }
        
        return InteractionResult(
            medication_a=med_a,
            medication_b=med_b,
            severity=severity_mapping.get(severity, SeverityLevel.LOW),
            severity_score=severity_scores.get(severity, 2.0),
            interaction_type=InteractionType.PHARMACOKINETIC,  # Default, would be determined by analysis
            mechanism=interaction_data.get("mechanism", "Unknown mechanism"),
            clinical_effects=interaction_data.get("effects", []),
            management_recommendations=interaction_data.get("management", []),
            contraindicated=severity == "high_severity" and "avoid" in interaction_data.get("management", []),
            monitoring_required=True if severity in ["high_severity", "moderate_severity"] else False,
            evidence_level=interaction_data.get("evidence", "unknown"),
            risk_factors=[]
        )
    
    def _check_drug_class_interaction(self, med_a: str, med_b: str) -> Optional[InteractionResult]:
        """Check for drug class-based interactions"""
        try:
            # Find drug classes for both medications
            class_a = self._get_drug_class(med_a)
            class_b = self._get_drug_class(med_b)
            
            if not class_a or not class_b:
                return None
            
            # Check for known class interactions
            class_interactions = {
                ("anticoagulants", "antiplatelets"): {
                    "severity": SeverityLevel.HIGH,
                    "score": 7.5,
                    "mechanism": "Increased bleeding risk from combined anticoagulant and antiplatelet effects",
                    "effects": ["Increased bleeding risk", "Hemorrhage", "Bruising"],
                    "management": ["Monitor for bleeding", "Consider alternative therapy", "Regular blood tests"]
                },
                ("ace_inhibitors", "nsaids"): {
                    "severity": SeverityLevel.MODERATE,
                    "score": 5.5,
                    "mechanism": "NSAIDs reduce ACE inhibitor effectiveness and increase kidney risk",
                    "effects": ["Reduced blood pressure control", "Kidney function decline"],
                    "management": ["Monitor blood pressure", "Check kidney function", "Consider alternative pain relief"]
                },
                ("beta_blockers", "calcium_channel_blockers"): {
                    "severity": SeverityLevel.MODERATE,
                    "score": 6.0,
                    "mechanism": "Additive effects on heart rate and blood pressure",
                    "effects": ["Bradycardia", "Hypotension", "Heart block"],
                    "management": ["Monitor heart rate and blood pressure", "Start with lower doses"]
                }
            }
            
            # Check both directions
            interaction_key = (class_a, class_b)
            reverse_key = (class_b, class_a)
            
            for key in [interaction_key, reverse_key]:
                if key in class_interactions:
                    interaction = class_interactions[key]
                    return InteractionResult(
                        medication_a=med_a,
                        medication_b=med_b,
                        severity=interaction["severity"],
                        severity_score=interaction["score"],
                        interaction_type=InteractionType.PHARMACODYNAMIC,
                        mechanism=interaction["mechanism"],
                        clinical_effects=interaction["effects"],
                        management_recommendations=interaction["management"],
                        contraindicated=interaction["severity"] == SeverityLevel.HIGH and interaction["score"] >= 8.0,
                        monitoring_required=interaction["severity"] in [SeverityLevel.HIGH, SeverityLevel.MODERATE],
                        evidence_level="moderate",
                        risk_factors=[]
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking drug class interaction: {e}")
            return None
    
    def _get_drug_class(self, medication_name: str) -> Optional[str]:
        """Get drug class for a medication"""
        for drug_class, medications in self.drug_classes.items():
            if medication_name in medications:
                return drug_class
        return None
    
    def check_medication_list(self, medications: List[str], user_id: str = None) -> List[InteractionResult]:
        """Check interactions for a list of medications"""
        interactions = []
        
        try:
            # Check all pairs of medications
            for i in range(len(medications)):
                for j in range(i + 1, len(medications)):
                    interaction = self.check_single_interaction(medications[i], medications[j])
                    if interaction:
                        interactions.append(interaction)
            
            # Sort by severity score (highest first)
            interactions.sort(key=lambda x: x.severity_score, reverse=True)
            
            # Save interaction reports to database if user_id provided
            if user_id:
                self._save_interaction_reports(interactions, user_id)
            
            return interactions
            
        except Exception as e:
            logger.error(f"Error checking medication list: {e}")
            return []
    
    def _save_interaction_reports(self, interactions: List[InteractionResult], user_id: str):
        """Save interaction reports to database"""
        try:
            for interaction in interactions:
                # Get medication IDs
                med_a = self.db.query(Medication).filter(
                    Medication.name.ilike(f"%{interaction.medication_a}%")
                ).first()
                med_b = self.db.query(Medication).filter(
                    Medication.name.ilike(f"%{interaction.medication_b}%")
                ).first()
                
                if not med_a or not med_b:
                    continue
                
                # Check if report already exists
                existing_report = self.db.query(DrugInteractionReport).filter(
                    DrugInteractionReport.user_id == user_id,
                    DrugInteractionReport.medication_a_id == med_a.id,
                    DrugInteractionReport.medication_b_id == med_b.id
                ).first()
                
                if existing_report:
                    # Update existing report
                    existing_report.severity_level = interaction.severity.value
                    existing_report.severity_score = interaction.severity_score
                    existing_report.mechanism = interaction.mechanism
                    existing_report.clinical_effects = interaction.clinical_effects
                    existing_report.management_recommendations = interaction.management_recommendations
                    existing_report.contraindicated = interaction.contraindicated
                    existing_report.monitoring_required = interaction.monitoring_required
                    existing_report.evidence_level = interaction.evidence_level
                    existing_report.generated_at = datetime.now(timezone.utc)
                else:
                    # Create new report
                    report = DrugInteractionReport(
                        user_id=user_id,
                        medication_a_id=med_a.id,
                        medication_b_id=med_b.id,
                        interaction_type=interaction.interaction_type.value,
                        severity_level=interaction.severity.value,
                        severity_score=interaction.severity_score,
                        mechanism=interaction.mechanism,
                        clinical_effects=interaction.clinical_effects,
                        management_recommendations=interaction.management_recommendations,
                        contraindicated=interaction.contraindicated,
                        monitoring_required=interaction.monitoring_required,
                        evidence_level=interaction.evidence_level,
                        risk_factors=interaction.risk_factors,
                        algorithm_version="1.0"
                    )
                    self.db.add(report)
            
            self.db.commit()
            logger.info(f"Saved {len(interactions)} interaction reports for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error saving interaction reports: {e}")
            self.db.rollback()
    
    def get_user_medication_interactions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all drug interactions for a user's current medications"""
        try:
            # Get user's active medications
            user_medications = self.db.query(UserMedication).join(Medication).filter(
                UserMedication.user_id == user_id,
                UserMedication.status == "active"
            ).all()
            
            if len(user_medications) < 2:
                return []
            
            # Extract medication names
            medication_names = [um.medication.name for um in user_medications if um.medication]
            
            # Check interactions
            interactions = self.check_medication_list(medication_names, user_id)
            
            # Format results
            results = []
            for interaction in interactions:
                results.append({
                    "medication_a": interaction.medication_a,
                    "medication_b": interaction.medication_b,
                    "severity": interaction.severity.value,
                    "severity_score": interaction.severity_score,
                    "severity_color": self._get_severity_color(interaction.severity),
                    "mechanism": interaction.mechanism,
                    "clinical_effects": interaction.clinical_effects,
                    "management_recommendations": interaction.management_recommendations,
                    "contraindicated": interaction.contraindicated,
                    "monitoring_required": interaction.monitoring_required,
                    "evidence_level": interaction.evidence_level
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting user medication interactions: {e}")
            return []
    
    def _get_severity_color(self, severity: SeverityLevel) -> str:
        """Get color code for severity level"""
        colors = {
            SeverityLevel.LOW: "#ffc107",        # Yellow
            SeverityLevel.MODERATE: "#fd7e14",   # Orange
            SeverityLevel.HIGH: "#dc3545",       # Red
            SeverityLevel.CONTRAINDICATED: "#6f42c1"  # Purple
        }
        return colors.get(severity, "#6c757d")  # Gray for unknown
    
    def validate_medication_name(self, medication_name: str) -> Dict[str, Any]:
        """Validate and standardize medication name"""
        try:
            standardized_name = self.standardize_medication_name(medication_name)
            
            # Check if medication exists in database
            medication = self.db.query(Medication).filter(
                Medication.name.ilike(f"%{standardized_name}%")
            ).first()
            
            if medication:
                return {
                    "valid": True,
                    "standardized_name": medication.name,
                    "generic_name": medication.name,
                    "brand_names": medication.brand_names or [],
                    "drug_class": medication.drug_class,
                    "suggestions": []
                }
            else:
                # Try to find similar medications
                similar_meds = self.db.query(Medication).filter(
                    Medication.name.ilike(f"%{standardized_name[:3]}%")
                ).limit(5).all()
                
                suggestions = [med.name for med in similar_meds]
                
                return {
                    "valid": False,
                    "standardized_name": standardized_name,
                    "generic_name": None,
                    "brand_names": [],
                    "drug_class": None,
                    "suggestions": suggestions
                }
                
        except Exception as e:
            logger.error(f"Error validating medication name {medication_name}: {e}")
            return {
                "valid": False,
                "error": str(e),
                "suggestions": []
            }