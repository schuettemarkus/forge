"""Forge Printer Controller — runs on local LAN with Bambu printers."""

import structlog

logger = structlog.get_logger()


def main() -> None:
    logger.info("forge.printer_controller.starting", msg="Printer controller starting...")
    logger.info(
        "forge.printer_controller.no_printers",
        msg="No printers configured yet. Set up in M4.",
    )


if __name__ == "__main__":
    main()
