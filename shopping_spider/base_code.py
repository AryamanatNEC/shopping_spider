import requests
from bs4 import BeautifulSoup
import csv
import json
from user_input import get_user_input

def format_search_query(search_query):
    formatted_query = search_query.replace("'", '')
    formatted_query = formatted_query.lower()
    formatted_query = formatted_query.replace('"', '')
    formatted_query = formatted_query.replace(' ', '+')

    return formatted_query

def extract_number_from_string(s):
    parts = s.split()
    for i in range(len(parts)):
        if parts[i]=='stars.':
            return parts[i+1]

def get_shopping_data(formatted_query,next_page_url=None):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
        }

        base_url = f"https://www.google.com/search?q={formatted_query}&tbm=shop&gl=ind"
        print(base_url)
        response = requests.get(base_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        ads = []
        shopping_results = []

        while True:
            for el in soup.select(".sh-np__click-target"):
                ad = {
                    "title": el.select_one(".sh-np__product-title").get_text() if el.select_one(".sh-np__product-title") else None,
                    "link": "https://google.com" + el.get("href"),
                    "source": el.select_one(".sh-np__seller-container").get_text() if el.select_one(".sh-np__seller-container") else None,
                    "price": el.select_one(".hn9kf").get_text() if el.select_one(".hn9kf") else None,
                    "delivery": el.select_one(".U6puSd").get_text() if el.select_one(".U6puSd") else None,
                }
                extensions = el.select_one(".rz2LD")
                if extensions:
                    ad["extensions"] = extensions.get_text()
                ads.append(ad)

            for el in soup.select(".sh-dgr__gr-auto"):
                result = {
                    "title": el.select_one("h3.tAxDx").get_text() if el.select_one("h3.tAxDx") else None,
                    "link": el.select_one(".zLPF4b .eaGTj a.shntl")["href"][el.select_one("a.shntl")["href"].index("=") + 1:] if el.select_one(".zLPF4b .eaGTj a.shntl") else None,
                    "source": el.select_one(".IuHnof").get_text().replace(".aULzUe{.*?}.aULzUe::after{.*?}", "") if el.select_one(".IuHnof") else None,
                    "price": el.select_one(".XrAfOe .a8Pemb").get_text() if el.select_one(".XrAfOe .a8Pemb") else None,
                    "rating": None,
                    "reviews": None,
                    "delivery": el.select_one(".vEjMR").get_text() if el.select_one(".vEjMR") else None,
                }

                rating_element = el.select_one(".NzUzee .QIrs8")
                if rating_element:
                    rating_text = rating_element.get_text().strip()
                    #print(rating_text)
                    if "out" in rating_text:
                        try:
                            result["rating"] = float(rating_text.split("out")[0].strip())
                            #print(result["rating"])
                            result["reviews"] = extract_number_from_string(rating_text)
                            #print(result["reviews"])
                        except ValueError:
                            pass

                extensions = el.select_one(".Ib8pOd")
                if extensions:
                    result["extensions"] = extensions.get_text()
                shopping_results.append(result)

            next_page_link = soup.find('a', class_='fl')
            if next_page_link:
                next_page_url = "https://google.com" + next_page_link["href"]
                print(next_page_url)
                response = requests.get(next_page_url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
            else:
                break

        for ad in ads:
            ad.pop("", None)

        for result in shopping_results:
            result.pop("", None)

        return ads, shopping_results

    except Exception as e:
        print(e)

def main():
    search_query = get_user_input()
    formatted_query = format_search_query(search_query) 
    ads_data, shopping_results_data = get_shopping_data(formatted_query) 
    with open("shopping_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["title", "link", "source", "price", "delivery", "extensions"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for ad in ads_data:
            writer.writerow(ad)
        
    with open("shopping_results_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["title", "link", "source", "price", "rating", "reviews", "delivery", "extensions"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in shopping_results_data:
            writer.writerow(result)

    # Save to JSON
    with open("shopping_data.json", "w", encoding="utf-8") as jsonfile:
        json.dump(ads_data, jsonfile, ensure_ascii=False, indent=2)

    with open("shopping_results_data.json", "w", encoding="utf-8") as jsonfile:
        json.dump(shopping_results_data, jsonfile, ensure_ascii=False, indent=2)
   

if __name__ == "__main__":
    main() 