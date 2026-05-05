# SLA configuration per test type (in hours)
# Can be modified anytime without breaking the app

SLA_RULES = {
    # STAT / Emergency
    "STAT - Emergency": 1.0,
    
    # Routine tests (4-5.5 hours range, using 5 as target)
    "Routine - Hematology Manual": 5.0,
    "Routine - Serology": 5.0,
    "Routine - Chemistry": 5.0,
    "Routine - X-ray": 5.0,
    "Routine - Ultrasound": 5.0,
    "Routine - ECG": 5.0,
    "Routine - Spirometry": 5.0,
    
    # Specialized (24 hrs - few days, using 24 as baseline)
    "Specialized - Microbiology": 72.0,  # 3 days
    "Specialized - Histology Cytology": 720.0,  # 30 days
    "Specialized - X-ray Special": 72.0,  # 3 days
    "Specialized - Ultrasound Special": 24.0,
}

# Department phase templates
DEPARTMENT_PHASES = {
    "Lab": {
        "pre_analytical": [
            "sample_collection",
            "sample_labeling", 
            "sample_transport",
            "sample_reception",
            "sample_processing"
        ],
        "analytical": [
            "analysis"
        ],
        "post_analytical": [
            "review",
            "validation",
            "result_upload"
        ]
    },
    "Radiology": {
        "examination": [
            "exam"
        ],
        "post_examination": [
            "post_exam"
        ]
    },
    "Mobile": {
    "registration": [
        "register"
    ],
    "collection": [
        "mobile_collect"  # Changed from "collect" to "mobile_collect"
    ],
    "transport": [
        "transport_to_lab"
    ],
    "results": [
        "deliver_results"
    ]
}
}

# Target times per phase (in minutes) for guidance
PHASE_TARGETS = {
    "sample_collection": 10,
    "sample_labeling": 3,
    "sample_transport": 30,
    "sample_reception": 6,
    "sample_processing": 5,
    "analysis": 90,
    "review": 10,
    "validation": 5,
    "result_upload": 4,
    "exam": 20,
    "post_exam": 2880,  # 48 hrs in minutes
    "register": 10,
    "collect": 10,
    "transport_to_lab": 60,
    "deliver_results": 30
}

# Histology weekly checkpoints
HISTOLOGY_CHECKPOINTS = [
    "fixation_done",
    "embedding_done", 
    "cutting_done",
    "staining_done"
]

def get_sla_hours(test_name):
    """Get SLA in hours for a specific test"""
    return SLA_RULES.get(test_name, 24.0)  # default 24 hours