#!/usr/bin/env python3
"""
Decommission Scorer Framework - Risk-Based Prioritization for EC2 & WorkSpaces

This module provides scoring algorithms for prioritizing EC2 and WorkSpaces
decommissioning candidates based on multiple risk signals.

Scoring Framework:
- EC2 Signals (7 signals, 0-100 scale):
  E1: Compute Optimizer Idle (60 points) - Max CPU ≤1% over 14 days
  E2: SSM Agent Offline/Stale (8 points) - >7 days since heartbeat
  E3: No Network Activity (8 points) - NetworkIn <threshold MB/day
  E4: Stopped State (8 points) - Instance stopped >30 days
  E5: Old Snapshot (6 points) - AMI/snapshot >180 days old
  E6: No Tags/Owner (5 points) - Missing critical tags
  E7: Dev/Test Environment (3 points) - Non-production classification

- WorkSpaces Signals (6 signals, 0-100 scale):
  W1: No Connection (45 points) - >90 days since last connection
  W2: Connection History (25 points) - <10% connection days over 90 days
  W3: ALWAYS_ON Non-Compliant (10 points) - <40 hrs/mo usage
  W4: Stopped State (10 points) - WorkSpace stopped >30 days
  W5: No User Tags (5 points) - Missing cost allocation tags
  W6: Test/Dev Environment (5 points) - Non-production classification

Decommission Tiers (0-100 scale):
- MUST (80-100): Immediate candidates (high confidence)
- SHOULD (50-79): Strong candidates (review recommended)
- COULD (25-49): Potential candidates (manual review required)
- KEEP (<25): Active resources (no action)

Pattern: Follows base_enrichers.py pattern (Rich CLI, configurable thresholds)

Usage:
    from runbooks.finops.decommission_scorer import calculate_ec2_score

    # Calculate EC2 decommission score
    signals = {
        'E1': 60,  # Compute Optimizer Idle
        'E2': 8,   # SSM Agent Offline
        'E3': 8,   # No Network Activity
        'E4': 0,   # Running (not stopped)
        'E5': 6,   # Old Snapshot
        'E6': 5,   # No Tags
        'E7': 3    # Dev Environment
    }

    result = calculate_ec2_score(signals)
    # Returns: {
    #     'total_score': 90,
    #     'tier': 'MUST',
    #     'recommendation': 'Immediate decommission candidate',
    #     'signals': signals,
    #     'confidence': 'High'
    # }

Strategic Alignment:
- Objective 1 (runbooks package): Reusable scoring for notebooks
- Enterprise SDLC: Evidence-based prioritization with audit trails
- KISS/DRY/LEAN: Configurable thresholds, transparent calculations
"""

import logging
from typing import Dict, List, Optional

from ..common.rich_utils import (
    console,
    create_table,
    print_error,
    print_info,
    print_success,
    print_warning,
)

logger = logging.getLogger(__name__)

# Default EC2 signal weights (0-100 scale, total: 100 points max)
# Reference: .claude/prompts/aws-compute/ec2-workspaces.scoring.md lines 56-64
DEFAULT_EC2_WEIGHTS = {
    'E1': 60,  # Compute Optimizer Idle (max CPU ≤1% for 14 days)
    'E2': 10,  # CloudWatch CPU+Network (p95 CPU ≤3%, Network ≤10MB/day)
    'E3': 8,   # CloudTrail activity (no write events for 90 days)
    'E4': 8,   # SSM heartbeat (PingStatus != Online OR LastPingDateTime > 14d)
    'E5': 6,   # Service attachment (not in ASG/LB/ECS/EKS)
    'E6': 5,   # Storage I/O (p95 DiskReadOps+DiskWriteOps ≈ 0)
    'E7': 3    # Cost Explorer rightsizing (terminate savings > $0)
}

# Default WorkSpaces signal weights (0-100 scale, total: 100 points max)
DEFAULT_WORKSPACES_WEIGHTS = {
    'W1': 45,  # No Connection (>90 days)
    'W2': 25,  # Connection History (<10% days)
    'W3': 10,  # ALWAYS_ON Non-Compliant (<40 hrs/mo)
    'W4': 10,  # Stopped State (>30 days)
    'W5': 5,   # No User Tags
    'W6': 5    # Test/Dev Environment
}

