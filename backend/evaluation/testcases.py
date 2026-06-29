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
    }
]