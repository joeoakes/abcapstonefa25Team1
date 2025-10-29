def init_app(app_type: str):
    if app_type == "cli":
        from abcapstonefa25team1.frontend.cli.app import main as cli_main

        return cli_main
    elif app_type == "gui":
        from abcapstonefa25team1.frontend.gui.app import main as gui_main

        return gui_main
    else:
        raise ValueError(f"Unknown app type: {app_type}")
