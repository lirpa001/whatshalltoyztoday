from flask import Flask, render_template, send_file
import requests
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from datetime import datetime
import os

app = Flask(__name__)

def parse_minguo_date(date_str):
    """Convert a date string from Minguo format to Gregorian format."""
    try:
        parts = date_str.split('年')
        year = int(parts[0]) + 1911  # 民国年 + 1911 = 公历年
        month_day = parts[1].split('月')
        month = int(month_day[0])
        day = int(month_day[1].split('日')[0])
        return datetime(year, month, day)
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None

@app.route('/')
def home():
    try:
        # Fetch the page content
        url = "https://www.tcd.moj.gov.tw/14456/14612/941547/Lpsimplelist"
        response = requests.get(url)
        response.raise_for_status()

        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the menu links
        menu_links = []
        for link in soup.select('.list ul li a'):
            text = link.text.strip()
            if "收容人膳食菜單一週表" in text:
                menu_links.append((text, link['href']))

        # Find the current week's menu link
        today = datetime.today()
        current_week_link = None
        for text, link in menu_links:
            try:
                date_range = text.split('(')[1].split(')')[0].split('~')
                start_date = parse_minguo_date(date_range[0].strip())
                end_date = parse_minguo_date(date_range[1].strip())
                if start_date and end_date and start_date <= today <= end_date:
                    current_week_link = link
                    break
            except Exception as e:
                print(f"Error parsing date: {e}")

        if not current_week_link:
            return "Failed to load menu"

        # Download the PDF file
        pdf_url = f"https://www.tcd.moj.gov.tw{current_week_link}"
        pdf_response = requests.get(pdf_url)
        pdf_path = "menu.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_response.content)

        # Convert PDF to images
        images = convert_from_path(pdf_path)
        if not images:
            return "Failed to convert PDF to images"

        # Save the first image (assuming the menu is on the first page)
        image_path = "static/menu.png"
        images[0].save(image_path, "PNG")

        return render_template('index.html', image_path=image_path)

    except Exception as e:
        print(f"Error: {e}")
        return "Failed to load menu"

if __name__ == '__main__':
    app.run(debug=True)
