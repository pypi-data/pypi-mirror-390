"""UUID utilities for deterministic UUID5 generation in Ephemerista."""

import time
import uuid

# Base namespace UUID for Ephemerista project
# This is a UUID5 generated from the DNS namespace and "ephemerista.space"
EPHEMERISTA_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "ephemerista.space")

# Sub-namespaces for different entity types
ASSET_NAMESPACE = uuid.uuid5(EPHEMERISTA_NAMESPACE, "asset")
SCENARIO_NAMESPACE = uuid.uuid5(EPHEMERISTA_NAMESPACE, "scenario")
CHANNEL_NAMESPACE = uuid.uuid5(EPHEMERISTA_NAMESPACE, "channel")
COMMS_NAMESPACE = uuid.uuid5(EPHEMERISTA_NAMESPACE, "comms")
CONSTELLATION_NAMESPACE = uuid.uuid5(EPHEMERISTA_NAMESPACE, "constellation")


def generate_asset_uuid() -> uuid.UUID:
    """Generate a deterministic UUID5 for an asset based on timestamp."""
    # Use current timestamp as name for uniqueness
    name = f"asset_{time.time_ns()}"
    return uuid.uuid5(ASSET_NAMESPACE, name)


def generate_scenario_uuid() -> uuid.UUID:
    """Generate a deterministic UUID5 for a scenario based on timestamp."""
    name = f"scenario_{time.time_ns()}"
    return uuid.uuid5(SCENARIO_NAMESPACE, name)


def generate_channel_uuid() -> uuid.UUID:
    """Generate a deterministic UUID5 for a channel based on timestamp."""
    name = f"channel_{time.time_ns()}"
    return uuid.uuid5(CHANNEL_NAMESPACE, name)


def generate_comms_uuid() -> uuid.UUID:
    """Generate a deterministic UUID5 for a communication system based on timestamp."""
    name = f"comms_{time.time_ns()}"
    return uuid.uuid5(COMMS_NAMESPACE, name)


def generate_constellation_uuid() -> uuid.UUID:
    """Generate a deterministic UUID5 for a constellation based on timestamp."""
    name = f"constellation_{time.time_ns()}"
    return uuid.uuid5(CONSTELLATION_NAMESPACE, name)
