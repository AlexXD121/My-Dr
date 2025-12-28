import pytest
from fastapi.testclient import TestClient

class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client: TestClient):
        """Test that health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestChatEndpoints:
    """Test chat-related endpoints."""
    
    def test_chat_endpoint_requires_auth(self, client: TestClient):
        """Test that chat endpoint requires authentication."""
        response = client.post("/chat", json={"message": "Hello"})
        assert response.status_code == 401
    
    def test_chat_with_valid_message(self, client: TestClient, sample_user):
        """Test chat endpoint with valid message."""
        # Mock authentication
        headers = {"Authorization": f"Bearer test_token_{sample_user.id}"}
        response = client.post(
            "/chat",
            json={"message": "I have a headache"},
            headers=headers
        )
        assert response.status_code == 200
        assert "reply" in response.json()

class TestMedicalHistoryEndpoints:
    """Test medical history endpoints."""
    
    def test_get_medical_history(self, client: TestClient, sample_user, sample_medical_record):
        """Test retrieving medical history."""
        headers = {"Authorization": f"Bearer test_token_{sample_user.id}"}
        response = client.get("/medical-history", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1
    
    def test_create_medical_record(self, client: TestClient, sample_user):
        """Test creating a new medical record."""
        headers = {"Authorization": f"Bearer test_token_{sample_user.id}"}
        record_data = {
            "record_type": "visit",
            "title": "Test Visit",
            "description": "Test description",
            "date_recorded": "2024-01-20",
            "healthcare_provider": "Dr. Test"
        }
        response = client.post("/medical-history", json=record_data, headers=headers)
        assert response.status_code == 201
        assert response.json()["title"] == "Test Visit"

class TestSymptomAnalysisEndpoints:
    """Test symptom analysis endpoints."""
    
    def test_analyze_symptoms(self, client: TestClient, sample_user):
        """Test symptom analysis endpoint."""
        headers = {"Authorization": f"Bearer test_token_{sample_user.id}"}
        symptom_data = {
            "symptoms": ["headache", "fever"],
            "severity": 6,
            "duration": "2 days"
        }
        response = client.post("/analyze-symptoms", json=symptom_data, headers=headers)
        assert response.status_code == 200
        assert "urgency_score" in response.json()
        assert "recommendations" in response.json()

class TestDrugInteractionEndpoints:
    """Test drug interaction endpoints."""
    
    def test_check_drug_interactions(self, client: TestClient, sample_user):
        """Test drug interaction checking."""
        headers = {"Authorization": f"Bearer test_token_{sample_user.id}"}
        medication_data = {
            "medications": ["aspirin", "warfarin"]
        }
        response = client.post("/check-interactions", json=medication_data, headers=headers)
        assert response.status_code == 200
        assert "interactions" in response.json()

class TestHealthAnalyticsEndpoints:
    """Test health analytics endpoints."""
    
    def test_get_health_analytics(self, client: TestClient, sample_user):
        """Test health analytics endpoint."""
        headers = {"Authorization": f"Bearer test_token_{sample_user.id}"}
        response = client.get("/health-analytics", headers=headers)
        assert response.status_code == 200
        assert "consultation_stats" in response.json()
        assert "health_trends" in response.json()