#!/usr/bin/env python3
"""
Парсер вакансий с hh.ru
"""

import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys

BASE_URL = 'https://hh.ru/search/vacancy'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

def parse_vacancy(item):
    """Парсит одну вакансию из HTML-элемента"""
    try:
        # Название
        title_tag = item.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        title = title_tag.text.strip() if title_tag else 'N/A'
        url = 'https://hh.ru' + title_tag['href'] if title_tag else 'N/A'

        # Компания
        company_tag = item.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
        company = company_tag.text.strip() if company_tag else 'N/A'

        # Зарплата
        salary_tag = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        salary = salary_tag.text.strip() if salary_tag else 'Не указана'

        # Город
        location_tag = item.find('span', {'data-qa': 'vacancy-serp__vacancy-address'})
        location = location_tag.text.strip() if location_tag else 'N/A'

        return {
            'title': title,
            'company': company,
            'salary': salary,
            'location': location,
            'url': url
        }
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        return None

def search_vacancies(query, city='', pages=1, min_salary=None):
    """Поиск вакансий"""
    all_vacancies = []

    for page in range(pages):
        print(f"📄 Парсинг страницы {page + 1}...")

        params = {
            'text': query,
            'area': get_city_code(city) if city else '',
            'page': page,
            'per_page': 20
        }

        try:
            resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, 'html.parser')
            items = soup.find_all('div', {'class': 'vacancy-serp-item'})

            if not items:
                print("⚠️ Вакансий не найдено")
                break

            for item in items:
                vacancy = parse_vacancy(item)
                if vacancy:
                    # Фильтр по зарплате
                    if min_salary:
                        salary_num = extract_salary_number(vacancy['salary'])
                        if salary_num and salary_num < min_salary:
                            continue
                    all_vacancies.append(vacancy)

            time.sleep(1)  # Не дёргаем сервер

        except Exception as e:
            print(f"❌ Ошибка на странице {page}: {e}")
            break

    return all_vacancies

def get_city_code(city_name):
    """Получает код города (упрощённо)"""
    # Основные города
    cities = {
        'москва': 1,
        'санкт-петербург': 2,
        'новосибирск': 4,
        'екатеринбург': 3,
        'казань': 88,
        'нижний новгород': 66,
        'челябинск': 104,
        'самара': 78,
        'омск': 45,
        'ростов-на-дону': 76
    }
    return cities.get(city_name.lower(), 0)

def extract_salary_number(salary_str):
    """Извлекает число из строки зарплаты"""
    import re
    if 'не указана' in salary_str.lower():
        return None
    numbers = re.findall(r'\d+', salary_str.replace(' ', ''))
    if numbers:
        return int(numbers[0])
    return None

def save_to_csv(vacancies, filename):
    """Сохраняет в CSV"""
    df = pd.DataFrame(vacancies)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✅ Сохранено {len(vacancies)} вакансий в {filename}")

def main():
    parser = argparse.ArgumentParser(description='Парсер вакансий с hh.ru')
    parser.add_argument('--query', required=True, help='Поисковый запрос (например, "Python Django")')
    parser.add_argument('--city', default='', help='Город (Москва, СПб и т.д.)')
    parser.add_argument('--pages', type=int, default=3, help='Количество страниц (по умолчанию 3)')
    parser.add_argument('--output', default='vacancies.csv', help='Файл для сохранения')
    parser.add_argument('--min-salary', type=int, help='Минимальная зарплата (фильтр)')

    args = parser.parse_args()

    print(f"🔍 Ищу вакансии: '{args.query}'")
    if args.city:
        print(f"📍 Город: {args.city}")
    print(f"📄 Страниц: {args.pages}")

    vacancies = search_vacancies(
        query=args.query,
        city=args.city,
        pages=args.pages,
        min_salary=args.min_salary
    )

    if vacancies:
        save_to_csv(vacancies, args.output)
        print(f"\n📊 Статистика:")
        print(f"   Всего найдено: {len(vacancies)}")
        salaries = [extract_salary_number(v['salary']) for v in vacancies]
        salaries = [s for s in salaries if s]
        if salaries:
            print(f"   Средняя зарплата: {sum(salaries)//len(salaries):,} ₽")
    else:
        print("❌ Вакансий не найдено")

if __name__ == '__main__':
    main()
