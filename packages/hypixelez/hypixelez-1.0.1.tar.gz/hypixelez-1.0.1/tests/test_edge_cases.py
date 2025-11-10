"""
Test edge cases and error scenarios
"""

import pytest
from unittest.mock import Mock, patch
from src.hypixelez.hypixel_api import HypixelClient, SkyblockProfileData


class TestEdgeCases:
    """Test edge cases and error handling"""

    @patch("requests.get")
    def test_uuid_not_found(self, mock_get):
        """Test when UUID is not found"""
        mock_response = Mock()
        mock_response.json.return_value = {}  # No 'id' field
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = HypixelClient(api_key="test_key")
        result = client.get_uuid_by_name("NonExistentPlayer")

        assert result is None

    @patch("requests.Session.get")
    def test_network_error(self, mock_session_get):
        """Test network error handling"""
        mock_session_get.side_effect = Exception("Network error")

        client = HypixelClient(api_key="test_key")

        with pytest.raises(Exception, match="Network error"):
            client.fetch_profile_info("test_uuid", "test_profile")

    @patch("requests.Session.get")
    def test_rate_limit_handling(self, mock_session_get):
        """Test rate limit error handling"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": False, "cause": "Key throttle"}
        mock_response.raise_for_status = Mock()
        mock_session_get.return_value = mock_response

        client = HypixelClient(api_key="test_key")

        with pytest.raises(Exception, match="API Error: Key throttle"):
            client.fetch_profile_info("test_uuid", "test_profile")

    def test_empty_profile_handling(self, mock_profile_data):
        """Test methods with empty profile data"""
        # Test that methods don't crash with missing data
        assert mock_profile_data.get_collection("NON_EXISTENT") == 0
        assert mock_profile_data.get_skill_level("NON_EXISTENT_SKILL") == 0
        assert mock_profile_data.get_slayer_xp("NON_EXISTENT_SLAYER") == 0
        assert mock_profile_data.get_cata_level() >= 0  # Should not crash


class TestPerformance:
    """Performance-related tests"""

    def test_uuid_caching(self, mock_requests):
        """Test that UUID caching works"""
        mock_requests["get"].return_value.json.return_value = {"id": "test_uuid"}
        mock_requests["get"].return_value.raise_for_status = Mock()

        client = HypixelClient(api_key="test_key")

        # First call - should make request
        uuid1 = client.get_uuid_by_name("TestPlayer")

        # Second call - should use cache
        uuid2 = client.get_uuid_by_name("TestPlayer")

        assert uuid1 == uuid2 == "test_uuid"
        # Should only make one actual request
        assert mock_requests["get"].call_count == 1
