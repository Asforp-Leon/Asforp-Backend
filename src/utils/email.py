import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from urllib.parse import urljoin

class EmailService:
    def __init__(self):
        # Configuración de email (usando Gmail como ejemplo)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = os.getenv('EMAIL_USER', 'noreply@asforp.com')
        self.password = os.getenv('EMAIL_PASSWORD', '')
        
    def send_verification_email(self, user_email, user_name, verification_token, base_url="http://localhost:5174"):
        """
        Envía un email de verificación al usuario
        """
        try:
            # Crear el mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Verifica tu cuenta en ASFORP"
            msg['From'] = self.email
            msg['To'] = user_email
            
            # URL de verificación
            verification_url = f"{base_url}/verify-email?token={verification_token}"
            
            # Contenido HTML del email
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #1a1a1a; color: #ffffff; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .logo {{ color: #fbbf24; font-size: 32px; font-weight: bold; }}
                    .content {{ background-color: #374151; padding: 30px; border-radius: 10px; }}
                    .button {{ 
                        display: inline-block; 
                        background-color: #fbbf24; 
                        color: #1a1a1a; 
                        padding: 12px 30px; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        font-weight: bold; 
                        margin: 20px 0;
                    }}
                    .footer {{ text-align: center; margin-top: 30px; color: #9ca3af; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">ASFORP</div>
                        <p>Asesoría y Formación Profesional</p>
                    </div>
                    
                    <div class="content">
                        <h2>¡Bienvenido a ASFORP, {user_name}!</h2>
                        
                        <p>Gracias por registrarte en nuestra plataforma. Para completar tu registro y activar tu cuenta, necesitas verificar tu dirección de email.</p>
                        
                        <p>Haz clic en el siguiente botón para verificar tu cuenta:</p>
                        
                        <div style="text-align: center;">
                            <a href="{verification_url}" class="button">Verificar mi cuenta</a>
                        </div>
                        
                        <p>Si no puedes hacer clic en el botón, copia y pega el siguiente enlace en tu navegador:</p>
                        <p style="word-break: break-all; color: #fbbf24;">{verification_url}</p>
                        
                        <p><strong>Este enlace expirará en 24 horas.</strong></p>
                        
                        <p>Si no has creado una cuenta en ASFORP, puedes ignorar este email.</p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2024 ASFORP - Asesoría y Formación Profesional</p>
                        <p>Este es un email automático, por favor no respondas a este mensaje.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Contenido de texto plano como alternativa
            text_content = f"""
            ¡Bienvenido a ASFORP, {user_name}!
            
            Gracias por registrarte en nuestra plataforma. Para completar tu registro y activar tu cuenta, necesitas verificar tu dirección de email.
            
            Visita el siguiente enlace para verificar tu cuenta:
            {verification_url}
            
            Este enlace expirará en 24 horas.
            
            Si no has creado una cuenta en ASFORP, puedes ignorar este email.
            
            © 2024 ASFORP - Asesoría y Formación Profesional
            """
            
            # Crear las partes del mensaje
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            # Adjuntar las partes al mensaje
            msg.attach(part1)
            msg.attach(part2)
            
            # En desarrollo, solo simular el envío
            print(f"[EMAIL SIMULADO] Enviando email de verificación a: {user_email}")
            print(f"[EMAIL SIMULADO] URL de verificación: {verification_url}")
            print(f"[EMAIL SIMULADO] Token: {verification_token}")
            
            # TODO: En producción, descomentar el código siguiente para envío real
            """
            # Conectar al servidor SMTP y enviar
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            """
            
            return True
            
        except Exception as e:
            print(f"Error enviando email: {str(e)}")
            return False
    
    def send_premium_confirmation_email(self, user_email, user_name):
        """
        Envía un email de confirmación cuando el usuario se convierte en premium
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "¡Bienvenido a ASFORP Premium!"
            msg['From'] = self.email
            msg['To'] = user_email
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #1a1a1a; color: #ffffff; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .logo {{ color: #fbbf24; font-size: 32px; font-weight: bold; }}
                    .content {{ background-color: #374151; padding: 30px; border-radius: 10px; }}
                    .premium-badge {{ 
                        background: linear-gradient(45deg, #fbbf24, #f59e0b);
                        color: #1a1a1a;
                        padding: 10px 20px;
                        border-radius: 25px;
                        font-weight: bold;
                        display: inline-block;
                        margin: 10px 0;
                    }}
                    .footer {{ text-align: center; margin-top: 30px; color: #9ca3af; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">ASFORP</div>
                        <p>Asesoría y Formación Profesional</p>
                    </div>
                    
                    <div class="content">
                        <h2>¡Felicidades {user_name}!</h2>
                        
                        <div style="text-align: center;">
                            <div class="premium-badge">✨ USUARIO PREMIUM ✨</div>
                        </div>
                        
                        <p>Tu pago ha sido procesado exitosamente y ahora tienes acceso completo a todo nuestro contenido premium de formación.</p>
                        
                        <h3>¿Qué incluye tu membresía premium?</h3>
                        <ul>
                            <li>Acceso a todos los cursos de formación profesional</li>
                            <li>Material exclusivo y recursos descargables</li>
                            <li>Certificados de finalización</li>
                            <li>Soporte prioritario</li>
                            <li>Actualizaciones de contenido sin costo adicional</li>
                        </ul>
                        
                        <p>Ya puedes acceder a la sección de formación en tu cuenta.</p>
                        
                        <p>¡Gracias por confiar en ASFORP para tu desarrollo profesional!</p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2024 ASFORP - Asesoría y Formación Profesional</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            ¡Felicidades {user_name}!
            
            Tu pago ha sido procesado exitosamente y ahora tienes acceso completo a todo nuestro contenido premium de formación.
            
            ¿Qué incluye tu membresía premium?
            - Acceso a todos los cursos de formación profesional
            - Material exclusivo y recursos descargables
            - Certificados de finalización
            - Soporte prioritario
            - Actualizaciones de contenido sin costo adicional
            
            Ya puedes acceder a la sección de formación en tu cuenta.
            
            ¡Gracias por confiar en ASFORP para tu desarrollo profesional!
            
            © 2024 ASFORP - Asesoría y Formación Profesional
            """
            
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            print(f"[EMAIL SIMULADO] Enviando email de confirmación premium a: {user_email}")
            
            return True
            
        except Exception as e:
            print(f"Error enviando email premium: {str(e)}")
            return False

