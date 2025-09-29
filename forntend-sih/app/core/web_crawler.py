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

# Import compliance checking modules
try:
    from .schemas import ExtractedFields, ValidationResult, ValidationIssue
    from .rules_engine import load_rules, validate
    from .nlp_extract import extract_fields
    COMPLIANCE_AVAILABLE = True
except ImportError:
    COMPLIANCE_AVAILABLE = False
    logger.warning("Compliance modules not available, compliance checking disabled")

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
    compliance_status: Optional[str] = None  # COMPLIANT, NON_COMPLIANT, PARTIAL
    issues_found: List[str] = None
    validation_result: Optional[ValidationResult] = None
    compliance_details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.image_urls is None:
            self.image_urls = []
        if self.issues_found is None:
            self.issues_found = []

class EcommerceCrawler:
    """Comprehensive web crawler for major Indian e-commerce platforms"""
    
    def __init__(self):
        """Initialize the e-commerce crawler with platform configurations"""
        
        # Load compliance rules if available
        self.compliance_rules = None
        if COMPLIANCE_AVAILABLE:
            try:
                self.compliance_rules = load_rules("app/data/rules/legal_metrology_rules.yaml")
                logger.info("Compliance rules loaded successfully")
            except FileNotFoundError:
                logger.warning("Compliance rules file not found, compliance checking disabled")
            except Exception as e:
                logger.error(f"Error loading compliance rules: {e}")
        
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
        logger.info(f"Compliance checking: {'Enabled' if self.compliance_rules else 'Disabled'}")
    
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
            # Product title - try multiple selectors for better compatibility
            title = None
            title_selectors = [
                'h2[class*="a-size-mini"]',
                'h2[class*="a-size-medium"]', 
                'span[class*="a-size-medium"]',
                'span[class*="a-size-base"]',
                'h2 a span',
                'h2 span',
                'a[data-cy="title-recipe"]',
                '.s-title-instructions-style h2',
                '[data-cy="title-recipe"] span'
            ]
            
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 3:  # Ensure we have a meaningful title
                        break
            
            # Fallback: look for any h2 or span with substantial text
            if not title:
                for elem in container.find_all(['h2', 'span', 'a']):
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10 and len(text) < 200:  # Reasonable title length
                        title = text
                        break
            
            # Final fallback
            if not title:
                title = "Product Title Not Found"
            
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
            
            product = ProductData(
                title=title,
                price=price,
                mrp=mrp,
                product_url=product_url,
                image_urls=image_urls,
                platform='amazon',
                rating=rating,
                extracted_at=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Perform compliance check
            self._perform_compliance_check(product)
            
            return product
            
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
            # Product title - try multiple selectors for Flipkart
            title = None
            title_selectors = [
                'a[class*="IRpwTa"]',
                'div[class*="_4rR01T"]',
                'div[class*="_2WkVRV"]',
                'a[class*="s1Q9rs"]',
                'div[class*="_2mylT6"]',
                'a[class*="_2mylT6"]',
                'div[class*="s1Q9rs"]',
                'a span',
                'div[class*="_3pLy-c"] div'
            ]
            
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 3:  # Ensure we have a meaningful title
                        break
            
            # Fallback: look for any element with substantial text
            if not title:
                for elem in container.find_all(['a', 'div', 'span']):
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10 and len(text) < 200:  # Reasonable title length
                        # Skip price-related text
                        if not re.search(r'₹|Rs\.|INR|\d+,\d+', text):
                            title = text
                            break
            
            # Final fallback
            if not title:
                title = "Flipkart Product Title Not Found"
            
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
            
            product = ProductData(
                title=title,
                price=price,
                mrp=mrp,
                product_url=product_url,
                image_urls=image_urls,
                platform='flipkart',
                extracted_at=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Perform compliance check
            self._perform_compliance_check(product)
            
            return product
            
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
            # Product title - try multiple selectors for Myntra
            title = None
            title_selectors = [
                'h3[class*="product-product"]',
                'h4[class*="product-product"]',
                'div[class*="product-product"]',
                'a[class*="product-product"]',
                'span[class*="product-product"]',
                '.product-product',
                'h3',
                'h4'
            ]
            
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 3:  # Ensure we have a meaningful title
                        break
            
            # Fallback: look for any element with substantial text
            if not title:
                for elem in container.find_all(['h3', 'h4', 'div', 'a', 'span']):
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10 and len(text) < 200:  # Reasonable title length
                        # Skip price-related text
                        if not re.search(r'₹|Rs\.|INR|\d+,\d+', text):
                            title = text
                            break
            
            # Final fallback
            if not title:
                title = "Myntra Product Title Not Found"
            
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
            
            product = ProductData(
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
            
            # Perform compliance check
            self._perform_compliance_check(product)
            
            return product
            
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
            # Product title - try multiple selectors for Nykaa
            title = None
            title_selectors = [
                'div[class*="ProductTile-name"]',
                'div[class*="product-name"]',
                'div[class*="name"]',
                'h3',
                'h4',
                'div[class*="title"]',
                'a[class*="name"]',
                'span[class*="name"]'
            ]
            
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 3:  # Ensure we have a meaningful title
                        break
            
            # Fallback: look for any element with substantial text
            if not title:
                for elem in container.find_all(['div', 'h3', 'h4', 'a', 'span']):
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10 and len(text) < 200:  # Reasonable title length
                        # Skip price-related text
                        if not re.search(r'₹|Rs\.|INR|\d+,\d+', text):
                            title = text
                            break
            
            # Final fallback
            if not title:
                title = "Nykaa Product Title Not Found"
            
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
            
            product = ProductData(
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
            
            # Perform compliance check
            self._perform_compliance_check(product)
            
            return product
            
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
        products_data = []
        for product in products:
            product_dict = asdict(product)
            
            # Handle ValidationResult serialization
            if product_dict.get('validation_result'):
                validation_result = product_dict['validation_result']
                if hasattr(validation_result, '__dict__'):
                    # Convert ValidationResult to dict
                    product_dict['validation_result'] = {
                        'is_compliant': validation_result.is_compliant,
                        'score': validation_result.score,
                        'issues': [
                            {
                                'field': issue.field,
                                'level': issue.level,
                                'message': issue.message
                            } for issue in validation_result.issues
                        ] if validation_result.issues else []
                    }
            
            # Ensure all fields are JSON serializable
            for key, value in product_dict.items():
                if value is None or isinstance(value, (str, int, float, bool, list, dict)):
                    continue
                elif hasattr(value, '__dict__'):
                    # Convert custom objects to dict
                    product_dict[key] = value.__dict__ if hasattr(value, '__dict__') else str(value)
                else:
                    # Convert other non-serializable objects to string
                    product_dict[key] = str(value)
            
            products_data.append(product_dict)
        
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
                # Handle ValidationResult deserialization
                if 'validation_result' in data and data['validation_result']:
                    # Skip validation_result for now as it's complex to reconstruct
                    # The compliance_details should contain the necessary information
                    data.pop('validation_result', None)
                
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
        
        # Convert to DataFrame with proper serialization
        products_data = []
        for product in products:
            product_dict = asdict(product)
            
            # Remove ValidationResult as it's not CSV-friendly
            product_dict.pop('validation_result', None)
            
            # Convert complex objects to strings
            for key, value in product_dict.items():
                if value is None:
                    continue
                elif isinstance(value, (str, int, float, bool)):
                    continue
                elif isinstance(value, list):
                    product_dict[key] = '; '.join(str(v) for v in value) if value else ''
                elif hasattr(value, '__dict__'):
                    product_dict[key] = str(value)
                else:
                    product_dict[key] = str(value)
            
            products_data.append(product_dict)
        
        df = pd.DataFrame(products_data)
        
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
    
    def _perform_compliance_check(self, product: ProductData) -> None:
        """Perform compliance check on crawled product data"""
        if not self.compliance_rules or not COMPLIANCE_AVAILABLE:
            return
        
        try:
            # Create text for NLP extraction from product data
            product_text = self._create_product_text(product)
            
            # Extract fields using NLP
            extracted_fields = extract_fields(product_text)
            
            # Perform validation
            validation_result = validate(extracted_fields, self.compliance_rules)
            
            # Update product with compliance information
            product.validation_result = validation_result
            product.compliance_score = validation_result.score
            product.compliance_status = self._determine_compliance_status(validation_result)
            product.issues_found = [issue.message for issue in validation_result.issues]
            
            # Create compliance details
            product.compliance_details = {
                'extracted_fields': {
                    'mrp_value': extracted_fields.mrp_value,
                    'net_quantity_value': extracted_fields.net_quantity_value,
                    'unit': extracted_fields.unit,
                    'manufacturer_name': extracted_fields.manufacturer_name,
                    'manufacturer_address': extracted_fields.manufacturer_address,
                    'consumer_care': extracted_fields.consumer_care,
                    'country_of_origin': extracted_fields.country_of_origin,
                    'mfg_date': extracted_fields.mfg_date,
                    'expiry_date': extracted_fields.expiry_date
                },
                'validation_issues': [
                    {
                        'field': issue.field,
                        'level': issue.level,
                        'message': issue.message
                    } for issue in validation_result.issues
                ],
                'is_compliant': validation_result.is_compliant,
                'score': validation_result.score
            }
            
            logger.debug(f"Compliance check completed for {product.title}: Score {product.compliance_score}")
            
        except Exception as e:
            logger.error(f"Error performing compliance check for {product.title}: {e}")
            product.compliance_status = "ERROR"
            product.compliance_score = 0
            product.issues_found = [f"Compliance check failed: {str(e)}"]
    
    def _create_product_text(self, product: ProductData) -> str:
        """Create text representation of product for NLP extraction"""
        text_parts = []
        
        if product.title:
            text_parts.append(f"Product: {product.title}")
        
        if product.description:
            text_parts.append(f"Description: {product.description}")
        
        if product.brand:
            text_parts.append(f"Brand: {product.brand}")
        
        if product.manufacturer:
            text_parts.append(f"Manufacturer: {product.manufacturer}")
        
        if product.price:
            text_parts.append(f"Price: ₹{product.price}")
        
        if product.mrp:
            text_parts.append(f"MRP: ₹{product.mrp}")
        
        if product.net_quantity:
            text_parts.append(f"Net Quantity: {product.net_quantity}")
        
        if product.country_of_origin:
            text_parts.append(f"Country of Origin: {product.country_of_origin}")
        
        if product.mfg_date:
            text_parts.append(f"Manufacturing Date: {product.mfg_date}")
        
        if product.expiry_date:
            text_parts.append(f"Expiry Date: {product.expiry_date}")
        
        return " ".join(text_parts)
    
    def _determine_compliance_status(self, validation_result: ValidationResult) -> str:
        """Determine overall compliance status based on validation result"""
        if validation_result.is_compliant:
            return "COMPLIANT"
        elif validation_result.score >= 60:
            return "PARTIAL"
        else:
            return "NON_COMPLIANT"
    
    def get_compliance_summary(self, products: List[ProductData]) -> Dict[str, Any]:
        """Generate compliance summary for a list of products"""
        if not products:
            return {}
        
        total_products = len(products)
        compliant_count = sum(1 for p in products if p.compliance_status == "COMPLIANT")
        partial_count = sum(1 for p in products if p.compliance_status == "PARTIAL")
        non_compliant_count = sum(1 for p in products if p.compliance_status == "NON_COMPLIANT")
        
        # Calculate average compliance score
        scores = [p.compliance_score for p in products if p.compliance_score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Count issues by type
        issue_counts = {}
        for product in products:
            if product.issues_found:
                for issue in product.issues_found:
                    issue_type = issue.split(':')[0] if ':' in issue else issue
                    issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Platform-wise compliance
        platform_compliance = {}
        for product in products:
            platform = product.platform or 'unknown'
            if platform not in platform_compliance:
                platform_compliance[platform] = {'total': 0, 'compliant': 0, 'avg_score': 0}
            
            platform_compliance[platform]['total'] += 1
            if product.compliance_status == "COMPLIANT":
                platform_compliance[platform]['compliant'] += 1
        
        # Calculate platform averages
        for platform in platform_compliance:
            platform_products = [p for p in products if p.platform == platform]
            platform_scores = [p.compliance_score for p in platform_products if p.compliance_score is not None]
            platform_compliance[platform]['avg_score'] = sum(platform_scores) / len(platform_scores) if platform_scores else 0
        
        return {
            'total_products': total_products,
            'compliant_products': compliant_count,
            'partial_products': partial_count,
            'non_compliant_products': non_compliant_count,
            'compliance_rate': (compliant_count / total_products * 100) if total_products > 0 else 0,
            'average_score': avg_score,
            'issue_counts': issue_counts,
            'platform_compliance': platform_compliance
        }


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
