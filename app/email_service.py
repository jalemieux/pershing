from flask_mail import Message
from flask import render_template_string
from app import mail

class EmailService:
    @staticmethod
    def send_verification_code(email, code):
        # HTML template for the verification email
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .code { font-size: 32px; font-weight: bold; text-align: center; 
                        padding: 20px; background: #f5f5f5; margin: 20px 0; }
                .warning { color: #666; font-size: 14px; }
                .expiry { color: #ff4444; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Your Verification Code</h2>
                <p>Please use the following code to verify your email address:</p>
                <div class="code">{{ code }}</div>
                <p class="expiry">This code will expire in 10 minutes.</p>
                <p class="warning">
                    If you didn't request this code, please ignore this email.
                    Never share this code with anyone.
                </p>
                <p>
                    Security Notice: We will never ask for this code outside of our website.
                    Always verify you're on our official website before entering the code.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            'Your Verification Code',
            sender='noreply@yourdomain.com',
            recipients=[email]
        )
        
        msg.html = render_template_string(
            html_template,
            code=code
        )
        
        try:
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False