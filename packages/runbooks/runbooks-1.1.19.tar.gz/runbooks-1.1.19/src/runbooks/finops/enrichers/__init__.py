"""
FinOps Enrichers Package.

This package provides enrichment functionality for AWS resources,
consolidating enrichers from the parent module.
"""

# Import enrichers from parent module for backward compatibility
from runbooks.finops.ec2_enrichment import (
    enrich_with_ec2_context,
    analyze_ec2_cloudtrail,
    get_ec2_cost_data,
)
from runbooks.finops.workspaces_enrichment import (
    enrich_with_workspaces_context,
    analyze_workspaces_cloudtrail,
    get_workspaces_cost_data,
)
from runbooks.finops.base_enrichers import (
    OrganizationsEnricher,
    CostExplorerEnricher,
    CloudTrailEnricher,
    StoppedStateEnricher,
    format_tags_combined,
)

__all__ = [
    # EC2 enrichers
    "enrich_with_ec2_context",
    "analyze_ec2_cloudtrail",
    "get_ec2_cost_data",
    # WorkSpaces enrichers
    "enrich_with_workspaces_context",
    "analyze_workspaces_cloudtrail",
    "get_workspaces_cost_data",
    # Base enrichers
    "OrganizationsEnricher",
    "CostExplorerEnricher",
    "CloudTrailEnricher",
    "StoppedStateEnricher",
    "format_tags_combined",
]
