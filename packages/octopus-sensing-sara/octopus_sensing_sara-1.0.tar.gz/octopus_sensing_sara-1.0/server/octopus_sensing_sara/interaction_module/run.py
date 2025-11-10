"""Application entry point."""

import logging
import uvicorn

# Configure uvicorn to use clean logging format
if __name__ == "__main__":
    # Set log config to suppress default uvicorn formatting
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["default"]["fmt"] = "%(message)s"
    log_config["formatters"]["access"]["fmt"] = "%(message)s"

    uvicorn.run(
        "octopus_sensing_sara.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="warning",  # Reduce uvicorn verbosity
        log_config=log_config,
    )