# Decommission tier thresholds
TIER_THRESHOLDS = {
    'MUST': 80,     # 80-100: Immediate candidates
    'SHOULD': 50,   # 50-79: Strong candidates
    'COULD': 25,    # 25-49: Potential candidates
    'KEEP': 0       # 0-24: Active resources
}


def calculate_ec2_score(
    signals: Dict[str, int],
    custom_weights: Optional[Dict[str, int]] = None,
    tier_thresholds: Optional[Dict[str, int]] = None
) -> Dict:
    """
    Calculate EC2 decommission score from multiple signals.

    Scoring Logic:
    - Sum of weighted signals (0-100 scale)
    - Each signal contributes its weight if criteria met
    - Tier classification based on total score
    - High transparency: breakdown included in result

    Args:
        signals: Dictionary of signal scores (E1-E7)
                 Signal key → score (0 for absent, weight for present)
                 Example: {'E1': 60, 'E2': 0, 'E3': 8, 'E4': 0, 'E5': 6, 'E6': 5, 'E7': 3}
        custom_weights: Optional custom signal weights (override defaults)
        tier_thresholds: Optional custom tier thresholds (override defaults)

    Returns:
        Dictionary with scoring results:
        {
            'total_score': 82,
            'tier': 'MUST',
            'recommendation': 'Immediate decommission candidate',
            'signals': {
                'E1': {'score': 60, 'weight': 60, 'description': 'Compute Optimizer Idle'},
                'E2': {'score': 0, 'weight': 8, 'description': 'SSM Agent Offline/Stale'},
                ...
            },
            'confidence': 'High',  # Based on signal coverage
            'breakdown': 'E1(60) + E3(8) + E5(6) + E6(5) + E7(3) = 82'
        }

    Example:
        >>> signals = {'E1': 60, 'E2': 0, 'E3': 8, 'E4': 0, 'E5': 6, 'E6': 5, 'E7': 3}
        >>> result = calculate_ec2_score(signals)
        >>> print(f"Score: {result['total_score']}, Tier: {result['tier']}")
        Score: 82, Tier: MUST

    Signal Descriptions (per ec2-workspaces.scoring.md):
        E1: Compute Optimizer identifies instance as idle (max CPU ≤1% over 14 days)
        E2: CloudWatch metrics show low activity (p95 CPU ≤3%, Network ≤10MB/day)
        E3: CloudTrail shows no write events for instance over 90 days
        E4: SSM agent heartbeat offline or stale (PingStatus != Online OR >14d)
        E5: No service attachment (not in ASG/LB/ECS/EKS cluster)
        E6: Storage I/O minimal (p95 DiskReadOps + DiskWriteOps ≈ 0)
        E7: Cost Explorer recommends termination with savings > $0
    """
    try:
        # Use custom weights if provided, otherwise defaults
        weights = custom_weights or DEFAULT_EC2_WEIGHTS
        thresholds = tier_thresholds or TIER_THRESHOLDS

        # Signal descriptions for transparency (matches specification)
        signal_descriptions = {
            'E1': 'Compute Optimizer Idle (max CPU ≤1% for 14d)',
            'E2': 'CloudWatch CPU+Network (p95 ≤3%, ≤10MB/day)',
            'E3': 'CloudTrail no write events (90d)',
            'E4': 'SSM heartbeat (offline or >14d stale)',
            'E5': 'No service attachment (ASG/LB/ECS/EKS)',
            'E6': 'Storage I/O idle (p95 DiskOps ≈ 0)',
            'E7': 'Cost Explorer terminate savings'
        }

        # Calculate total score
        total_score = 0
        signal_breakdown = {}
        contributing_signals = []

        for signal_id, signal_score in signals.items():
            if signal_id not in weights:
                logger.warning(f"Unknown EC2 signal: {signal_id} (skipped)")
                continue

            weight = weights[signal_id]
            description = signal_descriptions.get(signal_id, f"Signal {signal_id}")

            # Add to total if signal is present (score > 0)
            if signal_score > 0:
                total_score += signal_score
                contributing_signals.append(f"{signal_id}({signal_score})")

            signal_breakdown[signal_id] = {
                'score': signal_score,
                'weight': weight,
                'description': description,
                'contributing': signal_score > 0
            }

        # Determine tier
        tier = 'KEEP'
        for tier_name, threshold in sorted(thresholds.items(), key=lambda x: x[1], reverse=True):
            if total_score >= threshold:
                tier = tier_name
                break

        # Determine recommendation
        recommendations = {
            'MUST': 'Immediate decommission candidate (high confidence)',
            'SHOULD': 'Strong decommission candidate (review recommended)',
            'COULD': 'Potential decommission candidate (manual review required)',
            'KEEP': 'Active resource (no decommission action)'
        }
        recommendation = recommendations.get(tier, 'Unknown')

        # Determine confidence based on signal coverage
        signal_count = len([s for s in signals.values() if s > 0])
        if signal_count >= 4:
            confidence = 'High'
        elif signal_count >= 2:
            confidence = 'Medium'
        else:
            confidence = 'Low'

        # Build breakdown string
        if contributing_signals:
            breakdown = ' + '.join(contributing_signals) + f' = {total_score}'
        else:
            breakdown = 'No signals detected = 0'

        return {
            'total_score': total_score,
            'tier': tier,
            'recommendation': recommendation,
            'signals': signal_breakdown,
            'confidence': confidence,
            'breakdown': breakdown,
            'signal_count': signal_count,
            'max_possible_score': sum(weights.values())
        }

    except Exception as e:
        logger.error(f"EC2 score calculation error: {e}", exc_info=True)
        return {
            'total_score': 0,
            'tier': 'ERROR',
            'recommendation': f'Scoring error: {str(e)}',
            'signals': {},
            'confidence': 'N/A',
            'breakdown': 'Error',
            'error': str(e)
        }


