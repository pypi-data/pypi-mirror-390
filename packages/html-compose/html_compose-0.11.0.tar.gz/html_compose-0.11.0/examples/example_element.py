import html_compose as h
import html_compose.elements as el
from html_compose import a, article, body, br, p, strong


def state_component(username):
    return body()[
        article()[
            p()["Welcome to the internet", strong()[username], "!"],
            br(),
            p()[
                "Have you checked out this cool thing called a ",
                a(href="https://google.com")["search engine"],
                "?",
            ],
        ]
    ]


def demo_one():
    h.HTML5Document(
        title="Welcome",
        lang="en",
        head_extra=[
            el.link(
                rel="stylesheet",
                href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css",
            )
        ],
        body=[state_component("wanderer")],
    )
