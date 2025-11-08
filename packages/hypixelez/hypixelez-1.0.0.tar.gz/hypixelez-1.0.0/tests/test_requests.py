from difflib import restore

import pytest

from src.hypixelez.hypixel_api import HypixelClient
from tests.conftest import api_client

def test_get_collection(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"), 
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_collection("LOG")
    assert result == 77760

def test_get_slayer_stats(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_slayer_stats("zombie")
    assert result[0] == 15

def test_get_skill_level(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_skill_level("SKILL_CARPENTRY")
    assert result == 27

def test_get_skill_xp(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_skill_current_level_xp("SKILL_CARPENTRY")
    assert result == 687291

def test_get_cata_level_xp(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_cata_xp()
    assert result == 78802

def test_get_cata_level(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_cata_level()
    assert result == 24

def test_get_cata_class_xp(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_cata_class_xp("berserk")
    assert result == 21880

def test_get_cata_class_level(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_cata_class_level("berserk")
    assert result == 23

def test_get_slayer_xp(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_slayer_xp("zombie")
    assert result == 148706

def test_get_slayer_level(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_slayer_level("zombie")
    assert result == 7

def test_get_slayer_stats_by_tier(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_slayer_stats_by_tier("zombie", 1)
    assert result == 15

def test_get_global_level(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_global_level()
    assert result == 169

def test_get_global_xp(api_client):
    user = api_client.fetch_profile_info(api_client.get_uuid_by_name("Neono4ka"),
                                         "f5791b0c-caf1-4701-aea3-d727ea53a901")
    result = user.get_global_xp()
    assert result == 15

def test_get_profiles_by_uuid(api_client):
    result = api_client.get_profile_names_ids_by_id("eca19e2e713d49a98582320229f696ed")
    assert result == {
        'Kiwi': '0b1362a7-43e8-454b-a2ed-6db43ae32f19',
        'Peach': 'f5791b0c-caf1-4701-aea3-d727ea53a901',
        'Zucchini': 'eca19e2e-713d-49a9-8582-320229f696ed'
    }