def calculate_workspaces_score(
    signals: Dict[str, int],
    custom_weights: Optional[Dict[str, int]] = None,
    tier_thresholds: Optional[Dict[str, int]] = None
) -> Dict:
    """
    Calculate WorkSpaces decommission score from multiple signals.

    Scoring Logic:
    - Sum of weighted signals (0-100 scale)
    - Each signal contributes its weight if criteria met
    - Tier classification based on total score
    - High transparency: breakdown included in result

    Args:
        signals: Dictionary of signal scores (W1-W6)
                 Signal key → score (0 for absent, weight for present)
                 Example: {'W1': 45, 'W2': 25, 'W3': 0, 'W4': 0, 'W5': 5, 'W6': 5}
        custom_weights: Optional custom signal weights (override defaults)
        tier_thresholds: Optional custom tier thresholds (override defaults)

    Returns:
        Dictionary with scoring results:
        {
            'total_score': 80,
            'tier': 'MUST',
            'recommendation': 'Immediate decommission candidate',
            'signals': {
                'W1': {'score': 45, 'weight': 45, 'description': 'No Connection (>90 days)'},
                'W2': {'score': 25, 'weight': 25, 'description': 'Connection History (<10%)'},
                ...
            },
            'confidence': 'High',
            'breakdown': 'W1(45) + W2(25) + W5(5) + W6(5) = 80'
        }

    Example:
        >>> signals = {'W1': 45, 'W2': 25, 'W3': 0, 'W4': 0, 'W5': 5, 'W6': 5}
        >>> result = calculate_workspaces_score(signals)
        >>> print(f"Score: {result['total_score']}, Tier: {result['tier']}")
        Score: 80, Tier: MUST

    Signal Descriptions:
        W1: No connection detected (>90 days since last user connection)
        W2: Low connection history (<10% connection days over 90 days)
        W3: ALWAYS_ON mode with low usage (<40 hours/month breakeven threshold)
        W4: WorkSpace in stopped state (>30 days)
        W5: Missing user/cost allocation tags
        W6: Classified as test/dev environment (non-production)
    """
    try:
        # Use custom weights if provided, otherwise defaults
        weights = custom_weights or DEFAULT_WORKSPACES_WEIGHTS
        thresholds = tier_thresholds or TIER_THRESHOLDS

        # Signal descriptions for transparency
        signal_descriptions = {
            'W1': 'No Connection (>90 days)',
            'W2': 'Connection History (<10% days)',
            'W3': 'ALWAYS_ON Non-Compliant (<40 hrs/mo)',
            'W4': 'Stopped State (>30 days)',
            'W5': 'No User Tags',
            'W6': 'Test/Dev Environment'
        }

        # Calculate total score
        total_score = 0
        signal_breakdown = {}
        contributing_signals = []

        for signal_id, signal_score in signals.items():
            if signal_id not in weights:
                logger.warning(f"Unknown WorkSpaces signal: {signal_id} (skipped)")
                continue

            weight = weights[signal_id]
            description = signal_descriptions.get(signal_id, f"Signal {signal_id}")

            # Add to total if signal is present (score > 0)
            if signal_score > 0:
                total_score += signal_score
                contributing_signals.append(f"{signal_id}({signal_score})")

            signal_breakdown[signal_id] = {
                'score': signal_score,
                'weight': weight,
                'description': description,
                'contributing': signal_score > 0
            }

        # Determine tier
        tier = 'KEEP'
        for tier_name, threshold in sorted(thresholds.items(), key=lambda x: x[1], reverse=True):
            if total_score >= threshold:
                tier = tier_name
                break

        # Determine recommendation
        recommendations = {
            'MUST': 'Immediate decommission candidate (high confidence)',
            'SHOULD': 'Strong decommission candidate (review recommended)',
            'COULD': 'Potential decommission candidate (manual review required)',
            'KEEP': 'Active resource (no decommission action)'
        }
        recommendation = recommendations.get(tier, 'Unknown')

        # Determine confidence based on signal coverage
        signal_count = len([s for s in signals.values() if s > 0])
        if signal_count >= 3:
            confidence = 'High'
        elif signal_count >= 2:
            confidence = 'Medium'
        else:
            confidence = 'Low'

        # Build breakdown string
        if contributing_signals:
            breakdown = ' + '.join(contributing_signals) + f' = {total_score}'
        else:
            breakdown = 'No signals detected = 0'

        return {
            'total_score': total_score,
            'tier': tier,
            'recommendation': recommendation,
            'signals': signal_breakdown,
            'confidence': confidence,
            'breakdown': breakdown,
            'signal_count': signal_count,
            'max_possible_score': sum(weights.values())
        }

    except Exception as e:
        logger.error(f"WorkSpaces score calculation error: {e}", exc_info=True)
        return {
            'total_score': 0,
            'tier': 'ERROR',
            'recommendation': f'Scoring error: {str(e)}',
            'signals': {},
            'confidence': 'N/A',
            'breakdown': 'Error',
            'error': str(e)
        }


