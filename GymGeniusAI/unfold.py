
UNFOLD = {
    "SITE_TITLE": "GymGenius Admin",
    "SITE_HEADER": "GymGenius",
    "SITE_SUBHEADER": "Fitness Platform Administration",
    "SITE_SYMBOL": "fitness_center",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "SHOW_BACK_BUTTON": True,
    "BORDER_RADIUS": "8px",
    "DASHBOARD_CALLBACK": "GymGeniusAI.dashboard.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "oklch(97.5% .01 250)",
            "100": "oklch(94% .02 250)",
            "200": "oklch(88% .04 250)",
            "300": "oklch(80% .08 250)",
            "400": "oklch(70% .14 250)",
            "500": "oklch(60% .2 250)",
            "600": "oklch(52% .23 255)",
            "700": "oklch(45% .2 255)",
            "800": "oklch(38% .16 255)",
            "900": "oklch(32% .12 255)",
            "950": "oklch(25% .1 255)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": "Users & Auth",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "people",
                        "link": "/admin/accounts/user/",
                    },
                    {
                        "title": "Subscription Plans",
                        "icon": "sell",
                        "link": "/admin/accounts/subscriptionplan/",
                    },
                    {
                        "title": "User Subscriptions",
                        "icon": "card_membership",
                        "link": "/admin/accounts/usersubscription/",
                    },
                ],
            },
            {
                "title": "Workouts",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Exercises",
                        "icon": "fitness_center",
                        "link": "/admin/workouts/exercise/",
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": "/admin/workouts/exercisecategory/",
                    },
                    {
                        "title": "User Workouts",
                        "icon": "assignment",
                        "link": "/admin/workouts/userworkout/",
                    },
                    {
                        "title": "Progress",
                        "icon": "trending_up",
                        "link": "/admin/workouts/workoutprogress/",
                    },
                    {
                        "title": "Activities",
                        "icon": "directions_run",
                        "link": "/admin/workouts/activity/",
                    },
                    {
                        "title": "Custom Routines",
                        "icon": "event_note",
                        "link": "/admin/workouts/customroutine/",
                    },
                ],
            },
            {
                "title": "Community",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Challenges",
                        "icon": "emoji_events",
                        "link": "/admin/community/challenge/",
                    },
                    {
                        "title": "Leaderboard",
                        "icon": "leaderboard",
                        "link": "/admin/community/leaderboard/",
                    },
                ],
            },
            {
                "title": "Content",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Articles",
                        "icon": "article",
                        "link": "/admin/articles/article/",
                    },
                    {
                        "title": "Workout Videos",
                        "icon": "videocam",
                        "link": "/admin/articles/workoutvideo/",
                    },
                    {
                        "title": "Gallery",
                        "icon": "photo_library",
                        "link": "/admin/gallery/usergallery/",
                    },
                ],
            },
            {
                "title": "Gamification",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Challenges",
                        "icon": "military_tech",
                        "link": "/admin/gamification/challenge/",
                    },
                    {
                        "title": "Ranks",
                        "icon": "stars",
                        "link": "/admin/gamification/rank/",
                    },
                    {
                        "title": "Activity Types",
                        "icon": "local_activity",
                        "link": "/admin/gamification/activitytype/",
                    },
                    {
                        "title": "User Ranks",
                        "icon": "person_pin",
                        "link": "/admin/gamification/userrank/",
                    },
                    {
                        "title": "Point Transactions",
                        "icon": "receipt_long",
                        "link": "/admin/gamification/pointtransaction/",
                    },
                    {
                        "title": "Weekly Leaderboard",
                        "icon": "calendar_view_week",
                        "link": "/admin/gamification/weeklyleaderboard/",
                    },
                    {
                        "title": "User Streaks",
                        "icon": "local_fire_department",
                        "link": "/admin/gamification/userstreak/",
                    },
                ],
            },
            {
                "title": "Utilities",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Notifications",
                        "icon": "notifications",
                        "link": "/admin/utils/notification/",
                    },
                    {
                        "title": "FAQs",
                        "icon": "help",
                        "link": "/admin/utils/faq/",
                    },
                    {
                        "title": "Contact Options",
                        "icon": "contact_support",
                        "link": "/admin/utils/contactoption/",
                    },
                    {
                        "title": "Favorites",
                        "icon": "favorite",
                        "link": "/admin/utils/favorite/",
                    },
                    {
                        "title": "Privacy Policy",
                        "icon": "policy",
                        "link": "/admin/utils/privacypolicy/",
                    },
                ],
            },
        ],
    },
}

