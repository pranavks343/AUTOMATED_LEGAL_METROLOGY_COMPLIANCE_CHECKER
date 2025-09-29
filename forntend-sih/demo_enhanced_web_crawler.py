#!/usr/bin/env python3
"""
Enhanced Web Crawler with Compliance Checking - Demo Script
Demonstrates automated product crawling with Legal Metrology compliance validation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.web_crawler import EcommerceCrawler, ProductData
import json
import pandas as pd
from datetime import datetime
import time

def demo_enhanced_crawler():
    """Demonstrate the enhanced web crawler with compliance checking"""
    
    print("🌐 Enhanced Web Crawler with Compliance Checking Demo")
    print("=" * 60)
    
    # Initialize crawler
    print("🔧 Initializing Enhanced Web Crawler...")
    crawler = EcommerceCrawler()
    
    # Check if compliance is available
    if crawler.compliance_rules:
        print("✅ Compliance checking enabled - Legal Metrology Rules loaded")
    else:
        print("⚠️ Compliance checking disabled - Rules not available")
    
    print()
    
    # Sample queries for compliance testing
    queries = [
        "organic food products",
        "packaged snacks",
        "beauty products"
    ]
    
    platforms = ['amazon', 'flipkart']  # Start with these platforms
    
    print(f"🎯 Starting crawl for {len(queries)} queries across {len(platforms)} platforms")
    print("📋 Queries:", ", ".join(queries))
    print("🏪 Platforms:", ", ".join(platforms))
    print()
    
    all_products = []
    
    # Perform crawling with progress tracking
    total_operations = len(queries) * len(platforms)
    current_operation = 0
    
    for query in queries:
        for platform in platforms:
            current_operation += 1
            progress = (current_operation / total_operations) * 100
            
            print(f"[{progress:5.1f}%] Crawling '{query}' on {platform}...")
            
            try:
                # Crawl products (limit to 5 for demo)
                products = crawler.search_products(query, platform, max_results=5)
                all_products.extend(products)
                
                print(f"    ✅ Found {len(products)} products")
                
                # Show compliance results for each product
                for product in products:
                    status = product.compliance_status or "UNKNOWN"
                    score = product.compliance_score or 0
                    issues_count = len(product.issues_found) if product.issues_found else 0
                    
                    print(f"    📦 {product.title[:40]}... | Status: {status} | Score: {score:.1f} | Issues: {issues_count}")
                
                # Respect rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                continue
    
    print()
    print("📊 Crawling Results Summary")
    print("=" * 40)
    
    if all_products:
        # Generate compliance summary
        compliance_summary = crawler.get_compliance_summary(all_products)
        
        print(f"Total Products Crawled: {len(all_products)}")
        print(f"Compliant Products: {compliance_summary.get('compliant_products', 0)}")
        print(f"Partial Compliance: {compliance_summary.get('partial_products', 0)}")
        print(f"Non-Compliant: {compliance_summary.get('non_compliant_products', 0)}")
        print(f"Compliance Rate: {compliance_summary.get('compliance_rate', 0):.1f}%")
        print(f"Average Score: {compliance_summary.get('average_score', 0):.1f}/100")
        
        # Platform breakdown
        print("\n🏪 Platform Breakdown:")
        platform_compliance = compliance_summary.get('platform_compliance', {})
        for platform, stats in platform_compliance.items():
            rate = (stats['compliant'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {platform.title()}: {stats['total']} products, {rate:.1f}% compliant")
        
        # Most common issues
        print("\n⚠️ Most Common Compliance Issues:")
        issue_counts = compliance_summary.get('issue_counts', {})
        if issue_counts:
            sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
            for issue, count in sorted_issues[:5]:  # Top 5 issues
                print(f"  • {issue}: {count} occurrences")
        else:
            print("  ✅ No major compliance issues found!")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = f"demo_crawl_results_{timestamp}.json"
        csv_file = f"demo_crawl_results_{timestamp}.csv"
        
        # Save JSON
        crawler.save_products(all_products, json_file)
        print(f"\n💾 Results saved to: {json_file}")
        
        # Save CSV
        crawler.export_to_csv(all_products, csv_file)
        print(f"💾 CSV exported to: {csv_file}")
        
        # Show sample products with compliance details
        print("\n🔍 Sample Product Analysis:")
        print("-" * 50)
        
        for i, product in enumerate(all_products[:3]):  # Show first 3 products
            print(f"\n{i+1}. {product.title}")
            print(f"   Platform: {product.platform}")
            print(f"   Price: ₹{product.price}" if product.price else "   Price: N/A")
            print(f"   Compliance Status: {product.compliance_status}")
            print(f"   Compliance Score: {product.compliance_score:.1f}/100")
            
            if product.issues_found:
                print("   Issues Found:")
                for issue in product.issues_found[:3]:  # Show first 3 issues
                    print(f"     • {issue}")
                if len(product.issues_found) > 3:
                    print(f"     ... and {len(product.issues_found) - 3} more issues")
            else:
                print("   ✅ No compliance issues")
    
    else:
        print("❌ No products were successfully crawled")
    
    print("\n🎉 Demo completed!")
    print("\nTo use the enhanced web crawler in the Streamlit app:")
    print("1. Navigate to the '🌐 Enhanced Web Crawler' page")
    print("2. Select platforms and enter search queries")
    print("3. Enable compliance checking")
    print("4. Start crawling to get products with automatic compliance validation")

def demo_compliance_analysis():
    """Demonstrate compliance analysis features"""
    
    print("\n🔍 Compliance Analysis Demo")
    print("=" * 40)
    
    # Load sample crawled data if available
    try:
        crawler = EcommerceCrawler()
        
        # Look for existing crawl results
        crawl_files = []
        if os.path.exists("app/data/crawled"):
            for file in os.listdir("app/data/crawled"):
                if file.startswith("products_") and file.endswith(".json"):
                    crawl_files.append(os.path.join("app/data/crawled", file))
        
        if crawl_files:
            # Use the most recent file
            latest_file = max(crawl_files, key=os.path.getmtime)
            print(f"📂 Loading data from: {latest_file}")
            
            products = crawler.load_products(latest_file)
            print(f"📊 Loaded {len(products)} products")
            
            # Generate compliance summary
            summary = crawler.get_compliance_summary(products)
            
            print(f"\n📈 Compliance Analysis Results:")
            print(f"Total Products: {summary.get('total_products', 0)}")
            print(f"Compliance Rate: {summary.get('compliance_rate', 0):.1f}%")
            print(f"Average Score: {summary.get('average_score', 0):.1f}/100")
            
            # Show compliance breakdown
            print(f"\nCompliance Status Breakdown:")
            print(f"  ✅ Compliant: {summary.get('compliant_products', 0)}")
            print(f"  ⚠️ Partial: {summary.get('partial_products', 0)}")
            print(f"  ❌ Non-Compliant: {summary.get('non_compliant_products', 0)}")
            
        else:
            print("📭 No existing crawl data found. Run the main demo first.")
    
    except Exception as e:
        print(f"❌ Error in compliance analysis: {e}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Web Crawler Demo")
    print()
    
    try:
        # Run main demo
        demo_enhanced_crawler()
        
        # Run compliance analysis demo
        demo_compliance_analysis()
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n👋 Demo finished!")
