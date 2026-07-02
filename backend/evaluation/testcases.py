TEST_CASES = [
    {
        "name": "VPN connection issue should route to Network Operations Team",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "IT",
            "subject": "VPN not connecting",
            "description": "I am unable to connect to VPN. It keeps showing authentication failed even after entering correct password.",
            "urgency": "High"
        },
        "expected_category": "Network Issue",
        "expected_team": "Network Operations Team",
        "expected_web_search_used": False
    },
    {
        "name": "Account locked issue should route to Security IAM Team",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "IT",
            "subject": "Account locked",
            "description": "My account is locked after multiple failed login attempts and I cannot access email or VPN.",
            "urgency": "High"
        },
        "expected_category": "Access Issue",
        "expected_team": "Security / IAM Team",
        "expected_web_search_used": False
    },
    {
        "name": "Outlook email issue should route to Messaging Email Support Team",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "IT",
            "subject": "Outlook not sending email",
            "description": "My emails are stuck in outbox and Outlook is not syncing.",
            "urgency": "Medium"
        },
        "expected_category": "Email Issue",
        "expected_team": "Messaging / Email Support Team",
        "expected_web_search_used": False
    },
    {
        "name": "Monitor issue should route to Desktop Support Team",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "IT",
            "subject": "Monitor not working",
            "description": "My external monitor is not turning on after connecting HDMI cable.",
            "urgency": "Medium"
        },
        "expected_category": "Hardware Issue",
        "expected_team": "Desktop Support Team",
        "expected_web_search_used": True
    },
    {
        "name": "Keyboard issue should route to Desktop Support Team",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "IT",
            "subject": "Keyboard problem",
            "description": "Some keys on my keyboard are not working properly.",
            "urgency": "Low"
        },
        "expected_category": "Hardware Issue",
        "expected_team": "Desktop Support Team",
        "expected_web_search_used": True
    },
    {
        "name": "API timeout should route to Backend or DevOps Team",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "Engineering",
            "subject": "API timeout after deployment",
            "description": "The API is timing out after latest deployment and users are unable to complete requests.",
            "urgency": "High"
        },
        "expected_category": ["Bug", "Performance Issue"],
        "expected_team": ["Backend Team", "DevOps Team"],
        "expected_web_search_used": False
    },
    {
        "name": "Docker issue should trigger web search fallback",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "Engineering",
            "subject": "Docker container not starting",
            "description": "My Docker container exits immediately after running docker compose up. The logs show exit code 1.",
            "urgency": "High"
        },
        "expected_category": "General Support",
        "expected_team": "General Support Team",
        "expected_web_search_used": True
    },
    {
        "name": "GitHub Actions issue should trigger web search fallback",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "Engineering",
            "subject": "GitHub Actions workflow failed",
            "description": "Our GitHub Actions CI pipeline is failing during the build step after dependency installation.",
            "urgency": "Medium"
        },
        "expected_category": "General Support",
        "expected_team": "General Support Team",
        "expected_web_search_used": True
    },
    {
        "name": "Production outage should trigger critical escalation and guardrail",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "Operations",
            "subject": "Production system down for all customers",
            "description": "Our production system is completely down and all users are affected. No one can access the application and customer transactions are blocked.",
        },
        "expected_category": "Production Outage",
        "expected_team": "Incident Response Team",
        "expected_web_search_used": False,
        "expected_priority": "Critical",
        "expected_guardrail_applied": True,
        "expected_escalation_required": True,
        "expected_sla_breach_risk": "High"
    },
    {
        "name": "Security incident should trigger guardrail and security routing",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "Finance",
            "subject": "Suspicious login from unknown device",
            "description": "I received a login alert from a location I do not recognize and my account may be compromised. This looks like a phishing or credential theft event.",
        },
        "expected_category": "Security Incident",
        "expected_team": "Security / IAM Team",
        "expected_web_search_used": False,
        "expected_priority": "Critical",
        "expected_guardrail_applied": True,
        "expected_escalation_required": True,
        "expected_sla_breach_risk": "High"
    },
    {
        "name": "Data loss incident should trigger high priority escalation",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "Sales",
            "subject": "Missing customer records after cleanup",
            "description": "Several customer records are missing after the latest cleanup job and we suspect deleted data or database corruption.",
        },
        "expected_category": "Data Loss Incident",
        "expected_team": "Data Support Team",
        "expected_web_search_used": False,
        "expected_priority": "High",
        "expected_guardrail_applied": True,
        "expected_escalation_required": True,
        "expected_sla_breach_risk": "High"
    },
    {
        "name": "Ambiguous productivity issue should not over-escalate",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "HR",
            "subject": "Need help with report access",
            "description": "I need access to the quarterly report folder and I am not sure which permission group to request. It is not urgent.",
        },
        "expected_category": ["Access Issue", "Service Request", "General Support"],
        "expected_team": ["Security / IAM Team", "Service Desk Team", "General Support Team"],
        "expected_web_search_used": False,
        "expected_priority": ["Low", "Medium"],
        "expected_guardrail_applied": False,
        "expected_escalation_required": False,
        "expected_sla_breach_risk": ["Low", "Medium"]
    },
    {
        "name": "Performance regression after deployment should prefer backend or devops",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "Engineering",
            "subject": "API latency spike after release",
            "description": "After the latest deployment, API response time increased to 15 seconds, requests are timing out, and the backend logs show repeated failures.",
        },
        "expected_category": ["Bug", "Performance Issue"],
        "expected_team": ["Backend Team", "DevOps Team"],
        "expected_web_search_used": False,
        "expected_priority": ["High", "Critical", "Medium"],
        "expected_guardrail_applied": False,
        "expected_escalation_required": True,
        "expected_sla_breach_risk": ["High", "Medium"]
    },
    {
        "name": "Email attachment issue should stay in messaging support path",
        "request": {
            "user_name": "Ritik Yadav",
            "user_email": "ritik@example.com",
            "department": "Legal",
            "subject": "Email attachment not sending",
            "description": "I can compose the email but every time I attach a PDF and send it, the message stays in outbox and never leaves.",
        },
        "expected_category": "Email Issue",
        "expected_team": "Messaging / Email Support Team",
        "expected_web_search_used": False,
        "expected_priority": "Medium",
        "expected_guardrail_applied": False,
        "expected_escalation_required": False,
        "expected_sla_breach_risk": ["Medium", "Low"]
    }
]
