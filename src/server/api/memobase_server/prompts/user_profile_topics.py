from ..env import CONFIG, LOG
from .types import UserProfileTopic


CANDIDATE_PROFILE_TOPICS: list[UserProfileTopic] = [
    UserProfileTopic(
        "basic_info",
        [
            "Name",
            {
                "name": "Age",
                "description": "integer",
            },
            "Gender",
            "birth_date",
            "nationality",
            "ethnicity",
            "language_spoken",
        ],
    ),
    UserProfileTopic(
        "contact_info",
        [
            "email",
            "phone",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
        ],
    ),
    UserProfileTopic(
        "education",
        [
            "school",
            "degree",
            "major",
            "graduation_year",
            "field_of_study",
            "institutions",
        ],
    ),
    UserProfileTopic(
        "demographics",
        [
            "marital_status",
            "number_of_children",
            "household_income",
        ],
    ),
    UserProfileTopic(
        "work",
        [
            "company",
            "title",
            "workingLocation",
            "jobStartDate",
            "jobEndDate",
            "working_industry",
            "previous_projects",
            "work_skills",
        ],
    ),
    UserProfileTopic(
        "interest",
        [
            "books",
            "book_authors",
            "movies",
            "tv_shows",
            "music",
            "music_genres",
            "foods",
            "sports",
            "outdoor_activities",
            "games",
            "quotes",
        ],
    ),
    UserProfileTopic(
        "lifestyle",
        [
            {"name": "dietary_preferences", "description": "e.g., vegetarian, vegan"},
            "exercise_habits",
            "health_conditions",
            "sleep_patterns",
            "smoking",
            "alcohol",
        ],
    ),
    UserProfileTopic(
        "psychological",
        ["personality", "values", "beliefs", "motivations", "goals"],
    ),
    UserProfileTopic(
        "life_event",
        ["marriage", "relocation", "retirement"],
    ),
]

if CONFIG.overwrite_user_profiles is not None:
    CANDIDATE_PROFILE_TOPICS = [
        UserProfileTopic(up["topic"], up["sub_topics"])
        for up in CONFIG.overwrite_user_profiles
    ]
elif CONFIG.additional_user_profiles:
    _addon_user_profiles = [
        UserProfileTopic(up["topic"], up["sub_topics"])
        for up in CONFIG.additional_user_profiles
    ]
    CANDIDATE_PROFILE_TOPICS.extend(_addon_user_profiles)
if CONFIG.language == "en":
    LOG.info(f"User profiles: {CANDIDATE_PROFILE_TOPICS}")


def formate_profile_topic(topic: UserProfileTopic) -> str:
    if not topic.sub_topics:
        return f"- {topic.topic}"
    return f"- {topic.topic}. Including sub_topics: " + ", ".join(
        [
            f"{sp['name']}"
            + (f"({sp['description']})" if sp.get("description") else "")
            for sp in topic.sub_topics
        ]
    )


def get_prompt():
    return (
        "\n".join([formate_profile_topic(up) for up in CANDIDATE_PROFILE_TOPICS])
        + "\n..."
    )


if __name__ == "__main__":
    print(get_prompt())
