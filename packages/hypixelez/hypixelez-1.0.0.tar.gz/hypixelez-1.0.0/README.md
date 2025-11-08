# Hypixelez
### English | [Russian](https://github.com/SerJo2/hypixelez/blob/master/README.ru.md)



A modern Python library for easy interaction with the Hypixel API, specifically designed for SkyBlock profile data.

## Features

- 🔍 **Easy UUID lookup** - Get Minecraft player UUID by username
- 📊 **Comprehensive SkyBlock stats** - Access collections, skills, slayers, and dungeons
- 🎯 **Type hints** - Full type support for better development experience
- 🛡️ **Error handling** - Robust error handling with safe defaults
- 📝 **Logging** - Configurable logging for debugging
- ⚡ **Caching** - Smart caching for UUID lookups
- 🧪 **Tested** - Comprehensive test suite

## Installation

```bash
pip install hypixelez
```
## Quick Start
``` python
from hypixelez import HypixelClient

# Initialize client with your API key
client = HypixelClient(api_key="your-hypixel-api-key")

# Get player UUID
uuid = client.get_uuid_by_name("Neono4ka")

# Get available profiles
profiles = client.get_profile_names_ids_by_id(uuid)
# {'Kiwi': '0b1362a7-43e8-454b-a2ed-6db43ae32f19', ...}

# Fetch profile data
profile_data = client.fetch_profile_info(uuid, "f5791b0c-caf1-4701-aea3-d727ea53a901")

# Access various statistics
print(f"Skill Level: {profile_data.get_skill_level('SKILL_CARPENTRY')}")
print(f"Collection: {profile_data.get_collection('LOG')}")
print(f"Slayer XP: {profile_data.get_slayer_xp('zombie')}")
print(f"Catacombs Level: {profile_data.get_cata_level()}")
```

## Available Methods
### Player Information
```get_global_level()``` - SkyBlock level

```get_global_xp()``` - Current SkyBlock XP

### Skills
```get_skill_level(skill_name)``` - Skill level (0-60)

```get_skill_current_level_xp(skill_name)``` - Current level XP

### Collections
```get_collection(collection_name)``` - Collection count

### Slayers
```get_slayer_stats(slayer_name)``` - List of kills per tier

```get_slayer_stats_by_tier(slayer_name, tier)``` - Kills for specific tier

```get_slayer_xp(slayer_name)``` - Slayer XP

```get_slayer_level(slayer_name)``` - Slayer level

### Dungeons
```get_cata_level()``` - Catacombs level

```get_cata_xp()``` - Catacombs XP

```get_cata_class_level(class_name)``` - Class level

```get_cata_class_xp(class_name)``` - Class XP

## Configuration
``` python
# Enable debug logging
client = HypixelClient(api_key="your-key", debug=True)

# Or disable debug logging (default)
client = HypixelClient(api_key="your-key", debug=False)
```

## Error Handling
All methods return safe defaults (usually 0) when data is not found:

```python
# If skill doesn't exist, returns 0 instead of throwing error
level = profile_data.get_skill_level("NON_EXISTENT_SKILL")  # Returns 0
```

## Getting API Key
1. Visit Hypixel Developer Dashboard
2. Login with your Minecraft account
3. Generate a new API key
4. Use it in your application

## Testing
To run tests, set your API key as environment variable:

```bash
export API_KEY="your-hypixel-api-key"
pytest
```

## Requirements
 - Python 3.9+
 - requests library

## License
MIT License - see LICENSE file for details.

## Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Support
If you encounter any issues or have questions, please open an issue on GitHub.

## ⭐ If this project helped you, please give it a star on GitHub!