def display_scoring_summary(
    scores: List[Dict],
    resource_type: str = 'EC2'
) -> None:
    """
    Display scoring summary with Rich CLI formatting.

    Args:
        scores: List of scoring results from calculate_ec2_score() or calculate_workspaces_score()
        resource_type: 'EC2' or 'WorkSpaces' for display customization

    Example:
        >>> ec2_scores = [calculate_ec2_score(s) for s in signal_list]
        >>> display_scoring_summary(ec2_scores, resource_type='EC2')
    """
    try:
        # Count by tier
        tier_counts = {
            'MUST': 0,
            'SHOULD': 0,
            'COULD': 0,
            'KEEP': 0
        }

        for score in scores:
            tier = score.get('tier', 'KEEP')
            if tier in tier_counts:
                tier_counts[tier] += 1

        # Create summary table
        table = create_table(
            title=f"{resource_type} Decommission Scoring Summary",
            columns=[
                {"header": "Tier", "style": "cyan bold"},
                {"header": "Count", "style": "yellow"},
                {"header": "Percentage", "style": "green"},
                {"header": "Recommendation", "style": "blue"}
            ]
        )

        total = len(scores)
        if total == 0:
            print_warning("⚠️  No scores to display")
            return

        recommendations = {
            'MUST': 'Immediate decommission (80-100)',
            'SHOULD': 'Review for decommission (50-79)',
            'COULD': 'Manual review required (25-49)',
            'KEEP': 'Active resource (<25)'
        }

        for tier in ['MUST', 'SHOULD', 'COULD', 'KEEP']:
            count = tier_counts[tier]
            percentage = (count / total * 100) if total > 0 else 0
            recommendation = recommendations[tier]

            table.add_row(
                tier,
                str(count),
                f"{percentage:.1f}%",
                recommendation
            )

        console.print(table)

        # Priority statistics
        priority_count = tier_counts['MUST'] + tier_counts['SHOULD']
        priority_pct = (priority_count / total * 100) if total > 0 else 0

        if priority_count > 0:
            print_success(f"✅ Identified {priority_count} priority decommission candidates ({priority_pct:.1f}%)")
        else:
            print_info(f"ℹ️  No high-priority decommission candidates identified")

    except Exception as e:
        print_error(f"❌ Scoring summary display failed: {e}")
        logger.error(f"Display error: {e}", exc_info=True)


