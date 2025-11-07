#!/usr/bin/env python3
"""
Interactive Email Configuration CLI
Makes it easy to set up email without manual password configuration
"""

import sys
import os
from pathlib import Path

def main():
    """Interactive email configuration wizard"""
    from openai_cost_tracker.services.email_config import EmailConfigManager
    
    print("=" * 80)
    print("📧 AI Cost Tracker - Email Configuration Wizard")
    print("=" * 80)
    print()
    print("Choose your email provider:")
    print()
    print("1. SendGrid (Recommended - No password needed, just API key)")
    print("2. Mailgun (No password needed, just API key)")
    print("3. Gmail/Outlook SMTP (Requires app password)")
    print("4. Custom SMTP")
    print("5. Skip email configuration")
    print()
    
    choice = input("Enter your choice (1-5): ").strip()
    
    config_manager = EmailConfigManager()
    
    if choice == "1":
        configure_sendgrid(config_manager)
    elif choice == "2":
        configure_mailgun(config_manager)
    elif choice == "3":
        configure_gmail_smtp(config_manager)
    elif choice == "4":
        configure_custom_smtp(config_manager)
    elif choice == "5":
        print("\n⏭️  Skipping email configuration")
        print("You can configure email later by running: openai-cost-config-email")
        return
    else:
        print("\n❌ Invalid choice")
        sys.exit(1)
    
    # Ask for recipient email
    print()
    recipient = input("Enter recipient email for cost reports (or press Enter to skip): ").strip()
    if recipient:
        # Save to .env file
        env_file = config_manager.config_dir / ".env"
        with open(env_file, 'a') as f:
            f.write(f"\nCOST_REPORT_EMAIL={recipient}\n")
        print(f"✅ Recipient email saved: {recipient}")
    
    # Test email
    if recipient:
        print()
        test = input("Send test email? (y/n): ").strip().lower()
        if test == 'y':
            print("📧 Sending test email...")
            if config_manager.send_test_email(recipient):
                print("✅ Test email sent successfully!")
            else:
                print("❌ Failed to send test email. Check your configuration.")
    else:
        print("\n💡 Tip: Set COST_REPORT_EMAIL environment variable to receive cost reports")


def configure_sendgrid(config_manager):
    """Configure SendGrid"""
    print()
    print("=" * 80)
    print("SendGrid Configuration")
    print("=" * 80)
    print()
    print("📝 Steps to get your SendGrid API key:")
    print("1. Sign up at https://sendgrid.com (free tier: 100 emails/day)")
    print("2. Go to Settings > API Keys")
    print("3. Create a new API key with 'Mail Send' permissions")
    print("4. Copy the API key (you'll only see it once!)")
    print()
    
    api_key = input("Enter your SendGrid API key: ").strip()
    if not api_key:
        print("❌ API key is required")
        sys.exit(1)
    
    from_email = input("Enter sender email (e.g., noreply@yourdomain.com) [optional]: ").strip()
    
    print("\n⚙️  Configuring SendGrid...")
    if config_manager.configure_sendgrid(api_key, from_email or None):
        print("✅ SendGrid configured successfully!")
    else:
        print("❌ Configuration failed. Please check your API key.")


def configure_mailgun(config_manager):
    """Configure Mailgun"""
    print()
    print("=" * 80)
    print("Mailgun Configuration")
    print("=" * 80)
    print()
    print("📝 Steps to get your Mailgun credentials:")
    print("1. Sign up at https://mailgun.com (free tier: 5,000 emails/month)")
    print("2. Go to Sending > API Keys")
    print("3. Copy your API key")
    print("4. Note your domain (e.g., sandbox123.mailgun.org)")
    print()
    
    api_key = input("Enter your Mailgun API key: ").strip()
    if not api_key:
        print("❌ API key is required")
        sys.exit(1)
    
    domain = input("Enter your Mailgun domain: ").strip()
    if not domain:
        print("❌ Domain is required")
        sys.exit(1)
    
    from_email = input(f"Enter sender email (e.g., noreply@{domain}) [optional]: ").strip()
    
    print("\n⚙️  Configuring Mailgun...")
    if config_manager.configure_mailgun(api_key, domain, from_email or None):
        print("✅ Mailgun configured successfully!")
    else:
        print("❌ Configuration failed. Please check your credentials.")


def configure_gmail_smtp(config_manager):
    """Configure Gmail SMTP with helpful instructions"""
    print()
    print("=" * 80)
    print("Gmail/Outlook SMTP Configuration")
    print("=" * 80)
    print()
    print("📝 For Gmail:")
    print("1. Enable 2-factor authentication on your Google account")
    print("2. Go to https://myaccount.google.com/apppasswords")
    print("3. Generate an app password for 'Mail'")
    print("4. Use that app password (not your regular password)")
    print()
    print("📝 For Outlook:")
    print("1. Go to https://account.microsoft.com/security")
    print("2. Enable 2-factor authentication")
    print("3. Generate an app password")
    print()
    
    email = input("Enter your email address: ").strip()
    if not email:
        print("❌ Email is required")
        sys.exit(1)
    
    password = input("Enter your app password (not regular password): ").strip()
    if not password:
        print("❌ App password is required")
        sys.exit(1)
    
    # Detect provider
    if "gmail.com" in email.lower():
        server = "smtp.gmail.com"
        port = 587
    elif "outlook.com" in email.lower() or "hotmail.com" in email.lower():
        server = "smtp-mail.outlook.com"
        port = 587
    else:
        server = input("Enter SMTP server (e.g., smtp.gmail.com): ").strip()
        port = int(input("Enter SMTP port (usually 587): ").strip() or "587")
    
    print("\n⚙️  Configuring SMTP...")
    if config_manager.configure_smtp(server, port, email, password):
        print("✅ SMTP configured successfully!")
    else:
        print("❌ Configuration failed. Please check your credentials.")


def configure_custom_smtp(config_manager):
    """Configure custom SMTP"""
    print()
    print("=" * 80)
    print("Custom SMTP Configuration")
    print("=" * 80)
    print()
    
    server = input("Enter SMTP server: ").strip()
    if not server:
        print("❌ SMTP server is required")
        sys.exit(1)
    
    port = input("Enter SMTP port (usually 587 for TLS): ").strip()
    if not port:
        port = "587"
    
    try:
        port = int(port)
    except ValueError:
        print("❌ Invalid port number")
        sys.exit(1)
    
    user = input("Enter SMTP username/email: ").strip()
    if not user:
        print("❌ Username is required")
        sys.exit(1)
    
    password = input("Enter SMTP password: ").strip()
    if not password:
        print("❌ Password is required")
        sys.exit(1)
    
    print("\n⚙️  Configuring SMTP...")
    if config_manager.configure_smtp(server, port, user, password):
        print("✅ SMTP configured successfully!")
    else:
        print("❌ Configuration failed. Please check your credentials.")


if __name__ == "__main__":
    main()

