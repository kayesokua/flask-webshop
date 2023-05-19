# Cybersecurity

## Assets

1. User data (e.g., personal, address information, purchase history)
2. Product data (e.g., descriptions, images, prices)
3. Application code and infrastructure
4. Reputation of the store

## Trust Boundaries

1. Client-browser to web application
2. Web application to 3rd-party authentication provider
3. Web application to 3rd-party payment provider

## Threats and Vulnerabilities

1. Spoofing: Unauthorized access to user accounts, phishing attacks targeting users
2. Tampering: Unauthorized modification of product data, SQL injection
3. Repudiation: Disputes about user actions (e.g., unauthorized purchases)
4. Information Disclosure: Leakage of sensitive user or product data
5. Denial of Service (DoS): Resource exhaustion attacks (e.g., flooding requests)
6. Elevation of Privilege: Unauthorized access to admin features or sensitive data

## Mitigation Strategies

Spoofing Prevention

- [x] Securely store passwords with bcrypt hashing and salt.
- [x] Enforce strong password policies during registration, requiring at least one symbol, one number, and a minimum length
- [x] Prompt users to change passwords every 90 days
- [x] Implement mobile verification to prevent phishing attacks and ensure purchases are made by account holders
- [ ] Educate users about potential phising attacks

Tampering Prevention

- [x] Deploy to a platform that supports SSL (e.g., Heroku) and implement Content Security Policy
- [x] Use SQLAlchemy to avoid SQL injection attacks and perform input validation on all user inputs
- [ ] Implement HTTPS to prevent eavesdropping and ensure data integrity through digital signatures
- [x] Use secure cookies and implement the HttpOnly and Secure attributes

Repudiation
- [x] Preserving the data to protect against fraudulent activities or misunderstandings by establishing a reliable historical record.

Information Disclosure

- [x]  Mask sensitive information on the front-end using asterisks
- [ ]  Encrypt sensitive data both at rest and in transit

Denial of Service

- [x] Implement rate limiting based on expected usage
- [x] Use cache-based amplification for product pages and search results to reduce server load
- [ ] Employ a Web Application Firewall (WAF) to filter out malicious traffic

Elevation of Privilege

- [ ] Implement role-based permissions to prevent unauthorized access to sensitive functionality
- [x] Regularly review and update user permissions to ensure least privilege access

Others (Ex. Collaboration)

- [x] Ensuring secret keys are implemented to `.gitignore` and use environment variables for sensitive information
- [x] Configure repository settings to require approval from a listed collaborator before merging changes
- [ ] Set up Docker to create a consistent and isolated environment for development and deployment
- [x] Limit database access and mask sensitive information for engineers who do not require full access

## Testing Cybersecurity Measures

- [ ] Perform vulnerability scanning to scan your application for known vulnerabilities and security misconfigurations
- [ ] Plan and conduct penetration testing
- [ ] Incorporate security testing into your continuous integration (CI) pipeline

# Resources

1. https://owasp.org/www-community/Threat_Modeling_Process
2. https://www.practical-devsecops.com/what-is-stride-threat-model/
