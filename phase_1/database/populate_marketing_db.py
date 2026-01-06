"""
Generate sample data for Marketing Database
Run this after creating the schema
Usage: python3 populate_marketing_db.py [host] [user] [password] [port]
"""

import psycopg2
from datetime import datetime, timedelta
import random
import sys

def get_db_config():
    """Get database configuration from command line or defaults"""
    if len(sys.argv) >= 5:
        return {
            'host': sys.argv[1],
            'database': 'marketing_db',
            'user': sys.argv[2],
            'password': sys.argv[3],
            'port': int(sys.argv[4])
        }
    else:
        # Default configuration - UPDATE THESE
        return {
            'host': 'text2sql-cluster.cluster-cmey4eonndgc.ap-south-1.rds.amazonaws.com',
            'database': 'marketing_db',
            'user': 'postgres',
            'password': 'YourSecurePassword123',
            'port': 5432
        }

def get_connection():
    config = get_db_config()
    return psycopg2.connect(**config)

def populate_campaigns(conn):
    """Populate campaigns table with 30 records"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE campaigns CASCADE;")
    
    campaign_types = ['email', 'social_media', 'ppc', 'content', 'influencer']
    channels = ['facebook', 'google_ads', 'instagram', 'email', 'linkedin', 'twitter', 'tiktok']
    statuses = ['active', 'active', 'active', 'paused', 'completed']
    
    campaigns_data = []
    
    for i in range(1, 31):
        start_date = datetime.now().date() - timedelta(days=random.randint(30, 365))
        
        # Some campaigns are completed, others ongoing
        if random.random() < 0.3:
            end_date = start_date + timedelta(days=random.randint(30, 90))
            status = 'completed'
        else:
            end_date = None
            status = random.choice(['active', 'active', 'paused'])
        
        campaign_type = random.choice(campaign_types)
        channel = random.choice(channels)
        budget = round(random.uniform(5000, 50000), 2)
        
        campaigns_data.append((
            f'{campaign_type.title()} Campaign {i}',
            campaign_type,
            start_date,
            end_date,
            budget,
            status,
            channel,
            f'Target audience for {campaign_type} campaign on {channel}'
        ))
    
    for campaign in campaigns_data:
        cursor.execute("""
            INSERT INTO campaigns (campaign_name, campaign_type, start_date, end_date, budget, status, channel, target_audience)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, campaign)
    
    conn.commit()
    print(f"  ✓ Inserted {len(campaigns_data)} campaigns")

def populate_leads(conn):
    """Populate leads table with 200 records"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE leads CASCADE;")
    
    first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'James', 'Jennifer', 'Robert', 'Linda',
                   'William', 'Patricia', 'Richard', 'Barbara', 'Christopher', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Karen']
    
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                  'Wilson', 'Anderson', 'Taylor', 'Thomas', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White']
    
    companies = ['Tech Corp', 'Digital Solutions', 'Cloud Systems', 'Data Analytics Inc', 'AI Innovations',
                 'Software Hub', 'Mobile Apps Co', 'Web Services', 'Enterprise Solutions', 'Smart Tech',
                 'Future Systems', 'Innovation Labs', 'Digital Agency', 'Tech Partners', 'Solutions Group']
    
    job_titles = ['Marketing Manager', 'CEO', 'CTO', 'VP Sales', 'Director', 'Product Manager', 
                  'Business Analyst', 'Operations Manager', 'IT Manager', 'CFO']
    
    lead_sources = ['website', 'social_media', 'referral', 'event', 'webinar']
    lead_statuses = ['new', 'contacted', 'qualified', 'converted', 'lost']
    
    # Get campaign IDs
    cursor.execute("SELECT campaign_id FROM campaigns")
    campaign_ids = [row[0] for row in cursor.fetchall()]
    
    for i in range(200):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@{random.choice(['email.com', 'company.com', 'business.com'])}"
        phone = f"555-{random.randint(1000, 9999)}"
        company = random.choice(companies)
        job_title = random.choice(job_titles)
        campaign_id = random.choice(campaign_ids) if random.random() < 0.8 else None
        lead_source = random.choice(lead_sources)
        lead_status = random.choice(lead_statuses)
        lead_score = random.randint(0, 100)
        
        cursor.execute("""
            INSERT INTO leads (campaign_id, first_name, last_name, email, phone, company, job_title, 
                             lead_source, lead_status, lead_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (campaign_id, first_name, last_name, email, phone, company, job_title, 
              lead_source, lead_status, lead_score))
    
    conn.commit()
    print(f"  ✓ Inserted 200 leads")

