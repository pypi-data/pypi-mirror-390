#!/usr/bin/env python3
"""
Tests for RI Utilization Tracker

Basic validation tests for Reserved Instance utilization tracking.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from runbooks.finops.ri_utilization_tracker import (
    RIUtilizationTracker,
    RIUtilizationReport,
    Alert,
    track_ri_utilization,
)


@pytest.fixture
def mock_session():
    """Mock boto3 session for testing."""
    session = Mock()

    # Mock STS client for account ID
    sts_client = Mock()
    sts_client.get_caller_identity.return_value = {'Account': '123456789012'}
    session.client.return_value = sts_client

    return session


@pytest.fixture
def tracker(mock_session):
    """Create RIUtilizationTracker with mocked session."""
    with patch('runbooks.common.profile_utils.create_operational_session') as mock_create:
        mock_create.return_value = mock_session
        tracker = RIUtilizationTracker(
            profile='test-profile',
            threshold=90.0,
            lookback_days=30
        )
        return tracker


def test_tracker_initialization(tracker):
    """Test tracker initialization with correct parameters."""
    assert tracker.profile == 'test-profile'
    assert tracker.threshold == 90.0
    assert tracker.lookback_days == 30
    assert tracker.account_id == '123456789012'


def test_utilization_report_creation():
    """Test RIUtilizationReport dataclass creation."""
    report = RIUtilizationReport(
        service='EC2',
        instance_type='m5.large',
        region='us-east-1',
        account_id='123456789012',
        account_name='Test Account',
        total_reserved_hours=720.0,
        used_hours=500.0,
        unused_hours=220.0,
        utilization_percentage=69.4,
        monthly_cost=100.0,
        wasted_cost=30.6,
        recommendation='Review usage patterns',
        severity='warning'
    )

    assert report.service == 'EC2'
    assert report.utilization_percentage == 69.4
    assert report.severity == 'warning'
    assert report.wasted_cost == 30.6


def test_alert_creation():
    """Test Alert dataclass creation."""
    alert = Alert(
        alert_id='RI-0001',
        service='RDS',
        instance_type='db.m5.large',
        region='us-west-2',
        account_id='123456789012',
        utilization_percentage=65.0,
        wasted_cost=50.0,
        severity='critical',
        message='RDS db.m5.large in us-west-2: 65.0% utilization',
        timestamp=datetime.utcnow()
    )

    assert alert.alert_id == 'RI-0001'
    assert alert.severity == 'critical'
    assert alert.utilization_percentage == 65.0


def test_get_service_name_mapping(tracker):
    """Test service name mapping for Cost Explorer."""
    assert tracker._get_service_name('EC2') == 'Amazon Elastic Compute Cloud - Compute'
    assert tracker._get_service_name('RDS') == 'Amazon Relational Database Service'
    assert tracker._get_service_name('ElastiCache') == 'Amazon ElastiCache'
    assert tracker._get_service_name('Redshift') == 'Amazon Redshift'


def test_generate_alert_message(tracker):
    """Test alert message generation."""
    report = RIUtilizationReport(
        service='EC2',
        instance_type='m5.large',
        region='us-east-1',
        account_id='123456789012',
        account_name='Test Account',
        total_reserved_hours=720.0,
        used_hours=500.0,
        unused_hours=220.0,
        utilization_percentage=69.4,
        monthly_cost=100.0,
        wasted_cost=30.6,
        recommendation='Review usage patterns',
        severity='warning'
    )

    message = tracker._generate_alert_message(report)

    assert 'EC2' in message
    assert 'm5.large' in message
    assert 'us-east-1' in message
    assert '69.4%' in message
    assert '30.60' in message


def test_parse_utilization_data_critical_severity(tracker):
    """Test utilization data parsing with critical severity (<70%)."""
    group = {
        'Keys': ['m5.large', 'us-east-1'],
        'Attributes': {
            'UtilizationPercentage': '65.5',
            'TotalReservedHours': '720',
            'UsedHours': '471.6',
            'TotalAmortizedFee': '100.00'
        }
    }

    time_period = {}

    report = tracker._parse_utilization_data('EC2', group, time_period)

    assert report is not None
    assert report.severity == 'critical'
    assert 'IMMEDIATE ACTION' in report.recommendation
    assert report.utilization_percentage == 65.5


def test_parse_utilization_data_warning_severity(tracker):
    """Test utilization data parsing with warning severity (70-90%)."""
    group = {
        'Keys': ['m5.xlarge', 'us-west-2'],
        'Attributes': {
            'UtilizationPercentage': '85.0',
            'TotalReservedHours': '720',
            'UsedHours': '612.0',
            'TotalAmortizedFee': '200.00'
        }
    }

    time_period = {}

    report = tracker._parse_utilization_data('RDS', group, time_period)

    assert report is not None
    assert report.severity == 'warning'
    assert 'WARNING' in report.recommendation
    assert report.utilization_percentage == 85.0


def test_parse_utilization_data_good_severity(tracker):
    """Test utilization data parsing with good severity (>90%)."""
    group = {
        'Keys': ['cache.m5.large', 'eu-west-1'],
        'Attributes': {
            'UtilizationPercentage': '95.0',
            'TotalReservedHours': '720',
            'UsedHours': '684.0',
            'TotalAmortizedFee': '150.00'
        }
    }

    time_period = {}

    report = tracker._parse_utilization_data('ElastiCache', group, time_period)

    assert report is not None
    assert report.severity == 'good'
    assert 'Good utilization' in report.recommendation
    assert report.utilization_percentage == 95.0


def test_generate_alerts_no_underutilization(tracker):
    """Test alert generation with all RIs above threshold."""
    reports = [
        RIUtilizationReport(
            service='EC2',
            instance_type='m5.large',
            region='us-east-1',
            account_id='123456789012',
            account_name='Test Account',
            total_reserved_hours=720.0,
            used_hours=680.0,
            unused_hours=40.0,
            utilization_percentage=94.4,
            monthly_cost=100.0,
            wasted_cost=5.6,
            recommendation='Good utilization',
            severity='good'
        )
    ]

    alerts = tracker.generate_alerts(reports)

    assert len(alerts) == 0


def test_generate_alerts_with_underutilization(tracker):
    """Test alert generation with underutilized RIs."""
    reports = [
        RIUtilizationReport(
            service='EC2',
            instance_type='m5.large',
            region='us-east-1',
            account_id='123456789012',
            account_name='Test Account',
            total_reserved_hours=720.0,
            used_hours=500.0,
            unused_hours=220.0,
            utilization_percentage=69.4,
            monthly_cost=100.0,
            wasted_cost=30.6,
            recommendation='Review usage patterns',
            severity='critical'
        ),
        RIUtilizationReport(
            service='RDS',
            instance_type='db.m5.large',
            region='us-west-2',
            account_id='123456789012',
            account_name='Test Account',
            total_reserved_hours=720.0,
            used_hours=600.0,
            unused_hours=120.0,
            utilization_percentage=83.3,
            monthly_cost=200.0,
            wasted_cost=33.4,
            recommendation='Review usage patterns',
            severity='warning'
        )
    ]

    alerts = tracker.generate_alerts(reports)

    assert len(alerts) == 2
    assert alerts[0].severity == 'critical'
    assert alerts[1].severity == 'warning'


@patch('runbooks.common.profile_utils.create_operational_session')
@patch('runbooks.finops.ri_utilization_tracker.RIUtilizationTracker.track_utilization')
def test_track_ri_utilization_api(mock_track, mock_session):
    """Test main API function."""
    # Mock session
    mock_session.return_value = Mock()

    # Mock tracker
    mock_track.return_value = [
        RIUtilizationReport(
            service='EC2',
            instance_type='m5.large',
            region='us-east-1',
            account_id='123456789012',
            account_name='Test Account',
            total_reserved_hours=720.0,
            used_hours=500.0,
            unused_hours=220.0,
            utilization_percentage=69.4,
            monthly_cost=100.0,
            wasted_cost=30.6,
            recommendation='Review usage patterns',
            severity='critical'
        )
    ]

    # Call API
    df = track_ri_utilization(
        profile='test-profile',
        threshold=90.0
    )

    # Verify DataFrame
    assert not df.empty
    assert 'Service' in df.columns
    assert 'UtilizationPercentage' in df.columns
    assert len(df) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
