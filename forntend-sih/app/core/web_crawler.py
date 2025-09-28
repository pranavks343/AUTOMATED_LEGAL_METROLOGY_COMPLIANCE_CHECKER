"""
Web Crawling APIs for Major E-commerce Platforms
Automated data acquisition for Legal Metrology compliance checking
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse, parse_qs
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ProductData:
    """Structured product data from e-commerce platforms"""
    
    # Basic product info
    title: str
    brand: Optional[str] = None
    price: Optional[float] = None
    mrp: Optional[float] = None
    description: Optional[str] = None
    
    # Legal Metrology fields
    net_quantity: Optional[str] = None
    manufacturer: Optional[str] = None
    country_of_origin: Optional[str] = None
    mfg_date: Optional[str] = None
    expiry_date: Optional[str] = None
    
    # E-commerce metadata
    platform: Optional[str] = None
    seller: Optional[str] = None
    product_url: Optional[str] = None
    image_urls: List[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    
    # Compliance metadata
    extracted_at: Optional[str] = None
    compliance_score: Optional[float] = None
    issues_found: List[str] = None
    
    def __post_init__(self):
        if self.image_urls is None:
            self.image_urls = []
        if self.issues_found is None:
            self.issues_found = []

class EcommerceCrawler:
    """Comprehensive web crawler for major Indian e-commerce platforms"""
    
    def __init__(self):
        """Initialize the e-commerce crawler with platform configurations"""
        
        # Platform configurations
        self.platforms = {
            'amazon': {
                'name': 'Amazon India',
                'base_url': 'https://www.amazon.in',
                'search_url': 'https://www.amazon.in/s?k={query}&ref=nb_sb_noss',
                'rate_limit': 2.0,  # seconds between requests
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            },
            'flipkart': {
                'name': 'Flipkart',
                'base_url': 'https://www.flipkart.com',
                'search_url': 'https://www.flipkart.com/search?q={query}',
                'rate_limit': 2.0,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5'
                }
            },
            'myntra': {
                'name': 'Myntra',
                'base_url': 'https://www.myntra.com',
                'search_url': 'https://www.myntra.com/{query}',
                'rate_limit': 2.0,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            },
            'nykaa': {
                'name': 'Nykaa',
                'base_url': 'https://www.nykaa.com',
                'search_url': 'https://www.nykaa.com/search/result/?q={query}',
                'rate_limit': 2.0,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            }
        }
        
        # Initialize session
        self.session = requests.Session()
        self.last_request_time = {}
        
        # Chrome driver options for Selenium (for JavaScript-heavy sites)
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        logger.info("EcommerceCrawler initialized with support for Amazon, Flipkart, Myntra, and Nykaa")
    
    def _respect_rate_limit(self, platform: str):
        """Respect rate limiting for the platform"""
        if platform in self.last_request_time:
            elapsed = time.time() - self.last_request_time[platform]
            rate_limit = self.platforms[platform]['rate_limit']
            if elapsed < rate_limit:
                sleep_time = rate_limit - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.last_request_time[platform] = time.time()
    
    def _make_request(self, url: str, platform: str, use_selenium: bool = False) -> Optional[str]:
        """Make HTTP request with proper headers and rate limiting"""
        try:
            self._respect_rate_limit(platform)
            
            if use_selenium:
                return self._selenium_request(url)
            else:
                headers = self.platforms[platform]['headers']
                response = self.session.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                return response.text
                
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    def _selenium_request(self, url: str) -> Optional[str]:
        """Make request using Selenium for JavaScript-heavy pages"""
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            return driver.page_source
            
        except Exception as e:
            logger.error(f"Selenium request failed for {url}: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def search_products(self, query: str, platform: str = 'amazon', max_results: int = 50) -> List[ProductData]:
        """Search for products on specified e-commerce platform"""
        
        if platform not in self.platforms:
            raise ValueError(f"Unsupported platform: {platform}")
        
        logger.info(f"Searching for '{query}' on {self.platforms[platform]['name']}")
        
        # Platform-specific search implementations
        if platform == 'amazon':
            return self._search_amazon(query, max_results)
        elif platform == 'flipkart':
            return self._search_flipkart(query, max_results)
        elif platform == 'myntra':
            return self._search_myntra(query, max_results)
        elif platform == 'nykaa':
            return self._search_nykaa(query, max_results)
        else:
            logger.warning(f"Search not implemented for platform: {platform}")
            return []
    
    def _search_amazon(self, query: str, max_results: int) -> List[ProductData]:
        """Search Amazon India for products"""
        products = []
        
        try:
            search_url = self.platforms['amazon']['search_url'].format(query=query.replace(' ', '+'))
            html = self._make_request(search_url, 'amazon')
            
            if not html:
                return products
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find product containers
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for container in product_containers[:max_results]:
                try:
                    product = self._extract_amazon_product(container)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Failed to extract Amazon product: {e}")
                    continue
            
            logger.info(f"Extracted {len(products)} products from Amazon")
            
        except Exception as e:
            logger.error(f"Amazon search failed: {e}")
        
        return products
    
    def _extract_amazon_product(self, container) -> Optional[ProductData]:
        """Extract product data from Amazon product container"""
        try:
            # Product title
            title_elem = container.find('h2', class_='a-size-mini')
            if not title_elem:
                title_elem = container.find('span', class_='a-size-medium')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
            
            # Product URL
            link_elem = container.find('a', class_='a-link-normal')
            product_url = None
            if link_elem and link_elem.get('href'):
                product_url = urljoin(self.platforms['amazon']['base_url'], link_elem['href'])
            
            # Price information
            price = None
            mrp = None
            price_elem = container.find('span', class_='a-price-whole')
            if price_elem:
                price_text = price_elem.get_text(strip=True).replace(',', '')
                try:
                    price = float(price_text)
                except ValueError:
                    pass
            
            # MRP (strikethrough price)
            mrp_elem = container.find('span', class_='a-price-was')
            if mrp_elem:
                mrp_text = mrp_elem.get_text(strip=True).replace('₹', '').replace(',', '')
                try:
                    mrp = float(mrp_text)
                except ValueError:
                    pass
            
            # Image URL
            img_elem = container.find('img', class_='s-image')
            image_urls = []
            if img_elem and img_elem.get('src'):
                image_urls.append(img_elem['src'])
            
            # Rating
            rating = None
            rating_elem = container.find('span', class_='a-icon-alt')
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    try:
                        rating = float(rating_match.group(1))
                    except ValueError:
                        pass
            
            return ProductData(
                title=title,
                price=price,
                mrp=mrp,
                product_url=product_url,
                image_urls=image_urls,
                platform='amazon',
                rating=rating,
                extracted_at=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
        except Exception as e:
            logger.error(f"Failed to extract Amazon product data: {e}")
            return None
    
    def _search_flipkart(self, query: str, max_results: int) -> List[ProductData]:
        """Search Flipkart for products"""
        products = []
        
        try:
            search_url = self.platforms['flipkart']['search_url'].format(query=query.replace(' ', '%20'))
            html = self._make_request(search_url, 'flipkart', use_selenium=True)
            
            if not html:
                return products
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find product containers (Flipkart uses dynamic classes)
            product_containers = soup.find_all('div', class_=re.compile('.*_1AtVbE.*'))
            if not product_containers:
                product_containers = soup.find_all('div', class_=re.compile('.*_4ddWXP.*'))
            
            for container in product_containers[:max_results]:
                try:
                    product = self._extract_flipkart_product(container)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Failed to extract Flipkart product: {e}")
                    continue
            
            logger.info(f"Extracted {len(products)} products from Flipkart")
            
        except Exception as e:
            logger.error(f"Flipkart search failed: {e}")
        
        return products
    
    def _extract_flipkart_product(self, container) -> Optional[ProductData]:
        """Extract product data from Flipkart product container"""
        try:
            # Product title
            title_elem = container.find('a', class_=re.compile('.*IRpwTa.*'))
            if not title_elem:
                title_elem = container.find('div', class_=re.compile('.*_4rR01T.*'))
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
            
            # Product URL
            product_url = None
            if title_elem and title_elem.get('href'):
                product_url = urljoin(self.platforms['flipkart']['base_url'], title_elem['href'])
            
            # Price information
            price = None
            mrp = None
            price_elem = container.find('div', class_=re.compile('.*_30jeq3.*'))
            if price_elem:
                price_text = price_elem.get_text(strip=True).replace('₹', '').replace(',', '')
                try:
                    price = float(price_text)
                except ValueError:
                    pass
            
            # Image URL
            img_elem = container.find('img')
            image_urls = []
            if img_elem and img_elem.get('src'):
                image_urls.append(img_elem['src'])
            
            return ProductData(
                title=title,
                price=price,
                mrp=mrp,
                product_url=product_url,
                image_urls=image_urls,
                platform='flipkart',
                extracted_at=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
        except Exception as e:
            logger.error(f"Failed to extract Flipkart product data: {e}")
            return None
    
    def _search_myntra(self, query: str, max_results: int) -> List[ProductData]:
        """Search Myntra for fashion products"""
        products = []
        
        try:
            search_url = f"https://www.myntra.com/{query.replace(' ', '-')}"
            html = self._make_request(search_url, 'myntra', use_selenium=True)
            
            if not html:
                return products
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find product containers
            product_containers = soup.find_all('li', class_=re.compile('.*product-base.*'))
            
            for container in product_containers[:max_results]:
                try:
                    product = self._extract_myntra_product(container)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Failed to extract Myntra product: {e}")
                    continue
            
            logger.info(f"Extracted {len(products)} products from Myntra")
            
        except Exception as e:
            logger.error(f"Myntra search failed: {e}")
        
        return products
    
    def _extract_myntra_product(self, container) -> Optional[ProductData]:
        """Extract product data from Myntra product container"""
        try:
            # Product title
            title_elem = container.find('h3', class_='product-product')
            if not title_elem:
                title_elem = container.find('h4', class_='product-product')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
            
            # Brand
            brand_elem = container.find('h3', class_='product-brand')
            brand = brand_elem.get_text(strip=True) if brand_elem else None
            
            # Price information
            price = None
            mrp = None
            price_elem = container.find('span', class_='product-discountedPrice')
            if price_elem:
                price_text = price_elem.get_text(strip=True).replace('Rs. ', '').replace(',', '')
                try:
                    price = float(price_text)
                except ValueError:
                    pass
            
            # MRP
            mrp_elem = container.find('span', class_='product-strike')
            if mrp_elem:
                mrp_text = mrp_elem.get_text(strip=True).replace('Rs. ', '').replace(',', '')
                try:
                    mrp = float(mrp_text)
                except ValueError:
                    pass
            
            # Product URL
            link_elem = container.find('a')
            product_url = None
            if link_elem and link_elem.get('href'):
                product_url = urljoin(self.platforms['myntra']['base_url'], link_elem['href'])
            
            # Image URL
            img_elem = container.find('img', class_='img-responsive')
            image_urls = []
            if img_elem and img_elem.get('src'):
                image_urls.append(img_elem['src'])
            
            return ProductData(
                title=title,
                brand=brand,
                price=price,
                mrp=mrp,
                product_url=product_url,
                image_urls=image_urls,
                platform='myntra',
                category='fashion',
                extracted_at=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
        except Exception as e:
            logger.error(f"Failed to extract Myntra product data: {e}")
            return None
    
    def _search_nykaa(self, query: str, max_results: int) -> List[ProductData]:
        """Search Nykaa for beauty products"""
        products = []
        
        try:
            search_url = self.platforms['nykaa']['search_url'].format(query=query.replace(' ', '+'))
            html = self._make_request(search_url, 'nykaa', use_selenium=True)
            
            if not html:
                return products
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find product containers
            product_containers = soup.find_all('div', class_=re.compile('.*ProductTile.*'))
            
            for container in product_containers[:max_results]:
                try:
                    product = self._extract_nykaa_product(container)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Failed to extract Nykaa product: {e}")
                    continue
            
            logger.info(f"Extracted {len(products)} products from Nykaa")
            
        except Exception as e:
            logger.error(f"Nykaa search failed: {e}")
        
        return products
    
    def _extract_nykaa_product(self, container) -> Optional[ProductData]:
        """Extract product data from Nykaa product container"""
        try:
            # Product title
            title_elem = container.find('div', class_=re.compile('.*ProductTile-name.*'))
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
            
            # Brand
            brand_elem = container.find('div', class_=re.compile('.*ProductTile-brand.*'))
            brand = brand_elem.get_text(strip=True) if brand_elem else None
            
            # Price information
            price = None
            mrp = None
            price_elem = container.find('span', class_=re.compile('.*ProductTile-price.*'))
            if price_elem:
                price_text = price_elem.get_text(strip=True).replace('₹', '').replace(',', '')
                try:
                    price = float(price_text)
                except ValueError:
                    pass
            
            # Product URL
            link_elem = container.find('a')
            product_url = None
            if link_elem and link_elem.get('href'):
                product_url = urljoin(self.platforms['nykaa']['base_url'], link_elem['href'])
            
            # Image URL
            img_elem = container.find('img')
            image_urls = []
            if img_elem and img_elem.get('src'):
                image_urls.append(img_elem['src'])
            
            return ProductData(
                title=title,
                brand=brand,
                price=price,
                mrp=mrp,
                product_url=product_url,
                image_urls=image_urls,
                platform='nykaa',
                category='beauty',
                extracted_at=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
        except Exception as e:
            logger.error(f"Failed to extract Nykaa product data: {e}")
            return None
    
    def get_product_details(self, product_url: str, platform: str) -> Optional[ProductData]:
        """Get detailed product information from product page"""
        
        if platform not in self.platforms:
            raise ValueError(f"Unsupported platform: {platform}")
        
        logger.info(f"Getting product details from {product_url}")
        
        try:
            html = self._make_request(product_url, platform, use_selenium=True)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Platform-specific detail extraction
            if platform == 'amazon':
                return self._extract_amazon_details(soup, product_url)
            elif platform == 'flipkart':
                return self._extract_flipkart_details(soup, product_url)
            elif platform == 'myntra':
                return self._extract_myntra_details(soup, product_url)
            elif platform == 'nykaa':
                return self._extract_nykaa_details(soup, product_url)
            
        except Exception as e:
            logger.error(f"Failed to get product details from {product_url}: {e}")
        
        return None
    
    def _extract_amazon_details(self, soup: BeautifulSoup, url: str) -> Optional[ProductData]:
        """Extract detailed product information from Amazon product page"""
        try:
            # Product title
            title_elem = soup.find('span', {'id': 'productTitle'})
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
            
            # Brand
            brand = None
            brand_elem = soup.find('a', {'id': 'bylineInfo'})
            if brand_elem:
                brand = brand_elem.get_text(strip=True).replace('Visit the ', '').replace(' Store', '')
            
            # Price and MRP
            price = None
            mrp = None
            
            price_elem = soup.find('span', class_='a-price-whole')
            if price_elem:
                price_text = price_elem.get_text(strip=True).replace(',', '')
                try:
                    price = float(price_text)
                except ValueError:
                    pass
            
            # Product details table
            details = {}
            detail_table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})
            if detail_table:
                rows = detail_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        details[key] = value
            
            # Extract Legal Metrology fields from details
            net_quantity = details.get('net quantity') or details.get('item weight') or details.get('package weight')
            manufacturer = details.get('manufacturer') or details.get('brand')
            country_of_origin = details.get('country of origin') or details.get('origin')
            
            # Image URLs
            image_urls = []
            img_elements = soup.find_all('img', {'data-a-image-name': 'landingImage'})
            for img in img_elements:
                if img.get('data-a-image-source'):
                    image_urls.append(img['data-a-image-source'])
            
            # Description
            description_elem = soup.find('div', {'id': 'feature-bullets'})
            description = description_elem.get_text(strip=True) if description_elem else None
            
            return ProductData(
                title=title,
                brand=brand,
                price=price,
                mrp=mrp,
                description=description,
                net_quantity=net_quantity,
                manufacturer=manufacturer,
                country_of_origin=country_of_origin,
                platform='amazon',
                product_url=url,
                image_urls=image_urls,
                extracted_at=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
        except Exception as e:
            logger.error(f"Failed to extract Amazon product details: {e}")
            return None
    
    def bulk_crawl(self, queries: List[str], platforms: List[str] = None, max_results_per_query: int = 20) -> List[ProductData]:
        """Perform bulk crawling across multiple queries and platforms"""
        
        if platforms is None:
            platforms = ['amazon', 'flipkart']
        
        all_products = []
        
        for query in queries:
            logger.info(f"Bulk crawling for query: '{query}'")
            
            for platform in platforms:
                try:
                    products = self.search_products(query, platform, max_results_per_query)
                    all_products.extend(products)
                    logger.info(f"Found {len(products)} products for '{query}' on {platform}")
                    
                    # Respect rate limits between platforms
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to crawl {platform} for '{query}': {e}")
                    continue
        
        logger.info(f"Bulk crawling completed: {len(all_products)} total products")
        return all_products
    
    def save_products(self, products: List[ProductData], filepath: str = None) -> str:
        """Save crawled products to JSON file"""
        
        if filepath is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filepath = f"app/data/crawled_products_{timestamp}.json"
        
        # Convert to serializable format
        products_data = [asdict(product) for product in products]
        
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Save to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(products_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(products)} products to {filepath}")
        return filepath
    
    def load_products(self, filepath: str) -> List[ProductData]:
        """Load products from JSON file"""
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
            
            products = []
            for data in products_data:
                products.append(ProductData(**data))
            
            logger.info(f"Loaded {len(products)} products from {filepath}")
            return products
            
        except Exception as e:
            logger.error(f"Failed to load products from {filepath}: {e}")
            return []
    
    def export_to_csv(self, products: List[ProductData], filepath: str = None) -> str:
        """Export products to CSV format"""
        
        if filepath is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filepath = f"app/data/crawled_products_{timestamp}.csv"
        
        # Convert to DataFrame
        products_data = [asdict(product) for product in products]
        df = pd.DataFrame(products_data)
        
        # Handle list columns
        if 'image_urls' in df.columns:
            df['image_urls'] = df['image_urls'].apply(lambda x: '; '.join(x) if isinstance(x, list) else x)
        if 'issues_found' in df.columns:
            df['issues_found'] = df['issues_found'].apply(lambda x: '; '.join(x) if isinstance(x, list) else x)
        
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Save to CSV
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"Exported {len(products)} products to {filepath}")
        return filepath
    
    def get_supported_platforms(self) -> Dict[str, str]:
        """Get list of supported e-commerce platforms"""
        return {platform: config['name'] for platform, config in self.platforms.items()}
    
    def get_crawling_statistics(self, products: List[ProductData]) -> Dict[str, Any]:
        """Generate statistics for crawled products"""
        
        if not products:
            return {}
        
        stats = {
            'total_products': len(products),
            'platforms': {},
            'categories': {},
            'price_range': {},
            'data_completeness': {}
        }
        
        # Platform distribution
        for product in products:
            platform = product.platform or 'unknown'
            stats['platforms'][platform] = stats['platforms'].get(platform, 0) + 1
        
        # Category distribution
        for product in products:
            category = product.category or 'uncategorized'
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
        
        # Price statistics
        prices = [p.price for p in products if p.price is not None]
        if prices:
            stats['price_range'] = {
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices),
                'median': sorted(prices)[len(prices)//2]
            }
        
        # Data completeness
        fields = ['title', 'brand', 'price', 'net_quantity', 'manufacturer', 'country_of_origin']
        for field in fields:
            complete_count = sum(1 for p in products if getattr(p, field) is not None)
            stats['data_completeness'][field] = {
                'complete': complete_count,
                'percentage': (complete_count / len(products)) * 100
            }
        
        return stats


def demo_crawler():
    """Demonstration of the web crawler functionality"""
    
    # Initialize crawler
    crawler = EcommerceCrawler()
    
    # Sample queries for different product categories
    queries = [
        "organic food products",
        "packaged snacks",
        "beauty products",
        "electronics accessories"
    ]
    
    # Crawl products from Amazon and Flipkart
    products = crawler.bulk_crawl(queries, platforms=['amazon', 'flipkart'], max_results_per_query=5)
    
    # Save results
    json_file = crawler.save_products(products)
    csv_file = crawler.export_to_csv(products)
    
    # Generate statistics
    stats = crawler.get_crawling_statistics(products)
    
    print(f"Crawling completed!")
    print(f"Total products: {stats.get('total_products', 0)}")
    print(f"Platforms: {list(stats.get('platforms', {}).keys())}")
    print(f"Saved to: {json_file}")
    print(f"CSV export: {csv_file}")
    
    return products, stats

if __name__ == "__main__":
    # Run demonstration
    demo_crawler()
