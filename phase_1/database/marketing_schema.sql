-- =====================================================
-- MARKETING DATABASE SCHEMA
-- =====================================================

-- Create marketing database (run this separately as postgres user)
-- CREATE DATABASE marketing_db;

-- Connect to marketing_db before running below
-- \c marketing_db;

-- Campaigns Table
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id SERIAL PRIMARY KEY,
    campaign_name VARCHAR(255) NOT NULL,
    campaign_type VARCHAR(100),
    start_date DATE NOT NULL,
    end_date DATE,
    budget DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    channel VARCHAR(100),
    target_audience TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE campaigns IS 'Marketing campaigns across different channels';
COMMENT ON COLUMN campaigns.campaign_type IS 'Type: email, social_media, ppc, content, influencer';
COMMENT ON COLUMN campaigns.channel IS 'Channel: facebook, google_ads, instagram, email, linkedin';
COMMENT ON COLUMN campaigns.status IS 'Campaign status: active, paused, completed, cancelled';

-- Leads Table
CREATE TABLE IF NOT EXISTS leads (
    lead_id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(campaign_id),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    company VARCHAR(255),
    job_title VARCHAR(100),
    lead_source VARCHAR(100),
    lead_status VARCHAR(50) DEFAULT 'new',
    lead_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE leads IS 'Potential customers generated from marketing campaigns';
COMMENT ON COLUMN leads.lead_source IS 'Source: website, social_media, referral, event, webinar';
COMMENT ON COLUMN leads.lead_status IS 'Status: new, contacted, qualified, converted, lost';
COMMENT ON COLUMN leads.lead_score IS 'Lead quality score from 0-100';

-- Ad Spend Table
CREATE TABLE IF NOT EXISTS ad_spend (
    spend_id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(campaign_id),
    spend_date DATE NOT NULL,
    platform VARCHAR(100) NOT NULL,
    amount_spent DECIMAL(10, 2) NOT NULL,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0
);

COMMENT ON TABLE ad_spend IS 'Daily advertising spend and performance metrics';
COMMENT ON COLUMN ad_spend.platform IS 'Platform: google_ads, facebook_ads, instagram_ads, linkedin_ads';
COMMENT ON COLUMN ad_spend.impressions IS 'Number of times ad was shown';
COMMENT ON COLUMN ad_spend.clicks IS 'Number of clicks on the ad';
COMMENT ON COLUMN ad_spend.conversions IS 'Number of conversions from the ad';

-- Conversions Table
CREATE TABLE IF NOT EXISTS conversions (
    conversion_id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(lead_id),
    campaign_id INTEGER REFERENCES campaigns(campaign_id),
    conversion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    conversion_type VARCHAR(100),
    conversion_value DECIMAL(10, 2),
    customer_id INTEGER
);

COMMENT ON TABLE conversions IS 'Lead conversions to customers with attributed value';
COMMENT ON COLUMN conversions.conversion_type IS 'Type: signup, purchase, demo_request, subscription';
COMMENT ON COLUMN conversions.conversion_value IS 'Monetary value of the conversion';
COMMENT ON COLUMN conversions.customer_id IS 'Reference to customer ID if converted to customer';

-- Email Metrics Table
CREATE TABLE IF NOT EXISTS email_metrics (
    metric_id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(campaign_id),
    send_date DATE NOT NULL,
    emails_sent INTEGER NOT NULL,
    emails_delivered INTEGER NOT NULL,
    opens INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    unsubscribes INTEGER DEFAULT 0,
    bounces INTEGER DEFAULT 0,
    spam_complaints INTEGER DEFAULT 0
);

COMMENT ON TABLE email_metrics IS 'Email campaign performance metrics';
COMMENT ON COLUMN email_metrics.opens IS 'Number of unique email opens';
COMMENT ON COLUMN email_metrics.clicks IS 'Number of unique link clicks in email';
COMMENT ON COLUMN email_metrics.bounces IS 'Number of emails that bounced';

-- Create indexes for performance
CREATE INDEX idx_leads_campaign ON leads(campaign_id);
CREATE INDEX idx_leads_status ON leads(lead_status);
CREATE INDEX idx_ad_spend_campaign ON ad_spend(campaign_id);
CREATE INDEX idx_ad_spend_date ON ad_spend(spend_date);
CREATE INDEX idx_conversions_lead ON conversions(lead_id);
CREATE INDEX idx_conversions_campaign ON conversions(campaign_id);
CREATE INDEX idx_email_metrics_campaign ON email_metrics(campaign_id);
