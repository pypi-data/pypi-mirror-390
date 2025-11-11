import html_compose.live as live

live.server(
    # counter.py contents:
    #
    # from time import sleep, time
    # start = time()
    # while True:
    #     now = time()
    #     print(int(now - start))
    #     sleep(1)
    daemon=live.ShellCommand("python3 counter.py"),
    daemon_port=8000,
    daemon_delay=1,
    daemon_timeout=10,
    conds=[
        live.WatchCond(
            path_glob="src/**/*.py", action=live.ShellCommand("date")
        ),
        live.WatchCond(
            path_glob="./static/sass/**/*.scss",
            action=live.ShellCommand(
                ["sass", "--update", "static/sass:static/css"]
            ),
            reload=True,
            server_reload=True,
        ),
        live.WatchCond(path_glob="./static/css/", action=None, delay=0.5),
    ],
)
