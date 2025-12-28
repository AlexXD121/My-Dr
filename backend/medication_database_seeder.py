"""
Medication Database Seeder - Populate database with common medications
"""
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from drug_interaction_models import Medication

logger = logging.getLogger(__name__)


class MedicationDatabaseSeeder:
    """Seed database with common medications and their interaction data"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def seed_common_medications(self) -> bool:
        """Seed database with common medications"""
        try:
            medications_data = self._get_common_medications_data()
            
            for med_data in medications_data:
                # Check if medication already exists
                existing = self.db.query(Medication).filter(
                    Medication.name == med_data["name"]
                ).first()
                
                if not existing:
                    medication = Medication(**med_data)
                    self.db.add(medication)
            
            self.db.commit()
            logger.info(f"Successfully seeded {len(medications_data)} medications")
            return True
            
        except Exception as e:
            logger.error(f"Error seeding medications: {e}")
            self.db.rollback()
            return False
    
    def _get_common_medications_data(self) -> List[Dict[str, Any]]:
        """Get data for common medications with interaction information"""
        return [
            # Cardiovascular medications
            {
                "name": "warfarin",
                "brand_names": ["Coumadin", "Jantoven"],
                "drug_class": "anticoagulant",
                "active_ingredients": ["warfarin sodium"],
                "strength": "Various",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "Prevention of blood clots, stroke prevention in atrial fibrillation",
                "contraindications": ["Active bleeding", "Severe liver disease", "Pregnancy"],
                "side_effects": ["Bleeding", "Bruising", "Hair loss", "Skin necrosis"],
                "warnings": ["Regular INR monitoring required", "Many drug interactions", "Dietary vitamin K affects dosing"],
                "interaction_severity_high": ["aspirin", "ibuprofen", "naproxen", "heparin", "clopidogrel"],
                "interaction_severity_moderate": ["acetaminophen", "simvastatin", "omeprazole"],
                "interaction_severity_low": ["multivitamin"]
            },
            {
                "name": "aspirin",
                "brand_names": ["Bayer", "Bufferin", "Ecotrin"],
                "drug_class": "antiplatelet",
                "active_ingredients": ["acetylsalicylic acid"],
                "strength": "81mg, 325mg",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "Pain relief, fever reduction, cardiovascular protection",
                "contraindications": ["Active bleeding", "Severe kidney disease", "Children with viral infections"],
                "side_effects": ["Stomach upset", "Bleeding", "Tinnitus", "Allergic reactions"],
                "warnings": ["Increased bleeding risk", "Stomach ulcer risk", "Reye's syndrome in children"],
                "interaction_severity_high": ["warfarin", "heparin", "methotrexate"],
                "interaction_severity_moderate": ["lisinopril", "furosemide", "prednisone"],
                "interaction_severity_low": ["acetaminophen"]
            },
            {
                "name": "lisinopril",
                "brand_names": ["Prinivil", "Zestril"],
                "drug_class": "ace_inhibitor",
                "active_ingredients": ["lisinopril"],
                "strength": "2.5mg, 5mg, 10mg, 20mg, 40mg",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "High blood pressure, heart failure, post-heart attack",
                "contraindications": ["Pregnancy", "Angioedema history", "Bilateral renal artery stenosis"],
                "side_effects": ["Dry cough", "Dizziness", "Hyperkalemia", "Angioedema"],
                "warnings": ["Monitor kidney function", "Check potassium levels", "Avoid in pregnancy"],
                "interaction_severity_high": ["aliskiren", "sacubitril"],
                "interaction_severity_moderate": ["ibuprofen", "naproxen", "spironolactone", "potassium"],
                "interaction_severity_low": ["hydrochlorothiazide"]
            },
            {
                "name": "metoprolol",
                "brand_names": ["Lopressor", "Toprol-XL"],
                "drug_class": "beta_blocker",
                "active_ingredients": ["metoprolol tartrate", "metoprolol succinate"],
                "strength": "25mg, 50mg, 100mg, 200mg",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "High blood pressure, chest pain, heart failure",
                "contraindications": ["Severe bradycardia", "Heart block", "Cardiogenic shock"],
                "side_effects": ["Fatigue", "Dizziness", "Depression", "Cold hands/feet"],
                "warnings": ["Don't stop suddenly", "Monitor heart rate", "Use caution in diabetes"],
                "interaction_severity_high": ["verapamil", "diltiazem"],
                "interaction_severity_moderate": ["insulin", "epinephrine", "clonidine"],
                "interaction_severity_low": ["acetaminophen"]
            },
            
            # Cholesterol medications
            {
                "name": "atorvastatin",
                "brand_names": ["Lipitor"],
                "drug_class": "statin",
                "active_ingredients": ["atorvastatin calcium"],
                "strength": "10mg, 20mg, 40mg, 80mg",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "High cholesterol, cardiovascular disease prevention",
                "contraindications": ["Active liver disease", "Pregnancy", "Breastfeeding"],
                "side_effects": ["Muscle pain", "Liver enzyme elevation", "Headache", "Nausea"],
                "warnings": ["Monitor liver function", "Watch for muscle symptoms", "Avoid grapefruit juice"],
                "interaction_severity_high": ["clarithromycin", "itraconazole", "cyclosporine"],
                "interaction_severity_moderate": ["diltiazem", "verapamil", "amiodarone"],
                "interaction_severity_low": ["digoxin"]
            },
            {
                "name": "simvastatin",
                "brand_names": ["Zocor"],
                "drug_class": "statin",
                "active_ingredients": ["simvastatin"],
                "strength": "5mg, 10mg, 20mg, 40mg, 80mg",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "High cholesterol, cardiovascular disease prevention",
                "contraindications": ["Active liver disease", "Pregnancy", "Breastfeeding"],
                "side_effects": ["Muscle pain", "Liver enzyme elevation", "Headache", "Nausea"],
                "warnings": ["Monitor liver function", "Watch for muscle symptoms", "80mg dose has restrictions"],
                "interaction_severity_high": ["clarithromycin", "erythromycin", "itraconazole", "ketoconazole"],
                "interaction_severity_moderate": ["diltiazem", "verapamil", "amiodarone", "amlodipine"],
                "interaction_severity_low": ["digoxin"]
            },
            
            # Diabetes medications
            {
                "name": "metformin",
                "brand_names": ["Glucophage", "Fortamet", "Glumetza"],
                "drug_class": "biguanide",
                "active_ingredients": ["metformin hydrochloride"],
                "strength": "500mg, 850mg, 1000mg",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "Type 2 diabetes mellitus",
                "contraindications": ["Severe kidney disease", "Metabolic acidosis", "Diabetic ketoacidosis"],
                "side_effects": ["Nausea", "Diarrhea", "Metallic taste", "Vitamin B12 deficiency"],
                "warnings": ["Hold before contrast procedures", "Monitor kidney function", "Risk of lactic acidosis"],
                "interaction_severity_high": ["contrast_dye", "alcohol"],
                "interaction_severity_moderate": ["furosemide", "nifedipine", "cimetidine"],
                "interaction_severity_low": ["glyburide"]
            },
            
            # Pain medications
            {
                "name": "ibuprofen",
                "brand_names": ["Advil", "Motrin"],
                "drug_class": "nsaid",
                "active_ingredients": ["ibuprofen"],
                "strength": "200mg, 400mg, 600mg, 800mg",
                "dosage_form": "tablet, capsule, liquid",
                "route_of_administration": "oral",
                "indication": "Pain relief, fever reduction, inflammation",
                "contraindications": ["Active bleeding", "Severe heart failure", "Severe kidney disease"],
                "side_effects": ["Stomach upset", "Bleeding", "Kidney problems", "High blood pressure"],
                "warnings": ["Take with food", "Increased cardiovascular risk", "Monitor kidney function"],
                "interaction_severity_high": ["warfarin", "lithium", "methotrexate"],
                "interaction_severity_moderate": ["lisinopril", "furosemide", "prednisone"],
                "interaction_severity_low": ["acetaminophen"]
            },
            {
                "name": "acetaminophen",
                "brand_names": ["Tylenol"],
                "drug_class": "analgesic",
                "active_ingredients": ["acetaminophen"],
                "strength": "325mg, 500mg, 650mg",
                "dosage_form": "tablet, capsule, liquid",
                "route_of_administration": "oral",
                "indication": "Pain relief, fever reduction",
                "contraindications": ["Severe liver disease"],
                "side_effects": ["Rare at therapeutic doses", "Liver damage with overdose"],
                "warnings": ["Maximum 4g per day", "Check other medications for acetaminophen", "Liver toxicity risk"],
                "interaction_severity_high": ["alcohol_chronic"],
                "interaction_severity_moderate": ["warfarin", "phenytoin"],
                "interaction_severity_low": ["ibuprofen"]
            },
            
            # Antibiotics
            {
                "name": "clarithromycin",
                "brand_names": ["Biaxin"],
                "drug_class": "macrolide_antibiotic",
                "active_ingredients": ["clarithromycin"],
                "strength": "250mg, 500mg",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "Bacterial infections",
                "contraindications": ["Hypersensitivity to macrolides", "History of QT prolongation"],
                "side_effects": ["Nausea", "Diarrhea", "Metallic taste", "QT prolongation"],
                "warnings": ["Many drug interactions", "Monitor for arrhythmias", "C. diff risk"],
                "interaction_severity_high": ["simvastatin", "atorvastatin", "digoxin", "warfarin"],
                "interaction_severity_moderate": ["theophylline", "carbamazepine", "cyclosporine"],
                "interaction_severity_low": ["acetaminophen"]
            },
            {
                "name": "amoxicillin",
                "brand_names": ["Amoxil"],
                "drug_class": "penicillin_antibiotic",
                "active_ingredients": ["amoxicillin"],
                "strength": "250mg, 500mg, 875mg",
                "dosage_form": "tablet, capsule, liquid",
                "route_of_administration": "oral",
                "indication": "Bacterial infections",
                "contraindications": ["Penicillin allergy"],
                "side_effects": ["Nausea", "Diarrhea", "Rash", "Allergic reactions"],
                "warnings": ["Complete full course", "Allergic reaction risk", "C. diff risk"],
                "interaction_severity_high": [],
                "interaction_severity_moderate": ["warfarin", "methotrexate"],
                "interaction_severity_low": ["oral_contraceptives"]
            },
            
            # Gastrointestinal medications
            {
                "name": "omeprazole",
                "brand_names": ["Prilosec"],
                "drug_class": "proton_pump_inhibitor",
                "active_ingredients": ["omeprazole"],
                "strength": "10mg, 20mg, 40mg",
                "dosage_form": "capsule",
                "route_of_administration": "oral",
                "indication": "GERD, peptic ulcers, H. pylori eradication",
                "contraindications": ["Hypersensitivity to PPIs"],
                "side_effects": ["Headache", "Nausea", "Diarrhea", "Vitamin B12 deficiency"],
                "warnings": ["Long-term use risks", "Bone fracture risk", "C. diff risk"],
                "interaction_severity_high": ["atazanavir", "nelfinavir"],
                "interaction_severity_moderate": ["clopidogrel", "warfarin", "phenytoin"],
                "interaction_severity_low": ["digoxin"]
            },
            
            # Thyroid medications
            {
                "name": "levothyroxine",
                "brand_names": ["Synthroid", "Levoxyl"],
                "drug_class": "thyroid_hormone",
                "active_ingredients": ["levothyroxine sodium"],
                "strength": "25mcg, 50mcg, 75mcg, 100mcg, 125mcg, 150mcg",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "Hypothyroidism, thyroid cancer",
                "contraindications": ["Untreated adrenal insufficiency", "Acute MI"],
                "side_effects": ["Palpitations", "Insomnia", "Weight loss", "Heat intolerance"],
                "warnings": ["Take on empty stomach", "Many drug interactions", "Monitor TSH"],
                "interaction_severity_high": ["cholestyramine", "colesevelam"],
                "interaction_severity_moderate": ["calcium", "iron", "sucralfate", "coffee"],
                "interaction_severity_low": ["multivitamin"]
            },
            
            # Mental health medications
            {
                "name": "sertraline",
                "brand_names": ["Zoloft"],
                "drug_class": "ssri_antidepressant",
                "active_ingredients": ["sertraline hydrochloride"],
                "strength": "25mg, 50mg, 100mg",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "Depression, anxiety disorders, PTSD, OCD",
                "contraindications": ["MAOI use within 14 days", "Pimozide use"],
                "side_effects": ["Nausea", "Diarrhea", "Insomnia", "Sexual dysfunction"],
                "warnings": ["Suicide risk in young adults", "Serotonin syndrome risk", "Withdrawal symptoms"],
                "interaction_severity_high": ["mao_inhibitors", "pimozide", "linezolid"],
                "interaction_severity_moderate": ["warfarin", "tramadol", "triptans"],
                "interaction_severity_low": ["acetaminophen"]
            },
            
            # Diuretics
            {
                "name": "furosemide",
                "brand_names": ["Lasix"],
                "drug_class": "loop_diuretic",
                "active_ingredients": ["furosemide"],
                "strength": "20mg, 40mg, 80mg",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "Edema, heart failure, hypertension",
                "contraindications": ["Anuria", "Hypersensitivity to sulfonamides"],
                "side_effects": ["Dehydration", "Electrolyte imbalance", "Dizziness", "Hearing loss"],
                "warnings": ["Monitor electrolytes", "Monitor kidney function", "Ototoxicity risk"],
                "interaction_severity_high": ["lithium", "aminoglycosides"],
                "interaction_severity_moderate": ["digoxin", "nsaids", "ace_inhibitors"],
                "interaction_severity_low": ["acetaminophen"]
            },
            {
                "name": "hydrochlorothiazide",
                "brand_names": ["Microzide"],
                "drug_class": "thiazide_diuretic",
                "active_ingredients": ["hydrochlorothiazide"],
                "strength": "12.5mg, 25mg, 50mg",
                "dosage_form": "tablet",
                "route_of_administration": "oral",
                "indication": "Hypertension, edema",
                "contraindications": ["Anuria", "Hypersensitivity to sulfonamides"],
                "side_effects": ["Dizziness", "Electrolyte imbalance", "Photosensitivity", "Hyperuricemia"],
                "warnings": ["Monitor electrolytes", "Sun sensitivity", "Diabetes risk"],
                "interaction_severity_high": ["lithium"],
                "interaction_severity_moderate": ["digoxin", "nsaids", "corticosteroids"],
                "interaction_severity_low": ["acetaminophen"]
            }
        ]
    
    def get_medication_count(self) -> int:
        """Get current count of medications in database"""
        try:
            return self.db.query(Medication).count()
        except Exception as e:
            logger.error(f"Error getting medication count: {e}")
            return 0
    
    def clear_medications(self) -> bool:
        """Clear all medications from database (use with caution)"""
        try:
            self.db.query(Medication).delete()
            self.db.commit()
            logger.info("All medications cleared from database")
            return True
        except Exception as e:
            logger.error(f"Error clearing medications: {e}")
            self.db.rollback()
            return False