def export_scores_to_dataframe(
    scores: List[Dict],
    resource_ids: List[str]
):
    """
    Export scoring results to pandas DataFrame.

    Args:
        scores: List of scoring results
        resource_ids: List of resource IDs (instance IDs or WorkSpace IDs)

    Returns:
        pandas DataFrame with scoring columns

    Example:
        >>> scores = [calculate_ec2_score(s) for s in signals_list]
        >>> df = export_scores_to_dataframe(scores, instance_ids)
        >>> df.to_excel('ec2-decommission-scores.xlsx', index=False)
    """
    import pandas as pd

    try:
        # Build DataFrame records
        records = []

        for i, score in enumerate(scores):
            resource_id = resource_ids[i] if i < len(resource_ids) else f"resource-{i}"

            record = {
                'resource_id': resource_id,
                'total_score': score.get('total_score', 0),
                'tier': score.get('tier', 'KEEP'),
                'recommendation': score.get('recommendation', 'N/A'),
                'confidence': score.get('confidence', 'N/A'),
                'signal_count': score.get('signal_count', 0),
                'breakdown': score.get('breakdown', 'N/A')
            }

            records.append(record)

        df = pd.DataFrame(records)

        print_success(f"✅ Exported {len(df)} scores to DataFrame")

        return df

    except Exception as e:
        print_error(f"❌ DataFrame export failed: {e}")
        logger.error(f"Export error: {e}", exc_info=True)
        return pd.DataFrame()


# DataFrame-based Scoring Methods (Track 5: E1-E7/W1-W6 Implementation)


def score_ec2_dataframe(df):
    """
    Apply E1-E7 signals to EC2 DataFrame (100-point scale).

    Signal Breakdown (from ec2-workspaces.scoring.md):
    - E1: Compute Optimizer idle (60 points) - BACKBONE
    - E2: CloudWatch CPU/Network (10 points)
    - E3: CloudTrail activity (8 points)
    - E4: SSM heartbeat (8 points)
    - E5: Service attachment (6 points)
    - E6: Storage I/O (5 points)
    - E7: Cost savings (3 points)

    Classification:
    - MUST (80-100): Create Change Request → Stop → 7-day hold → Terminate
    - SHOULD (50-79): Off-hours stop schedule
    - COULD (25-49): Rightsizing or spot conversion
    - KEEP (<25): Production workload

    Args:
        df: DataFrame with enriched EC2 data (all 4 layers complete)

    Returns:
        DataFrame with 3 new columns: decommission_score, decommission_tier, signal_breakdown
    """
    import pandas as pd
    import json

    df['decommission_score'] = 0
    df['signal_breakdown'] = '{}'
    df['decommission_tier'] = 'KEEP'

    for idx, row in df.iterrows():
        score = 0
        signals = {}

        # E1: Compute Optimizer idle (60 points - BACKBONE SIGNAL)
        if row.get('compute_optimizer_finding') == 'Idle':
            score += 60
            signals['E1'] = 60

        # E2: CloudWatch CPU/Network (10 points)
        p95_cpu = row.get('p95_cpu_utilization', 100)
        p95_network = row.get('p95_network_bytes', float('inf'))
        E2_NETWORK_THRESHOLD_MB = 10  # Configurable parameter

        if p95_cpu <= 3.0 and p95_network <= (E2_NETWORK_THRESHOLD_MB * 1024 * 1024):
            score += 10
            signals['E2'] = 10

        # E3: CloudTrail activity (8 points)
        if row.get('days_since_activity', 0) >= 90:
            score += 8
            signals['E3'] = 8

        # E4: SSM heartbeat (8 points)
        if row.get('ssm_ping_status') != 'Online' or row.get('ssm_days_since_ping', 0) > 14:
            score += 8
            signals['E4'] = 8

        # E5: Service attachment (6 points)
        if not row.get('attached_to_service', False):
            score += 6
            signals['E5'] = 6

        # E6: Storage I/O (5 points)
        if row.get('p95_disk_io', float('inf')) == 0:
            score += 5
            signals['E6'] = 5

        # E7: Cost savings (3 points)
        if row.get('cost_explorer_savings_terminate', 0) > 0:
            score += 3
            signals['E7'] = 3

        # Classification
        if score >= 80:
            tier = 'MUST'
        elif score >= 50:
            tier = 'SHOULD'
        elif score >= 25:
            tier = 'COULD'
        else:
            tier = 'KEEP'

        df.at[idx, 'decommission_score'] = score
        df.at[idx, 'decommission_tier'] = tier
        df.at[idx, 'signal_breakdown'] = json.dumps(signals)

    return df


