from typing import Optional
from dataclasses import dataclass, field


@dataclass
class UserProfileTopic:
    topic: str
    sub_topics: list[str] = field(default_factory=list)


CANDIDATE_PROFILE_TOPICS: list[UserProfileTopic] = [
    UserProfileTopic(
        "basic_info",
        [
            "Name",
            "Age",
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
            "dietary_preferences (e.g., vegetarian, vegan)",
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


def get_prompt():
    return (
        "- "
        + "\n- ".join(
            [
                f"'{up.topic}', for example, {', '.join(up.sub_topics) if up.sub_topics else ''}"
                for up in CANDIDATE_PROFILE_TOPICS
            ]
        )
        + "\n..."
    )
