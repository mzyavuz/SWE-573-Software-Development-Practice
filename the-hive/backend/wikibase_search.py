import requests
import sys

# 1. Configuration
SEARCH_API_URL = "https://www.wikidata.org/w/api.php"
SPARQL_API_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "TheHiveServiceApp/1.0 (community-timebank)" # Wikidata requires a User-Agent

def get_entity_id(search_term):
    """
    Step 1: Search for the term and return the Q-ID of the best match.
    Filters out databases, websites, and other non-conceptual entities.
    """
    params = {
        "action": "wbsearchentities",
        "search": search_term,
        "language": "en",
        "format": "json",
        "type": "item",  # Strictly filter for items (not properties, lexemes, etc.)
        "limit": 5  # Get multiple results to choose from
    }
    
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(SEARCH_API_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data.get("search"):
            # Filter to avoid databases, websites, software, companies, etc.
            skip_keywords = ['database', 'website', 'software', 'company', 'organization', 
                           'web service', 'online', 'application', 'platform', 'record label',
                           'brand', 'corporation', 'enterprise', 'firm', 'business']
            
            for match in data["search"]:
                description = match.get('description', '').lower()
                label = match.get('label', '').lower()
                search_lower = search_term.lower()
                
                # Skip if description contains unwanted keywords (including video games)
                skip_descriptions = skip_keywords + ['video game', 'film', 'movie', 'album', 'song', 
                                                     'television', 'TV series', 'band', 'musical']
                if any(keyword in description for keyword in skip_descriptions):
                    continue
                
                # Prefer exact matches
                if label == search_lower:
                    print(f"Found Entity: {match['label']} ({match['id']}) - {match.get('description', '')}")
                    return match["id"]
                
                # For single-word searches, skip multi-word labels (avoid "Cooking Vinyl" for "cooking")
                label_words = label.split()
                search_words = search_lower.split()
                if len(search_words) == 1 and len(label_words) > 1:
                    # Skip this multi-word result
                    continue
                
                # Otherwise accept if search term is in label
                if search_lower in label:
                    print(f"Found Entity: {match['label']} ({match['id']}) - {match.get('description', '')}")
                    return match["id"]
            
            # If all results were filtered out, return the first one anyway
            best_match = data["search"][0]
            print(f"Found Entity (fallback): {best_match['label']} ({best_match['id']}) - {best_match.get('description', '')}")
            return best_match["id"]
        else:
            print(f"No entity found for '{search_term}'")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Search API: {e}")
        return None

def get_related_tags(entity_id):
    """
    Step 2: Use the Q-ID to find related service concepts via SPARQL (Hybrid approach).
    
    This query finds:
    1. Categories/Parents (P279 ↑): e.g., "Cooking" → "Food preparation", "Skill"
    2. Specializations/Children (P279 ↓): e.g., "Cooking" → "Baking", "Roasting"
    3. Tools/Equipment (P366): e.g., "Gardening" → "Shovel", "Rake"
    4. Practitioners/Roles (P3095): e.g., "Cooking" → "Chef", "Cook"
    5. Products (P1056): e.g., "Sewing" → "Clothing"
    """
    
    sparql_query = f"""
    SELECT DISTINCT ?itemLabel WHERE {{
      
      # Group 1: Broader Categories (What is this service a type of?)
      {{
        wd:{entity_id} wdt:P279 ?item.
      }}
      
      UNION
      
      # Group 2: Specializations (Specific types of this service)
      {{
        ?item wdt:P279 wd:{entity_id}.
      }}
      
      UNION
      
      # Group 3: Tools & Equipment (Things used in this service)
      {{
        ?item wdt:P366 wd:{entity_id}.
      }}
      
      UNION
      
      # Group 4: Roles (Who performs this?)
      {{
        wd:{entity_id} wdt:P3095 ?item.
      }}
      
      UNION
      
      # Group 5: Products (What does this produce?)
      {{
        wd:{entity_id} wdt:P1056 ?item.
      }}
      
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 20
    """

    params = {
        "query": sparql_query,
        "format": "json"
    }
    
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(SPARQL_API_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        results = []
        for result in data["results"]["bindings"]:
            label = result["itemLabel"]["value"]
            
            # Filter out unwanted results:
            # 1. Q-IDs (items without proper labels)
            if label.startswith('Q') and label[1:].isdigit():
                continue
            
            # 2. Lexeme IDs (L followed by numbers)
            if label.startswith('L') and '-' in label:
                continue
            
            # 3. Pure numbers
            if label.isdigit():
                continue
            
            # 4. Very short labels (likely codes or abbreviations)
            if len(label) <= 2:
                continue
            
            results.append(label)
        
        return results

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to SPARQL API: {e}")
        return []

# --- Main Execution ---
if __name__ == "__main__":
    # Change this to test different tags (e.g., "Music", "Computer Science", "Football")
    user_input = "Music" 

    print(f"--- Processing Tag: '{user_input}' ---")
    
    # 1. Get the ID
    q_id = get_entity_id(user_input)
    
    if q_id:
        # 2. Get Suggestions
        suggestions = get_related_tags(q_id)
        
        if suggestions:
            print("\n--- Suggested Semantic Tags ---")
            for tag in suggestions:
                print(f"- {tag}")
        else:
            print("No related suggestions found.")