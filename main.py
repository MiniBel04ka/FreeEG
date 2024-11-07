import requests
import json
from datetime import datetime, timezone

params = {
    'locale': 'en-US',
    'country': 'PL',
    'allowCountries': 'PL',
}

response = requests.get(
    'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions',
    params=params
)
data = response.json()

# Get the current time in UTC, making it timezone-aware
current_time = datetime.now(timezone.utc)

results = []

# Loop through all elements and check the promotions
for element in data['data'].get('Catalog', {}).get('searchStore', {}).get('elements', []):
    title = element.get('title')
    page_slug = None
    
    # Try to get pageSlug from offerMappings
    offer_mappings = element.get('offerMappings')
    if offer_mappings and isinstance(offer_mappings, list) and len(offer_mappings) > 0:
        page_slug = offer_mappings[0].get('pageSlug')
    
    # If not found in offerMappings, try to get pageSlug from catalogNs
    if not page_slug:
        catalog_ns = element.get('catalogNs')
        if catalog_ns and 'mappings' in catalog_ns:
            mappings = catalog_ns['mappings']
            if mappings and isinstance(mappings, list):
                page_slug = mappings[0].get('pageSlug')
    
    # Now check if the giveaway is ongoing, with a check for promotions being None
    promotion_data = element.get('promotions')
    if promotion_data and 'promotionalOffers' in promotion_data:
        promotion_data = promotion_data.get('promotionalOffers', [])
        
        # Flag to track if the promotion is active
        promotion_active = False

        for promo in promotion_data:
            for offer in promo.get('promotionalOffers', []):
                start_date = offer.get('startDate')
                end_date = offer.get('endDate')

                # Convert the startDate and endDate to datetime objects
                if start_date and end_date:
                    start_datetime = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                    end_datetime = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

                    # Check if the current time is within the giveaway period
                    if start_datetime <= current_time <= end_datetime:
                        promotion_active = True
                        break
            if promotion_active:
                break
        
        # Add to results if both title, pageSlug, and active promotion are found
        if title and page_slug and promotion_active:
            results.append({
                "title": title,
                "pageSlug": page_slug
            })

# Save the results to a JSON file
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4)