def score_workspaces_dataframe(df):
    """
    Apply W1-W6 signals to WorkSpaces DataFrame (100-point scale).

    Signal Breakdown:
    - W1: Connection recency (45 points) - ≥60 days since last connection
    - W2: CloudWatch usage (25 points) - UserConnected sum = 0
    - W3: Billing vs usage (10/5 points) - Dynamic break-even via Pricing API
    - W4: Cost Optimizer policy (10 points) - Flagged for termination
    - W5: Admin activity (5 points) - No admin changes for 90 days
    - W6: User status (5 points) - User NOT in Identity Center

    Args:
        df: DataFrame with enriched WorkSpaces data (all 4 layers complete)

    Returns:
        DataFrame with 3 new columns: decommission_score, decommission_tier, signal_breakdown
    """
    import pandas as pd
    import json

    df['decommission_score'] = 0
    df['signal_breakdown'] = '{}'
    df['decommission_tier'] = 'KEEP'

    for idx, row in df.iterrows():
        score = 0
        signals = {}

        # W1: Connection recency (45 points)
        days_since_connection = row.get('days_since_connection', 0)
        if days_since_connection >= 60:
            score += 45
            signals['W1'] = 45

        # W2: CloudWatch usage (25 points)
        if row.get('user_connected_sum', 1) == 0:
            score += 25
            signals['W2'] = 25

        # W3: Billing vs usage (10/5 points)
        hourly_usage = row.get('hourly_usage_hours_mtd', 0)
        dynamic_breakeven = row.get('dynamic_breakeven_hours', 85)  # From Pricing API

        if hourly_usage < dynamic_breakeven:
            score += 10
            signals['W3'] = 10
        elif hourly_usage >= dynamic_breakeven:
            score += 5
            signals['W3'] = 5

        # W4: Cost Optimizer policy (10 points)
        if row.get('cost_optimizer_flags_termination', False):
            score += 10
            signals['W4'] = 10

        # W5: Admin activity (5 points)
        if row.get('no_admin_activity_90d', False):
            score += 5
            signals['W5'] = 5

        # W6: User status (5 points - Identity Center)
        if row.get('user_not_in_identity_center', False):
            score += 5
            signals['W6'] = 5

        # Classification (same thresholds)
        if score >= 80:
            tier = 'MUST'
        elif score >= 50:
            tier = 'SHOULD'
        elif score >= 25:
            tier = 'COULD'
        else:
            tier = 'KEEP'

        df.at[idx, 'decommission_score'] = score
        df.at[idx, 'decommission_tier'] = tier
        df.at[idx, 'signal_breakdown'] = json.dumps(signals)

    return df


