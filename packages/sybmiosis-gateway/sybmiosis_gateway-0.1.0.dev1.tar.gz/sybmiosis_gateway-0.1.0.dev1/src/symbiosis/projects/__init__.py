"""The projects module manages configuration of projects in the AI gateway.

Each project represents a distinct AI application or service that is connected
to one or more models in the model catalog.

For each project we record:

- The project name and description.
- Virtual API keys for accessing models through the gateway.
- A budget for the project, to manage costs.
- A rate limit to control request frequency.
"""