# Legal Practice Targets

Before running WVS (Web Vulnerability Scanner) on any target, ensure you have explicit, written authorization. If you want to practice scanning and test the scanner's capabilities safely, use the following intentionally-vulnerable applications.

## Recommended Targets

1. **DVWA (Damn Vulnerable Web App)**
   - A highly vulnerable web application built in PHP/MySQL designed to practice web exploitation.
   - **Running locally via Docker (Recommended)**:
     ```bash
     docker run -d -p 80:80 vulnerables/web-dvwa
     ```
   - *Note: DVWA requires authentication. WVS currently doesn't support session auth, so you will need to add authentication support or run scans against unauthenticated surfaces.*

2. **OWASP Juice Shop**
   - The most modern and sophisticated insecure web application.
   - **Running locally via Docker (Recommended)**:
     ```bash
     docker run -d -p 3000:3000 bkimminich/juice-shop
     ```

3. **Acunetix Test Site**
   - A vulnerable PHP web application explicitly set up for testing scanners.
   - URL: http://testphp.vulnweb.com/

4. **PortSwigger Web Security Academy Labs**
   - Free, online web security training from the creators of Burp Suite. Contains hundreds of labs with isolated environments for each user.
   - URL: https://portswigger.net/web-security