def display_tier_distribution(df) -> None:
    """
    Display decommission tier distribution with Rich table.

    Args:
        df: DataFrame with decommission_tier and decommission_score columns

    Example:
        >>> df = score_ec2_dataframe(enriched_df)
        >>> display_tier_distribution(df)
    """
    import pandas as pd

    if 'decommission_tier' not in df.columns:
        print_warning("⚠️  No decommission_tier column found in DataFrame")
        return

    # Tier distribution
    tier_counts = df['decommission_tier'].value_counts()
    total = len(df)

    summary_rows = []
    for tier in ['MUST', 'SHOULD', 'COULD', 'KEEP']:
        count = tier_counts.get(tier, 0)
        pct = (count / total * 100) if total > 0 else 0
        summary_rows.append([tier, f"{count} resources ({pct:.1f}%)"])

    # Add separator and top 5 decommission candidates (MUST tier)
    if 'decommission_score' in df.columns:
        must_candidates = df[df['decommission_tier'] == 'MUST'].nlargest(5, 'decommission_score')
        if len(must_candidates) > 0:
            summary_rows.append(["", ""])  # Separator
            summary_rows.append(["Top Candidates", "Score"])
            for idx, row in must_candidates.iterrows():
                # Try multiple possible identifier columns
                identifier = row.get('identifier', row.get('resource_id', row.get('instance_id', row.get('workspace_id', 'Unknown'))))
                score = row.get('decommission_score', 0)
                summary_rows.append([f"  {str(identifier)[:30]}", f"{score:.0f}"])

    tier_table = create_table(
        "Decommission Tier Distribution",
        ["Tier", "Count"],
        summary_rows
    )
    console.print(tier_table)

    # Print additional insights
    priority_count = tier_counts.get('MUST', 0) + tier_counts.get('SHOULD', 0)
    priority_pct = (priority_count / total * 100) if total > 0 else 0

    if priority_count > 0:
        print_success(f"✅ Identified {priority_count} priority decommission candidates ({priority_pct:.1f}%)")
    else:
        print_info(f"ℹ️  No high-priority decommission candidates identified")


def calculate_production_ready_score(validation_results: Dict) -> Dict:
    """
    Calculate production-ready score (Section 1A framework).

    Scoring Categories:
    - Data Availability: /40 points (Excel validated, MCP ≥99.5%, signals present, provenance)
    - Workflow Execution: /30 points (MCP queries, CLI tested, notebook operational)
    - Technical Credibility: /30 points (src/runbooks/ changes, execution evidence, manager summary)

    Threshold: ≥70/100 for production-ready status

    Args:
        validation_results: Dictionary with validation test results

    Returns:
        Dictionary with score breakdown and status
    """
    score = {
        'data_availability': 0,      # /40
        'workflow_execution': 0,     # /30
        'technical_credibility': 0,  # /30
        'total': 0,
        'threshold': 70,
        'status': 'BLOCKED'
    }

    # Data Availability (40 points)
    if validation_results.get('excel_validated'):
        score['data_availability'] += 10
    if validation_results.get('mcp_accuracy', 0) >= 0.995:
        score['data_availability'] += 15
    if validation_results.get('decommission_signals_present'):
        score['data_availability'] += 10
    if validation_results.get('data_provenance_documented'):
        score['data_availability'] += 5

    # Workflow Execution (30 points)
    if validation_results.get('mcp_queries_executed'):
        score['workflow_execution'] += 15
    if validation_results.get('cli_tested'):
        score['workflow_execution'] += 10
    if validation_results.get('notebook_operational'):
        score['workflow_execution'] += 5

    # Technical Credibility (30 points)
    if validation_results.get('src_runbooks_changes'):
        score['technical_credibility'] += 10
    if validation_results.get('execution_evidence'):
        score['technical_credibility'] += 10
    if validation_results.get('manager_summary_concise'):
        score['technical_credibility'] += 10

    # Calculate total
    score['total'] = score['data_availability'] + score['workflow_execution'] + score['technical_credibility']

    # Determine status
    if score['total'] >= 90:
        score['status'] = 'PRODUCTION-READY'
    elif score['total'] >= 70:
        score['status'] = 'ACCEPTABLE'
    else:
        score['status'] = 'BLOCKED'

    return score
