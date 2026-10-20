"""
Batch collector for public Pakistani-context documents across diverse domains.
Strictly checks robots.txt and logs all sources to data/sources.csv.
"""

import os
import sys
import time
import logging

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrape import fetch_article, log_source_entry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("collect")

# Comprehensive targets covering the exact 20 categories and diverse Pakistani domains
PUBLIC_TARGETS = [
    # 1. Politics & Government
    {"url": "https://en.wikipedia.org/wiki/Government_of_Pakistan", "source": "Wikipedia", "domain": "Politics", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Parliament_of_Pakistan", "source": "Wikipedia", "domain": "Politics", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/List_of_political_parties_in_Pakistan", "source": "Wikipedia", "domain": "Politics", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Prime_Minister_of_Pakistan", "source": "Wikipedia", "domain": "Politics", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Cabinet_of_Pakistan", "source": "Wikipedia", "domain": "Politics", "lang": "en"},
    
    # 2. Economy & Finance (MONEY, PERCENT, ORG, GOV_BODY)
    {"url": "https://en.wikipedia.org/wiki/Economy_of_Pakistan", "source": "Wikipedia", "domain": "Economy", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/State_Bank_of_Pakistan", "source": "Wikipedia", "domain": "Economy", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Pakistan_Stock_Exchange", "source": "Wikipedia", "domain": "Economy", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Federal_Board_of_Revenue", "source": "Wikipedia", "domain": "Economy", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Pakistani_rupee", "source": "Wikipedia", "domain": "Economy", "lang": "en"},

    # 3. Judiciary & Law (COURT_LEGAL_BODY, LAW_ACT)
    {"url": "https://en.wikipedia.org/wiki/Supreme_Court_of_Pakistan", "source": "Wikipedia", "domain": "Legal", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Constitution_of_Pakistan", "source": "Wikipedia", "domain": "Legal", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Pakistan_Penal_Code", "source": "Wikipedia", "domain": "Legal", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Lahore_High_Court", "source": "Wikipedia", "domain": "Legal", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Sindh_High_Court", "source": "Wikipedia", "domain": "Legal", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Islamabad_High_Court", "source": "Wikipedia", "domain": "Legal", "lang": "en"},

    # 4. Geography, Cities & Regions (CITY, PROVINCE_REGION, COUNTRY)
    {"url": "https://en.wikipedia.org/wiki/Administrative_units_of_Pakistan", "source": "Wikipedia", "domain": "Geography", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Karachi", "source": "Wikipedia", "domain": "Geography", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Lahore", "source": "Wikipedia", "domain": "Geography", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Islamabad", "source": "Wikipedia", "domain": "Geography", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Peshawar", "source": "Wikipedia", "domain": "Geography", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Quetta", "source": "Wikipedia", "domain": "Geography", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Gilgit-Baltistan", "source": "Wikipedia", "domain": "Geography", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Azad_Kashmir", "source": "Wikipedia", "domain": "Geography", "lang": "en"},

    # 5. Landmarks & Facilities (LANDMARK_FACILITY)
    {"url": "https://en.wikipedia.org/wiki/Minar-e-Pakistan", "source": "Wikipedia", "domain": "Landmarks", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Badshahi_Mosque", "source": "Wikipedia", "domain": "Landmarks", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Jinnah_International_Airport", "source": "Wikipedia", "domain": "Landmarks", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Allama_Iqbal_International_Airport", "source": "Wikipedia", "domain": "Landmarks", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/National_Stadium,_Karachi", "source": "Wikipedia", "domain": "Landmarks", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Gaddafi_Stadium", "source": "Wikipedia", "domain": "Landmarks", "lang": "en"},

    # 6. Sports & Teams (SPORTS_TEAM, EVENT)
    {"url": "https://en.wikipedia.org/wiki/Pakistan_national_cricket_team", "source": "Wikipedia", "domain": "Sports", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Pakistan_Super_League", "source": "Wikipedia", "domain": "Sports", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Karachi_Kings", "source": "Wikipedia", "domain": "Sports", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Lahore_Qalandars", "source": "Wikipedia", "domain": "Sports", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Islamabad_United", "source": "Wikipedia", "domain": "Sports", "lang": "en"},

    # 7. Education & Institutions (EDUCATIONAL_INSTITUTION)
    {"url": "https://en.wikipedia.org/wiki/Higher_Education_Commission_(Pakistan)", "source": "Wikipedia", "domain": "Education", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Lahore_University_of_Management_Sciences", "source": "Wikipedia", "domain": "Education", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Quaid-i-Azam_University", "source": "Wikipedia", "domain": "Education", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/NED_University_of_Engineering_and_Technology", "source": "Wikipedia", "domain": "Education", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Institute_of_Business_Administration,_Karachi", "source": "Wikipedia", "domain": "Education", "lang": "en"},

    # 8. Media Outlets (MEDIA_OUTLET)
    {"url": "https://en.wikipedia.org/wiki/Media_of_Pakistan", "source": "Wikipedia", "domain": "Media", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Dawn_(newspaper)", "source": "Wikipedia", "domain": "Media", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/The_Express_Tribune", "source": "Wikipedia", "domain": "Media", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Geo_News", "source": "Wikipedia", "domain": "Media", "lang": "en"},
    {"url": "https://en.wikipedia.org/wiki/Pakistan_Television_Corporation", "source": "Wikipedia", "domain": "Media", "lang": "en"},

    # 9. Urdu Script (10-15% of total, for multilingual robustness)
    {"url": "https://ur.wikipedia.org/wiki/%D9%BE%D8%A7%DA%A9%D8%B3%D8%AA%D8%A7%D9%86", "source": "Urdu Wikipedia", "domain": "General", "lang": "ur"},
    {"url": "https://ur.wikipedia.org/wiki/%D8%AD%DA%A9%D9%88%D9%85%D8%AA_%D9%BE%D8%A7%DA%A9%D8%B3%D8%AA%D8%A7%D9%86", "source": "Urdu Wikipedia", "domain": "Politics", "lang": "ur"},
    {"url": "https://ur.wikipedia.org/wiki/%D8%B9%D8%AF%D8%A7%D9%84%D8%AA_%D8%B9%D8%B8%D9%85%DB%8C%D9%B4_%D9%BE%D8%A7%DA%A9%D8%B3%D8%AA%D8%A7%D9%86", "source": "Urdu Wikipedia", "domain": "Legal", "lang": "ur"},
    {"url": "https://ur.wikipedia.org/wiki/%DA%A9%D8%B1%D8%A7%DA%86%DB%8C", "source": "Urdu Wikipedia", "domain": "Geography", "lang": "ur"},
    {"url": "https://ur.wikipedia.org/wiki/%D9%BE%D8%A7%DA%A9%D8%B3%D8%AA%D8%A7%D9%86_%D8%B3%D9%BE%D8%B1_%D9%84%DB%8C%DA%AF", "source": "Urdu Wikipedia", "domain": "Sports", "lang": "ur"}
]

def run_batch_collection(limit: int = None):
    targets = PUBLIC_TARGETS[:limit] if limit else PUBLIC_TARGETS
    logger.info(f"Starting batch collection of {len(targets)} public resources...")
    success_count = 0
    
    for item in targets:
        logger.info(f"Processing: {item['url']} ({item['domain']} / {item['lang']})")
        doc = fetch_article(
            url=item["url"],
            source_name=item["source"],
            domain_category=item["domain"],
            language=item["lang"]
        )
        if doc:
            success_count += 1
            
    logger.info(f"Batch collection finished. Successfully fetched {success_count}/{len(targets)} documents.")

if __name__ == "__main__":
    max_items = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_batch_collection(max_items)
