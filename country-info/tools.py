from agents import tool  # ✅ This imports the actual decorator function
import requests
from difflib import get_close_matches

@tool
def get_country_info(country_name: str) -> dict:
    """Get capital, population, languages, flag and map location of a country using RESTCountries API"""
    url = "https://restcountries.com/v3.1/all"
    try:
        res = requests.get(url)
        data = res.json()

        # 🔠 Spelling correction
        country_names = [c["name"]["common"] for c in data]
        closest = get_close_matches(country_name, country_names, n=1)
        if not closest:
            return {"error": "Country not found. Try again."}

        matched = closest[0]
        country_data = next(item for item in data if item["name"]["common"] == matched)

        capital = country_data.get("capital", ["N/A"])[0]
        population = f'{country_data.get("population", 0):,}'
        languages = ", ".join(country_data.get("languages", {}).values())
        flag_url = country_data.get("flags", {}).get("png", "")
        latlng = country_data.get("latlng", [0, 0])
        map_link = f"https://www.google.com/maps/search/?api=1&query={latlng[0]},{latlng[1]}"

        return {
            "country": matched,
            "capital": capital,
            "population": population,
            "languages": languages,
            "flag_url": flag_url,
            "map_link": map_link
        }

    except Exception as e:
        return {"error": str(e)}



# # tools.py
# import os
# from agents import tool
# from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
# from agents.run import RunConfig

 
# import requests
# from difflib import get_close_matches

# @tool
# def get_country_info(country_name: str) -> dict:
#     """Get capital, population, languages, flag and map location of a country using RESTCountries API"""
#     url = "https://restcountries.com/v3.1/all"
#     try:
#         res = requests.get(url)
#         data = res.json()

#         # 🔠 Spelling correction
#         country_names = [c["name"]["common"] for c in data]
#         closest = get_close_matches(country_name, country_names, n=1)
#         if not closest:
#             return {"error": "Country not found. Try again."}

#         matched = closest[0]
#         country_data = next(item for item in data if item["name"]["common"] == matched)

#         capital = country_data.get("capital", ["N/A"])[0]
#         population = f'{country_data.get("population", 0):,}'
#         languages = ", ".join(country_data.get("languages", {}).values())
#         flag_url = country_data.get("flags", {}).get("png", "")
#         latlng = country_data.get("latlng", [0, 0])
#         map_link = f"https://www.google.com/maps/search/?api=1&query={latlng[0]},{latlng[1]}"

#         return {
#             "country": matched,
#             "capital": capital,
#             "population": population,
#             "languages": languages,
#             "flag_url": flag_url,
#             "map_link": map_link
#         }

#     except Exception as e:
#         return {"error": str(e)}
#     except requests.RequestException as e:
#         return {"error": "Network error. Please try again later."}
