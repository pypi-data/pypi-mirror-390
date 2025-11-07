"""
Modern Email Configuration System
Supports OAuth2, SendGrid, Mailgun, and traditional SMTP
"""

import os
import json
import smtplib
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class EmailProvider:
    """Base class for email providers"""
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Send email - must be implemented by subclasses"""
        raise NotImplementedError


class SMTPProvider(EmailProvider):
    """Traditional SMTP provider"""
    
    def __init__(self, server: str, port: int, user: str, password: str):
        self.server = server
        self.port = port
        self.user = user
        self.password = password
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"SMTP send failed: {e}")
            return False


class SendGridProvider(EmailProvider):
    """SendGrid API provider (no password needed, just API key)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Send email via SendGrid API"""
        try:
            import requests
            
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": os.getenv("SENDGRID_FROM_EMAIL", "noreply@example.com")},
                "subject": subject,
                "content": [
                    {
                        "type": "text/html" if html_body else "text/plain",
                        "value": html_body or body
                    }
                ]
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return response.status_code == 202
        except ImportError:
            logger.error("SendGrid requires 'requests' package. Install with: pip install requests")
            return False
        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")
            return False


class MailgunProvider(EmailProvider):
    """Mailgun API provider (no password needed, just API key)"""
    
    def __init__(self, api_key: str, domain: str):
        self.api_key = api_key
        self.domain = domain
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Send email via Mailgun API"""
        try:
            import requests
            
            url = f"https://api.mailgun.net/v3/{self.domain}/messages"
            auth = ("api", self.api_key)
            
            data = {
                "from": os.getenv("MAILGUN_FROM_EMAIL", f"noreply@{self.domain}"),
                "to": to_email,
                "subject": subject,
            }
            
            if html_body:
                data["html"] = html_body
            else:
                data["text"] = body
            
            response = requests.post(url, auth=auth, data=data, timeout=10)
            return response.status_code == 200
        except ImportError:
            logger.error("Mailgun requires 'requests' package. Install with: pip install requests")
            return False
        except Exception as e:
            logger.error(f"Mailgun send failed: {e}")
            return False


class EmailConfigManager:
    """Manages email configuration with multiple provider support"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path.home() / ".openai_cost_tracker"
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "email_config.json"
        self.provider: Optional[EmailProvider] = None
        self._load_config()
    
    def _load_config(self):
        """Load email configuration"""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            provider_type = config.get("provider", "smtp")
            
            if provider_type == "sendgrid":
                api_key = config.get("api_key") or os.getenv("SENDGRID_API_KEY")
                if api_key:
                    self.provider = SendGridProvider(api_key)
            elif provider_type == "mailgun":
                api_key = config.get("api_key") or os.getenv("MAILGUN_API_KEY")
                domain = config.get("domain") or os.getenv("MAILGUN_DOMAIN")
                if api_key and domain:
                    self.provider = MailgunProvider(api_key, domain)
            elif provider_type == "smtp":
                # Try to load from config or env
                server = config.get("server") or os.getenv("SMTP_SERVER", "smtp.gmail.com")
                port = int(config.get("port") or os.getenv("SMTP_PORT", "587"))
                user = config.get("user") or os.getenv("SMTP_USER") or os.getenv("EMAIL_IMAP_USER")
                password = config.get("password") or os.getenv("SMTP_PASSWORD") or os.getenv("EMAIL_IMAP_PASS", "").strip('"').strip("'")
                
                if user and password:
                    self.provider = SMTPProvider(server, port, user, password)
        except Exception as e:
            logger.error(f"Failed to load email config: {e}")
    
    def configure_sendgrid(self, api_key: str, from_email: Optional[str] = None) -> bool:
        """Configure SendGrid provider"""
        try:
            config = {
                "provider": "sendgrid",
                "api_key": api_key,
            }
            if from_email:
                config["from_email"] = from_email
                os.environ["SENDGRID_FROM_EMAIL"] = from_email
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.provider = SendGridProvider(api_key)
            
            # Test email
            test_result = self.send_test_email()
            if test_result:
                logger.info("✅ SendGrid configured successfully!")
                return True
            else:
                logger.warning("⚠️ SendGrid configured but test email failed")
                return False
        except Exception as e:
            logger.error(f"Failed to configure SendGrid: {e}")
            return False
    
    def configure_mailgun(self, api_key: str, domain: str, from_email: Optional[str] = None) -> bool:
        """Configure Mailgun provider"""
        try:
            config = {
                "provider": "mailgun",
                "api_key": api_key,
                "domain": domain,
            }
            if from_email:
                config["from_email"] = from_email
                os.environ["MAILGUN_FROM_EMAIL"] = from_email
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.provider = MailgunProvider(api_key, domain)
            
            # Test email
            test_result = self.send_test_email()
            if test_result:
                logger.info("✅ Mailgun configured successfully!")
                return True
            else:
                logger.warning("⚠️ Mailgun configured but test email failed")
                return False
        except Exception as e:
            logger.error(f"Failed to configure Mailgun: {e}")
            return False
    
    def configure_smtp(self, server: str, port: int, user: str, password: str) -> bool:
        """Configure SMTP provider"""
        try:
            config = {
                "provider": "smtp",
                "server": server,
                "port": port,
                "user": user,
                "password": password,  # Note: In production, consider encryption
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.provider = SMTPProvider(server, port, user, password)
            
            # Test email
            test_result = self.send_test_email()
            if test_result:
                logger.info("✅ SMTP configured successfully!")
                return True
            else:
                logger.warning("⚠️ SMTP configured but test email failed")
                return False
        except Exception as e:
            logger.error(f"Failed to configure SMTP: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Send email using configured provider"""
        if not self.provider:
            logger.error("No email provider configured. Run: openai-cost-config-email")
            return False
        
        return self.provider.send_email(to_email, subject, body, html_body)
    
    def send_test_email(self, to_email: Optional[str] = None) -> bool:
        """Send a test email"""
        if not to_email:
            # Try to get from config
            try:
                if self.config_file.exists():
                    with open(self.config_file, 'r') as f:
                        config = json.load(f)
                    to_email = config.get("test_email") or os.getenv("COST_REPORT_EMAIL")
            except:
                pass
        
        if not to_email:
            logger.error("No recipient email specified")
            return False
        
        subject = "AI Cost Tracker - Test Email"
        body = "This is a test email from AI Cost Tracker. If you received this, your email configuration is working correctly!"
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }}
                .container {{ background-color: #ffffff; padding: 20px; border-radius: 5px; border: 1px solid #ddd; }}
                h1 {{ color: #333; }}
                p {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✅ Email Configuration Test</h1>
                <p>This is a test email from AI Cost Tracker.</p>
                <p>If you received this, your email configuration is working correctly!</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html_body)
    
    def is_configured(self) -> bool:
        """Check if email is configured"""
        return self.provider is not None

