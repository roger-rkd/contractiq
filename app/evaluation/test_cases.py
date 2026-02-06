TEST_CASES = [
    {
        "question": "What law governs this agreement?",
        "expected_keywords": [],
        "expect_absent": True
    },
    {
        "question": "How is personal data handled?",
        "expected_keywords": [],
        "expect_absent": True
    },
    {
        "question": "What are the termination conditions?",
        "expected_keywords": [
            "terminate",
            "termination",
            "breach",
            "insolvency"
        ],
        "expect_absent": False
    }
]
