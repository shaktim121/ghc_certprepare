"""
Test suite for POST /activities/{activity_name}/signup endpoint
Follows Arrange-Act-Assert pattern
"""


class TestSignupForActivity:
    """Tests for signing up a student for an activity"""

    def test_signup_new_participant_success(self, client, reset_activities):
        """
        GIVEN a student is not signed up for an activity
        WHEN the signup endpoint is called with a valid activity and email
        THEN the student should be added and a success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in data["message"]
        assert new_email in data["message"]


    def test_signup_adds_participant_to_activity_list(self, client, reset_activities):
        """
        GIVEN a student signs up successfully
        WHEN checking the activity's participant list
        THEN the new participant should be in the list
        """
        # Arrange
        from app import activities
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert new_email in activities[activity_name]["participants"]


    def test_signup_duplicate_email_returns_error(self, client, reset_activities):
        """
        GIVEN a student is already signed up for an activity
        WHEN attempting to sign up again with the same email
        THEN a 400 error should be returned
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in data["detail"]


    def test_signup_invalid_activity_returns_404(self, client, reset_activities):
        """
        GIVEN an activity does not exist
        WHEN attempting to sign up for it
        THEN a 404 error should be returned
        """
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in data["detail"]


    def test_signup_missing_email_returns_validation_error(self, client, reset_activities):
        """
        GIVEN the email parameter is not provided
        WHEN attempting to sign up
        THEN a validation error (422) should be returned
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert
        assert response.status_code == 422


    def test_signup_multiple_activities_same_email(self, client, reset_activities):
        """
        GIVEN a student can sign up for multiple different activities
        WHEN signing up for different activities
        THEN all signups should succeed
        """
        # Arrange
        from app import activities
        email = "multistudent@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class"]
        
        # Act
        responses = []
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            responses.append(response)
        
        # Assert
        for response in responses:
            assert response.status_code == 200
        
        for activity in activities_to_join:
            assert email in activities[activity]["participants"]
