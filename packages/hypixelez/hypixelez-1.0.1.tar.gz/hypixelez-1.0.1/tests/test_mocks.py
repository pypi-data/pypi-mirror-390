"""
Tests using mock data
"""

import pytest
from unittest.mock import Mock, patch
from src.hypixelez.hypixel_api import HypixelClient, SkyblockProfileData
from .mocks import *


class TestWithMocks:
    """Test cases using mock data"""

    @patch("requests.get")
    def test_get_uuid_with_mock(self, mock_get):
        """Test UUID lookup with mock data"""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = MOCK_UUID_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Test
        client = HypixelClient(api_key="test_key")
        uuid = client.get_uuid_by_name("Neono4ka")

        # Assertions
        assert uuid == "eca19e2e713d49a98582320229f696ed"
        mock_get.assert_called_once_with(
            "https://api.mojang.com/users/profiles/minecraft/Neono4ka", timeout=10
        )

    @patch("requests.Session.get")
    def test_fetch_profile_with_mock(self, mock_session_get):
        """Test profile fetching with mock data"""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = MOCK_PROFILE_DATA
        mock_response.raise_for_status = Mock()
        mock_session_get.return_value = mock_response

        # Test
        client = HypixelClient(api_key="test_key")
        profile_data = client.fetch_profile_info(
            "eca19e2e713d49a98582320229f696ed", "f5791b0c-caf1-4701-aea3-d727ea53a901"
        )

        # Assertions
        assert isinstance(profile_data, SkyblockProfileData)
        assert profile_data.get_collection("LOG") == 77760
        assert profile_data.get_skill_level("SKILL_CARPENTRY") == 27
        mock_session_get.assert_called_once()

    @patch("requests.Session.get")
    def test_api_error_handling(self, mock_session_get):
        """Test API error handling with mock"""
        # Setup error mock
        mock_response = Mock()
        mock_response.json.return_value = MOCK_ERROR_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_session_get.return_value = mock_response

        # Test
        client = HypixelClient(api_key="invalid_key")

        with pytest.raises(Exception, match="API Error: Invalid API key"):
            client.fetch_profile_info("test_uuid", "test_profile")

    @patch("requests.Session.get")
    def test_missing_data_handling(self, mock_session_get):
        """Test handling of missing data with mock"""
        # Setup empty data mock
        mock_response = Mock()
        mock_response.json.return_value = MOCK_EMPTY_PROFILE
        mock_response.raise_for_status = Mock()
        mock_session_get.return_value = mock_response

        # Test
        client = HypixelClient(api_key="test_key")
        profile_data = client.fetch_profile_info("test_uuid", "test_profile")

        # Should return 0 for missing data, not raise exceptions
        assert profile_data.get_collection("NON_EXISTENT") == 0
        assert profile_data.get_skill_level("NON_EXISTENT_SKILL") == 0
        assert profile_data.get_slayer_xp("NON_EXISTENT_SLAYER") == 0


class TestSkyblockProfileDataWithMocks:
    """Test SkyblockProfileData methods with mock data"""

    def setup_method(self):
        """Setup test with mock data"""
        self.profile_data = SkyblockProfileData(
            MOCK_PROFILE_DATA, "eca19e2e713d49a98582320229f696ed"
        )

    def test_collection_methods(self):
        """Test collection-related methods"""
        assert self.profile_data.get_collection("LOG") == 77760
        assert self.profile_data.get_collection("COAL") == 15000
        assert self.profile_data.get_collection("NON_EXISTENT") == 0

    def test_skill_methods(self):
        """Test skill-related methods"""
        assert self.profile_data.get_skill_level("SKILL_CARPENTRY") == 27
        assert self.profile_data.get_skill_current_level_xp("SKILL_CARPENTRY") == 687291

    def test_slayer_methods(self):
        """Test slayer-related methods"""
        assert self.profile_data.get_slayer_xp("zombie") == 148706
        assert self.profile_data.get_slayer_level("zombie") == 7
        assert self.profile_data.get_slayer_stats("zombie") == [15, 10, 8, 5]
        assert self.profile_data.get_slayer_stats_by_tier("zombie", 1) == 15

    def test_dungeon_methods(self):
        """Test dungeon-related methods"""
        assert self.profile_data.get_cata_level() == 24
        assert self.profile_data.get_cata_xp() == 78802
        assert self.profile_data.get_cata_class_level("berserk") == 23
        assert self.profile_data.get_cata_class_xp("berserk") == 21880

    def test_global_methods(self):
        """Test global level methods"""
        assert self.profile_data.get_global_level() == 169
        assert self.profile_data.get_global_xp() == 15


@pytest.mark.parametrize(
    "xp,expected_level",
    [
        (0, 0),  # No XP = level 0
        (50, 1),  # Exactly at level 1 threshold
        (100, 1),  # Between level 1 and 2
        (14926, 11),  # High XP
        (999999999, 60),  # Max level
    ],
)
def test_skill_level_calculation(xp, expected_level):
    """Test skill level calculation with various XP values"""
    # Create mock data with specific XP
    mock_data = {
        "profile": {
            "members": {
                "test_uuid": {"player_data": {"experience": {"TEST_SKILL": xp}}}
            }
        }
    }

    profile = SkyblockProfileData(mock_data, "test_uuid")
    level = profile.get_skill_level("TEST_SKILL")

    assert level == expected_level
