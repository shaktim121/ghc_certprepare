"""
Test suite for GET /activities endpoint
Follows Arrange-Act-Assert pattern
"""


class TestGetActivities:
    """Tests for retrieving all activities"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        GIVEN the app is running
        WHEN a GET request is made to /activities
        THEN all activities should be returned with status 200
        """
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity in expected_activities:
            assert activity in data


    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """
        GIVEN activities are stored in the database
        WHEN /activities is requested
        THEN each activity contains description, schedule, max_participants, and participants
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_details in data.items():
            for field in required_fields:
                assert field in activity_details, f"Missing field '{field}' in {activity_name}"
            assert isinstance(activity_details["participants"], list)


    def test_get_activities_participants_are_emails(self, client, reset_activities):
        """
        GIVEN activities have participants
        WHEN /activities is requested
        THEN participants should be stored as email addresses
        """
        # Arrange
        expected_participants = {
            "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
            "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
        }
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity, participants in expected_participants.items():
            assert all(
                email in data[activity]["participants"]
                for email in participants
            )


    def test_get_activities_max_participants_is_number(self, client, reset_activities):
        """
        GIVEN activities are defined with capacity
        WHEN /activities is requested
        THEN max_participants should be a positive integer
        """
        # Arrange
        # (setup implicit via reset_activities)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_details in data.items():
            assert isinstance(activity_details["max_participants"], int)
            assert activity_details["max_participants"] > 0
