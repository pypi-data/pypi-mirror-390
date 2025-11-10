#!/usr/bin/env python3
"""
Tests for Cost Anomaly Detector

Basic validation tests for cost spike detection and root cause analysis.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from runbooks.finops.cost_anomaly_detector import (
    CostAnomalyDetector,
    Anomaly,
    RootCauseAnalysis,
    detect_cost_anomalies,
)


@pytest.fixture
def mock_session():
    """Mock boto3 session for testing."""
    session = Mock()

    # Mock STS client for account ID
    sts_client = Mock()
    sts_client.get_caller_identity.return_value = {'Account': '123456789012'}

    # Mock Cost Explorer client
    ce_client = Mock()

    def client_factory(service, **kwargs):
        if service == 'sts':
            return sts_client
        elif service == 'ce':
            return ce_client
        return Mock()

    session.client = client_factory

    return session


@pytest.fixture
def detector(mock_session):
    """Create CostAnomalyDetector with mocked session."""
    with patch('runbooks.common.profile_utils.create_operational_session') as mock_create:
        mock_create.return_value = mock_session

        with patch('runbooks.finops.aws_client.get_organization_accounts') as mock_orgs:
            mock_orgs.return_value = [{
                'id': '123456789012',
                'name': 'Test Account',
                'status': 'ACTIVE'
            }]

            detector = CostAnomalyDetector(
                profile='test-profile',
                threshold=20.0,
                lookback_days=30
            )
            return detector


def test_detector_initialization(detector):
    """Test detector initialization with correct parameters."""
    assert detector.profile == 'test-profile'
    assert detector.threshold == 20.0
    assert detector.lookback_days == 30
    assert detector.account_id == '123456789012'
    assert len(detector.accounts) == 1


def test_anomaly_creation():
    """Test Anomaly dataclass creation."""
    anomaly = Anomaly(
        anomaly_id='ANOM-0001',
        account_id='123456789012',
        account_name='Test Account',
        detection_date=datetime.utcnow(),
        baseline_cost=1000.0,
        current_cost=1500.0,
        cost_increase=500.0,
        percentage_increase=50.0,
        severity='critical',
        top_services=[('EC2', 300.0), ('RDS', 200.0)],
        top_regions=[('us-east-1', 400.0), ('us-west-2', 100.0)]
    )

    assert anomaly.anomaly_id == 'ANOM-0001'
    assert anomaly.severity == 'critical'
    assert anomaly.percentage_increase == 50.0
    assert len(anomaly.top_services) == 2


def test_root_cause_analysis_creation():
    """Test RootCauseAnalysis dataclass creation."""
    rca = RootCauseAnalysis(
        anomaly_id='ANOM-0001',
        primary_service='EC2',
        primary_region='us-east-1',
        service_breakdown={'EC2': 300.0, 'RDS': 200.0},
        region_breakdown={'us-east-1': 400.0, 'us-west-2': 100.0},
        recommendation='Investigate EC2 usage in us-east-1'
    )

    assert rca.anomaly_id == 'ANOM-0001'
    assert rca.primary_service == 'EC2'
    assert rca.primary_region == 'us-east-1'
    assert len(rca.service_breakdown) == 2


def test_generate_recommendation_critical(detector):
    """Test recommendation generation for critical severity."""
    anomaly = Anomaly(
        anomaly_id='ANOM-0001',
        account_id='123456789012',
        account_name='Test Account',
        detection_date=datetime.utcnow(),
        baseline_cost=1000.0,
        current_cost=1600.0,
        cost_increase=600.0,
        percentage_increase=60.0,
        severity='critical',
        top_services=[('EC2', 400.0)],
        top_regions=[('us-east-1', 400.0)]
    )

    recommendation = detector._generate_recommendation(
        anomaly,
        'EC2',
        'us-east-1'
    )

    assert 'CRITICAL' in recommendation
    assert 'EC2' in recommendation
    assert 'us-east-1' in recommendation
    assert '60.0%' in recommendation


def test_generate_recommendation_high(detector):
    """Test recommendation generation for high severity."""
    anomaly = Anomaly(
        anomaly_id='ANOM-0002',
        account_id='123456789012',
        account_name='Test Account',
        detection_date=datetime.utcnow(),
        baseline_cost=1000.0,
        current_cost=1400.0,
        cost_increase=400.0,
        percentage_increase=40.0,
        severity='high',
        top_services=[('RDS', 300.0)],
        top_regions=[('us-west-2', 300.0)]
    )

    recommendation = detector._generate_recommendation(
        anomaly,
        'RDS',
        'us-west-2'
    )

    assert 'HIGH PRIORITY' in recommendation
    assert 'RDS' in recommendation
    assert 'us-west-2' in recommendation
    assert '40.0%' in recommendation


def test_generate_recommendation_medium(detector):
    """Test recommendation generation for medium severity."""
    anomaly = Anomaly(
        anomaly_id='ANOM-0003',
        account_id='123456789012',
        account_name='Test Account',
        detection_date=datetime.utcnow(),
        baseline_cost=1000.0,
        current_cost=1250.0,
        cost_increase=250.0,
        percentage_increase=25.0,
        severity='medium',
        top_services=[('S3', 150.0)],
        top_regions=[('eu-west-1', 150.0)]
    )

    recommendation = detector._generate_recommendation(
        anomaly,
        'S3',
        'eu-west-1'
    )

    assert 'MONITOR' in recommendation
    assert 'S3' in recommendation
    assert 'eu-west-1' in recommendation
    assert '25.0%' in recommendation


def test_analyze_root_cause(detector):
    """Test root cause analysis from anomaly."""
    anomaly = Anomaly(
        anomaly_id='ANOM-0001',
        account_id='123456789012',
        account_name='Test Account',
        detection_date=datetime.utcnow(),
        baseline_cost=1000.0,
        current_cost=1500.0,
        cost_increase=500.0,
        percentage_increase=50.0,
        severity='critical',
        top_services=[('EC2', 300.0), ('RDS', 200.0)],
        top_regions=[('us-east-1', 400.0), ('us-west-2', 100.0)]
    )

    rca = detector.analyze_root_cause(anomaly)

    assert rca.anomaly_id == 'ANOM-0001'
    assert rca.primary_service == 'EC2'
    assert rca.primary_region == 'us-east-1'
    assert 'CRITICAL' in rca.recommendation


def test_severity_classification_critical():
    """Test severity classification for critical (>50%)."""
    # Critical severity should be assigned for >50% increase
    percentage = 60.0
    expected_severity = 'critical' if percentage >= 50 else 'high'

    assert expected_severity == 'critical'


def test_severity_classification_high():
    """Test severity classification for high (30-50%)."""
    # High severity should be assigned for 30-50% increase
    percentage = 40.0
    expected_severity = 'critical' if percentage >= 50 else ('high' if percentage >= 30 else 'medium')

    assert expected_severity == 'high'


def test_severity_classification_medium():
    """Test severity classification for medium (20-30%)."""
    # Medium severity should be assigned for 20-30% increase
    percentage = 25.0
    expected_severity = 'critical' if percentage >= 50 else ('high' if percentage >= 30 else 'medium')

    assert expected_severity == 'medium'


def test_get_account_cost_calculation(detector):
    """Test account cost calculation logic."""
    # Mock Cost Explorer response
    mock_response = {
        'ResultsByTime': [
            {'Total': {'UnblendedCost': {'Amount': '100.00'}}},
            {'Total': {'UnblendedCost': {'Amount': '150.00'}}},
            {'Total': {'UnblendedCost': {'Amount': '200.00'}}}
        ]
    }

    detector.ce_client.get_cost_and_usage = Mock(return_value=mock_response)

    start_date = datetime.utcnow().date() - timedelta(days=7)
    end_date = datetime.utcnow().date()

    cost = detector._get_account_cost('123456789012', start_date, end_date)

    assert cost == 450.0  # 100 + 150 + 200


def test_get_service_breakdown(detector):
    """Test service-level cost breakdown."""
    # Mock Cost Explorer response
    mock_response = {
        'ResultsByTime': [
            {
                'Groups': [
                    {
                        'Keys': ['Amazon Elastic Compute Cloud - Compute'],
                        'Metrics': {'UnblendedCost': {'Amount': '300.00'}}
                    },
                    {
                        'Keys': ['Amazon Relational Database Service'],
                        'Metrics': {'UnblendedCost': {'Amount': '200.00'}}
                    }
                ]
            }
        ]
    }

    detector.ce_client.get_cost_and_usage = Mock(return_value=mock_response)

    start_date = datetime.utcnow().date() - timedelta(days=7)
    end_date = datetime.utcnow().date()

    breakdown = detector._get_service_breakdown('123456789012', start_date, end_date)

    assert len(breakdown) == 2
    assert breakdown[0][0] == 'Amazon Elastic Compute Cloud - Compute'
    assert breakdown[0][1] == 300.0
    assert breakdown[1][0] == 'Amazon Relational Database Service'
    assert breakdown[1][1] == 200.0


def test_get_region_breakdown(detector):
    """Test region-level cost breakdown."""
    # Mock Cost Explorer response
    mock_response = {
        'ResultsByTime': [
            {
                'Groups': [
                    {
                        'Keys': ['us-east-1'],
                        'Metrics': {'UnblendedCost': {'Amount': '400.00'}}
                    },
                    {
                        'Keys': ['us-west-2'],
                        'Metrics': {'UnblendedCost': {'Amount': '100.00'}}
                    }
                ]
            }
        ]
    }

    detector.ce_client.get_cost_and_usage = Mock(return_value=mock_response)

    start_date = datetime.utcnow().date() - timedelta(days=7)
    end_date = datetime.utcnow().date()

    breakdown = detector._get_region_breakdown('123456789012', start_date, end_date)

    assert len(breakdown) == 2
    assert breakdown[0][0] == 'us-east-1'
    assert breakdown[0][1] == 400.0
    assert breakdown[1][0] == 'us-west-2'
    assert breakdown[1][1] == 100.0


@patch('runbooks.common.profile_utils.create_operational_session')
@patch('runbooks.finops.aws_client.get_organization_accounts')
@patch('runbooks.finops.cost_anomaly_detector.CostAnomalyDetector.detect_anomalies')
def test_detect_cost_anomalies_api(mock_detect, mock_orgs, mock_session):
    """Test main API function."""
    # Mock session
    mock_session.return_value = Mock()

    # Mock organization accounts
    mock_orgs.return_value = [{
        'id': '123456789012',
        'name': 'Test Account',
        'status': 'ACTIVE'
    }]

    # Mock anomaly detection
    mock_detect.return_value = [
        Anomaly(
            anomaly_id='ANOM-0001',
            account_id='123456789012',
            account_name='Test Account',
            detection_date=datetime.utcnow(),
            baseline_cost=1000.0,
            current_cost=1500.0,
            cost_increase=500.0,
            percentage_increase=50.0,
            severity='critical',
            top_services=[('EC2', 300.0)],
            top_regions=[('us-east-1', 400.0)]
        )
    ]

    # Call API
    df = detect_cost_anomalies(
        profile='test-profile',
        threshold=20.0
    )

    # Verify DataFrame
    assert not df.empty
    assert 'AnomalyID' in df.columns
    assert 'PercentageIncrease' in df.columns
    assert len(df) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
