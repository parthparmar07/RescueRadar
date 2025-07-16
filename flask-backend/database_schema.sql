-- RescueRadar Database Schema
-- Run this in your Supabase SQL Editor

-- Create reports table
CREATE TABLE IF NOT EXISTS public.reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  description TEXT NOT NULL,
  location TEXT NOT NULL,
  coordinates JSONB,
  contact_name VARCHAR(255),
  contact_email VARCHAR(255),
  contact_phone VARCHAR(20),
  urgency_level VARCHAR(20) DEFAULT 'normal' CHECK (urgency_level IN ('low', 'normal', 'high', 'emergency')),
  animal_type VARCHAR(50),
  situation_type VARCHAR(50) CHECK (situation_type IN ('abuse', 'neglect', 'injury', 'abandonment', 'hoarding', 'fighting', 'other')),
  image_url TEXT,
  ai_analysis JSONB,
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'in_progress', 'resolved', 'closed')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create notifications table to track sent notifications
CREATE TABLE IF NOT EXISTS public.notifications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  report_id UUID REFERENCES public.reports(id) ON DELETE CASCADE,
  notification_type VARCHAR(20) NOT NULL CHECK (notification_type IN ('email', 'whatsapp', 'sms')),
  recipient VARCHAR(255) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
  message_id TEXT,
  error_message TEXT,
  sent_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_reports_status ON public.reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON public.reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_urgency ON public.reports(urgency_level);
CREATE INDEX IF NOT EXISTS idx_notifications_report_id ON public.notifications(report_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access to reports
CREATE POLICY "Public can view active reports" ON public.reports
  FOR SELECT USING (status = 'active');

CREATE POLICY "Public can insert reports" ON public.reports
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Public can view notifications" ON public.notifications
  FOR SELECT USING (true);

CREATE POLICY "Public can insert notifications" ON public.notifications
  FOR INSERT WITH CHECK (true);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_reports_updated_at 
  BEFORE UPDATE ON public.reports 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
