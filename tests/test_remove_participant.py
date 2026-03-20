"""
Test suite for DELETE /activities/{activity_name}/participants/{email} endpoint
Follows Arrange-Act-Assert pattern
"""


class TestRemoveParticipant:
    """Tests for removing a participant from an activity"""

    def test_remove_participant_success(self, client, reset_activities):
        """
        GIVEN a participant is signed up for an activity
        WHEN the DELETE endpoint is called
        THEN the participant should be removed and a success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in data["message"]
        assert email_to_remove in data["message"]


    def test_remove_participant_removes_from_list(self, client, reset_activities):
        """
        GIVEN a participant is in an activity
        WHEN removing them via DELETE
        THEN they should no longer appear in the activity's participant list
        """
        # Arrange
        from app import activities
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert email_to_remove not in activities[activity_name]["participants"]


    def test_remove_nonexistent_participant_returns_404(self, client, reset_activities):
        """
        GIVEN a participant is not signed up for an activity
        WHEN attempting to remove them
        THEN a 404 error should be returned
        """
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "notmember@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "not found" in data["detail"]


    def test_remove_from_invalid_activity_returns_404(self, client, reset_activities):
        """
        GIVEN an activity does not exist
        WHEN attempting to remove a participant from it
        THEN a 404 error should be returned
        """
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants/{email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in data["detail"]


    def test_remove_all_participants_clears_list(self, client, reset_activities):
        """
        GIVEN an activity has multiple participants
        WHEN removing all of them sequentially
        THEN the participants list should become empty
        """
        # Arrange
        from app import activities
        activity_name = "Chess Club"
        participants_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        for email in participants_to_remove:
            response = client.delete(
                f"/activities/{activity_name}/participants/{email}"
            )
            assert response.status_code == 200
        
        # Assert
        assert len(activities[activity_name]["participants"]) == 0


    def test_remove_participant_undo_signup(self, client, reset_activities):
        """
        GIVEN a participant has been removed
        WHEN they sign up again
        THEN they should be successfully re-added
        """
        # Arrange
        from app import activities
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act: First remove
        delete_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert delete_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        
        # Act: Then signup again
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