def populate_ad_spend(conn):
    """Populate ad_spend table with daily records for campaigns"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE ad_spend CASCADE;")
    
    platforms = ['google_ads', 'facebook_ads', 'instagram_ads', 'linkedin_ads']
    
    # Get active campaigns
    cursor.execute("""
        SELECT campaign_id, start_date, end_date, budget 
        FROM campaigns 
        WHERE campaign_type IN ('ppc', 'social_media')
    """)
    
    campaigns = cursor.fetchall()
    
    total_records = 0
    for campaign_id, start_date, end_date, budget in campaigns:
        # Generate daily records
        current_date = start_date
        end = end_date if end_date else datetime.now().date()
        
        # Limit to 90 days max
        if (end - start_date).days > 90:
            end = start_date + timedelta(days=90)
        
        daily_budget = float(budget) / max((end - start_date).days, 1)
        
        while current_date <= end:
            platform = random.choice(platforms)
            daily_spend = daily_budget * random.uniform(0.8, 1.2)
            impressions = int(daily_spend * random.uniform(800, 1500))
            clicks = int(impressions * random.uniform(0.01, 0.05))
            conversions = int(clicks * random.uniform(0.02, 0.1))
            
            cursor.execute("""
                INSERT INTO ad_spend (campaign_id, spend_date, platform, amount_spent, impressions, clicks, conversions)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (campaign_id, current_date, platform, round(daily_spend, 2), impressions, clicks, conversions))
            
            total_records += 1
            current_date += timedelta(days=1)
    
    conn.commit()
    print(f"  ✓ Inserted {total_records} ad spend records")

def populate_conversions(conn):
    """Populate conversions table based on qualified/converted leads"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE conversions CASCADE;")
    
    conversion_types = ['signup', 'purchase', 'demo_request', 'subscription']
    
    # Get qualified and converted leads
    cursor.execute("""
        SELECT lead_id, campaign_id, created_at 
        FROM leads 
        WHERE lead_status IN ('qualified', 'converted')
    """)
    
    leads = cursor.fetchall()
    
    for lead_id, campaign_id, created_at in leads:
        conversion_type = random.choice(conversion_types)
        
        # Conversion happens 1-30 days after lead creation
        conversion_date = created_at + timedelta(days=random.randint(1, 30))
        
        # Conversion value based on type
        if conversion_type == 'purchase':
            value = round(random.uniform(100, 5000), 2)
        elif conversion_type == 'subscription':
            value = round(random.uniform(50, 500), 2)
        elif conversion_type == 'demo_request':
            value = round(random.uniform(0, 100), 2)
        else:  # signup
            value = 0
        
        customer_id = random.randint(1, 50) if conversion_type in ['purchase', 'subscription'] else None
        
        cursor.execute("""
            INSERT INTO conversions (lead_id, campaign_id, conversion_date, conversion_type, conversion_value, customer_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (lead_id, campaign_id, conversion_date, conversion_type, value, customer_id))
    
    conn.commit()
    print(f"  ✓ Inserted {len(leads)} conversions")

def populate_email_metrics(conn):
    """Populate email_metrics table for email campaigns"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE email_metrics CASCADE;")
    
    # Get email campaigns
    cursor.execute("""
        SELECT campaign_id, start_date, end_date 
        FROM campaigns 
        WHERE campaign_type = 'email'
    """)
    
    campaigns = cursor.fetchall()
    
    total_records = 0
    for campaign_id, start_date, end_date in campaigns:
        # Generate weekly email metrics
        current_date = start_date
        end = end_date if end_date else datetime.now().date()
        
        # Limit to 12 weeks
        if (end - start_date).days > 84:
            end = start_date + timedelta(days=84)
        
        while current_date <= end:
            emails_sent = random.randint(5000, 50000)
            emails_delivered = int(emails_sent * random.uniform(0.95, 0.99))
            opens = int(emails_delivered * random.uniform(0.15, 0.35))
            clicks = int(opens * random.uniform(0.1, 0.3))
            unsubscribes = int(emails_sent * random.uniform(0.001, 0.005))
            bounces = emails_sent - emails_delivered
            spam_complaints = int(emails_sent * random.uniform(0.0001, 0.001))
            
            cursor.execute("""
                INSERT INTO email_metrics (campaign_id, send_date, emails_sent, emails_delivered, 
                                         opens, clicks, unsubscribes, bounces, spam_complaints)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (campaign_id, current_date, emails_sent, emails_delivered, opens, clicks, 
                  unsubscribes, bounces, spam_complaints))
            
            total_records += 1
            current_date += timedelta(days=7)  # Weekly sends
    
    conn.commit()
    print(f"  ✓ Inserted {total_records} email metrics records")

def main():
    print("\nPopulating Marketing Database...")
    
    try:
        conn = get_connection()
        print("  ✓ Connected to database")
        
        populate_campaigns(conn)
        populate_leads(conn)
        populate_ad_spend(conn)
        populate_conversions(conn)
        populate_email_metrics(conn)
        
        conn.close()
        print("  ✓ Marketing database population complete!\n")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
