/**
 * Dynamic Weight Configuration System for CFAT Assessment
 *
 * Replaces 30+ hardcoded weight values with flexible, environment-aware
 * configuration system supporting multiple compliance frameworks.
 *
 * Enterprise Features:
 * - Framework-specific weight profiles (AWS Well-Architected, SOC2, etc.)
 * - Environment-based weight adjustments (dev, staging, prod)
 * - Dynamic weight calculation based on organization size
 * - Override capabilities for specific requirements
 */
export var ComplianceFramework;
(function (ComplianceFramework) {
    ComplianceFramework["AWS_WELL_ARCHITECTED"] = "aws-well-architected";
    ComplianceFramework["SOC2"] = "soc2";
    ComplianceFramework["PCI_DSS"] = "pci-dss";
    ComplianceFramework["HIPAA"] = "hipaa";
    ComplianceFramework["NIST"] = "nist";
    ComplianceFramework["ISO_27001"] = "iso-27001";
    ComplianceFramework["CIS_BENCHMARKS"] = "cis";
    ComplianceFramework["CUSTOM"] = "custom";
})(ComplianceFramework || (ComplianceFramework = {}));
export var EnvironmentType;
(function (EnvironmentType) {
    EnvironmentType["DEVELOPMENT"] = "development";
    EnvironmentType["STAGING"] = "staging";
    EnvironmentType["PRODUCTION"] = "production";
    EnvironmentType["SANDBOX"] = "sandbox";
})(EnvironmentType || (EnvironmentType = {}));
export var OrganizationSize;
(function (OrganizationSize) {
    OrganizationSize["SMALL"] = "small";
    OrganizationSize["MEDIUM"] = "medium";
    OrganizationSize["LARGE"] = "large";
    OrganizationSize["ENTERPRISE"] = "enterprise"; // > 1000 accounts
})(OrganizationSize || (OrganizationSize = {}));
/**
 * Default weight configurations for different compliance frameworks
 */
export const FRAMEWORK_WEIGHTS = {
    [ComplianceFramework.AWS_WELL_ARCHITECTED]: {
        // Foundational requirements (Critical - Weight 6)
        organization_created: 6,
        management_account_created: 6,
        cloudtrail_created: 6,
        cloudtrail_org_service_enabled: 6,
        cloudtrail_org_trail_deployed: 6,
        config_recorder_management: 6,
        config_delivery_channel_management: 6,
        iam_idc_org_service_enabled: 6,
        iam_idc_configured: 6,
        scp_enabled: 6,
        tag_policy_enabled: 6,
        control_tower_deployed: 6,
        control_tower_not_drifted: 6,
        security_ou_deployed: 6,
        log_archive_account_deployed: 6,
        audit_account_deployed: 6,
        // Important but not critical (Weight 5)
        cloudformation_stacksets_activated: 5,
        cloudformation_org_service_enabled: 5,
        infrastructure_ou_deployed: 5,
        workloads_ou_deployed: 5,
        backup_policy_enabled: 5,
        control_tower_latest_version: 5,
        // Best practices (Weight 4)
        iam_users_removed: 4,
        ec2_instances_removed: 4,
        vpc_removed: 4,
        legacy_cur_setup: 4,
        guardduty_org_service_enabled: 4,
        ram_org_service_enabled: 4,
        securityhub_org_service_enabled: 4,
        iam_access_analyzer_org_service_enabled: 4,
        config_org_service_enabled: 4,
        backup_org_service_enabled: 4
    },
    [ComplianceFramework.SOC2]: {
        // SOC2 emphasizes security and availability (Higher security weights)
        organization_created: 6,
        management_account_created: 6,
        cloudtrail_created: 6,
        cloudtrail_org_service_enabled: 6,
        cloudtrail_org_trail_deployed: 6,
        config_recorder_management: 6,
        config_delivery_channel_management: 6,
        iam_idc_org_service_enabled: 6,
        iam_idc_configured: 6,
        scp_enabled: 6,
        tag_policy_enabled: 5,
        control_tower_deployed: 6,
        control_tower_not_drifted: 6,
        security_ou_deployed: 6,
        log_archive_account_deployed: 6,
        audit_account_deployed: 6,
        securityhub_org_service_enabled: 6, // Higher weight for SOC2
        iam_access_analyzer_org_service_enabled: 6, // Higher weight for SOC2
        // Enhanced security monitoring
        cloudformation_stacksets_activated: 5,
        cloudformation_org_service_enabled: 5,
        infrastructure_ou_deployed: 5,
        workloads_ou_deployed: 5,
        backup_policy_enabled: 6, // Higher for data protection
        control_tower_latest_version: 5,
        guardduty_org_service_enabled: 6, // Higher for threat detection
        // Management account hygiene (Important for SOC2)
        iam_users_removed: 5, // Higher weight for SOC2
        ec2_instances_removed: 5, // Higher weight for SOC2
        vpc_removed: 5, // Higher weight for SOC2
        legacy_cur_setup: 4,
        ram_org_service_enabled: 4,
        config_org_service_enabled: 5,
        backup_org_service_enabled: 6
    },
    [ComplianceFramework.PCI_DSS]: {
        // PCI-DSS focuses on data protection and network security
        organization_created: 6,
        management_account_created: 6,
        cloudtrail_created: 6,
        cloudtrail_org_service_enabled: 6,
        cloudtrail_org_trail_deployed: 6,
        config_recorder_management: 6,
        config_delivery_channel_management: 6,
        iam_idc_org_service_enabled: 6,
        iam_idc_configured: 6,
        scp_enabled: 6,
        tag_policy_enabled: 6,
        control_tower_deployed: 6,
        control_tower_not_drifted: 6,
        security_ou_deployed: 6,
        log_archive_account_deployed: 6,
        audit_account_deployed: 6,
        // Enhanced for PCI-DSS network and data requirements
        securityhub_org_service_enabled: 6,
        iam_access_analyzer_org_service_enabled: 6,
        guardduty_org_service_enabled: 6,
        backup_policy_enabled: 6,
        backup_org_service_enabled: 6,
        // Network isolation requirements
        iam_users_removed: 6, // Critical for PCI-DSS
        ec2_instances_removed: 6, // Critical for network isolation
        vpc_removed: 6, // Critical for network isolation
        cloudformation_stacksets_activated: 5,
        cloudformation_org_service_enabled: 5,
        infrastructure_ou_deployed: 5,
        workloads_ou_deployed: 5,
        control_tower_latest_version: 5,
        legacy_cur_setup: 4,
        ram_org_service_enabled: 4,
        config_org_service_enabled: 5
    },
    [ComplianceFramework.HIPAA]: {
        // HIPAA emphasizes data protection and audit trails
        organization_created: 6,
        management_account_created: 6,
        cloudtrail_created: 6,
        cloudtrail_org_service_enabled: 6,
        cloudtrail_org_trail_deployed: 6,
        config_recorder_management: 6,
        config_delivery_channel_management: 6,
        iam_idc_org_service_enabled: 6,
        iam_idc_configured: 6,
        scp_enabled: 6,
        tag_policy_enabled: 6,
        control_tower_deployed: 6,
        control_tower_not_drifted: 6,
        security_ou_deployed: 6,
        log_archive_account_deployed: 6,
        audit_account_deployed: 6,
        // Data protection and monitoring
        securityhub_org_service_enabled: 6,
        iam_access_analyzer_org_service_enabled: 6,
        backup_policy_enabled: 6,
        backup_org_service_enabled: 6,
        config_org_service_enabled: 6,
        // Audit and compliance
        cloudformation_stacksets_activated: 5,
        cloudformation_org_service_enabled: 5,
        infrastructure_ou_deployed: 5,
        workloads_ou_deployed: 5,
        control_tower_latest_version: 5,
        guardduty_org_service_enabled: 5,
        // Access controls
        iam_users_removed: 5,
        ec2_instances_removed: 4,
        vpc_removed: 4,
        legacy_cur_setup: 4,
        ram_org_service_enabled: 4
    },
    [ComplianceFramework.NIST]: {
        // NIST Cybersecurity Framework alignment
        organization_created: 6,
        management_account_created: 6,
        cloudtrail_created: 6,
        cloudtrail_org_service_enabled: 6,
        cloudtrail_org_trail_deployed: 6,
        config_recorder_management: 6,
        config_delivery_channel_management: 6,
        iam_idc_org_service_enabled: 6,
        iam_idc_configured: 6,
        scp_enabled: 6,
        tag_policy_enabled: 5,
        control_tower_deployed: 6,
        control_tower_not_drifted: 6,
        security_ou_deployed: 6,
        log_archive_account_deployed: 6,
        audit_account_deployed: 6,
        // Identify, Protect, Detect framework
        securityhub_org_service_enabled: 6,
        iam_access_analyzer_org_service_enabled: 6,
        guardduty_org_service_enabled: 6,
        backup_policy_enabled: 5,
        backup_org_service_enabled: 5,
        cloudformation_stacksets_activated: 5,
        cloudformation_org_service_enabled: 5,
        infrastructure_ou_deployed: 5,
        workloads_ou_deployed: 5,
        control_tower_latest_version: 5,
        config_org_service_enabled: 5,
        iam_users_removed: 4,
        ec2_instances_removed: 4,
        vpc_removed: 4,
        legacy_cur_setup: 4,
        ram_org_service_enabled: 4
    },
    [ComplianceFramework.ISO_27001]: {
        // ISO 27001 Information Security Management
        organization_created: 6,
        management_account_created: 6,
        cloudtrail_created: 6,
        cloudtrail_org_service_enabled: 6,
        cloudtrail_org_trail_deployed: 6,
        config_recorder_management: 6,
        config_delivery_channel_management: 6,
        iam_idc_org_service_enabled: 6,
        iam_idc_configured: 6,
        scp_enabled: 6,
        tag_policy_enabled: 6,
        control_tower_deployed: 6,
        control_tower_not_drifted: 6,
        security_ou_deployed: 6,
        log_archive_account_deployed: 6,
        audit_account_deployed: 6,
        // Information security controls
        securityhub_org_service_enabled: 6,
        iam_access_analyzer_org_service_enabled: 6,
        backup_policy_enabled: 6,
        backup_org_service_enabled: 6,
        config_org_service_enabled: 6,
        guardduty_org_service_enabled: 5,
        cloudformation_stacksets_activated: 5,
        cloudformation_org_service_enabled: 5,
        infrastructure_ou_deployed: 5,
        workloads_ou_deployed: 5,
        control_tower_latest_version: 5,
        iam_users_removed: 5,
        ec2_instances_removed: 4,
        vpc_removed: 4,
        legacy_cur_setup: 4,
        ram_org_service_enabled: 4
    },
    [ComplianceFramework.CIS_BENCHMARKS]: {
        // CIS Controls alignment
        organization_created: 6,
        management_account_created: 6,
        cloudtrail_created: 6,
        cloudtrail_org_service_enabled: 6,
        cloudtrail_org_trail_deployed: 6,
        config_recorder_management: 6,
        config_delivery_channel_management: 6,
        iam_idc_org_service_enabled: 6,
        iam_idc_configured: 6,
        scp_enabled: 6,
        tag_policy_enabled: 5,
        control_tower_deployed: 6,
        control_tower_not_drifted: 6,
        security_ou_deployed: 6,
        log_archive_account_deployed: 6,
        audit_account_deployed: 6,
        // CIS Controls emphasis
        securityhub_org_service_enabled: 6,
        iam_access_analyzer_org_service_enabled: 6,
        guardduty_org_service_enabled: 6,
        backup_policy_enabled: 5,
        backup_org_service_enabled: 5,
        config_org_service_enabled: 6,
        cloudformation_stacksets_activated: 5,
        cloudformation_org_service_enabled: 5,
        infrastructure_ou_deployed: 5,
        workloads_ou_deployed: 5,
        control_tower_latest_version: 5,
        // Asset and access management
        iam_users_removed: 5,
        ec2_instances_removed: 5,
        vpc_removed: 5,
        legacy_cur_setup: 4,
        ram_org_service_enabled: 4
    },
    [ComplianceFramework.CUSTOM]: {
        // Balanced default weights (original hardcoded values preserved)
        organization_created: 6,
        management_account_created: 6,
        iam_users_removed: 4,
        ec2_instances_removed: 4,
        vpc_removed: 4,
        legacy_cur_setup: 4,
        cloudtrail_created: 6,
        cloudtrail_org_service_enabled: 6,
        cloudtrail_org_trail_deployed: 6,
        config_recorder_management: 6,
        config_delivery_channel_management: 6,
        cloudformation_stacksets_activated: 5,
        guardduty_org_service_enabled: 4,
        ram_org_service_enabled: 4,
        securityhub_org_service_enabled: 4,
        iam_access_analyzer_org_service_enabled: 4,
        config_org_service_enabled: 4,
        cloudformation_org_service_enabled: 5,
        backup_org_service_enabled: 4,
        infrastructure_ou_deployed: 5,
        security_ou_deployed: 6,
        workloads_ou_deployed: 5,
        iam_idc_org_service_enabled: 6,
        iam_idc_configured: 6,
        scp_enabled: 6,
        tag_policy_enabled: 6,
        backup_policy_enabled: 5,
        control_tower_deployed: 6,
        control_tower_latest_version: 5,
        control_tower_not_drifted: 6,
        log_archive_account_deployed: 6,
        audit_account_deployed: 6
    }
};
/**
 * Environment-based weight modifiers
 */
export const ENVIRONMENT_MODIFIERS = {
    [EnvironmentType.DEVELOPMENT]: 0.8, // 20% reduction for dev environments
    [EnvironmentType.STAGING]: 0.9, // 10% reduction for staging
    [EnvironmentType.PRODUCTION]: 1.0, // Full weight for production
    [EnvironmentType.SANDBOX]: 0.6 // 40% reduction for sandbox
};
/**
 * Organization size-based weight adjustments
 */
export const SIZE_MODIFIERS = {
    [OrganizationSize.SMALL]: {
        // Small orgs might not need all enterprise features
        infrastructure_ou_deployed: -1,
        workloads_ou_deployed: -1,
        backup_policy_enabled: -1
    },
    [OrganizationSize.MEDIUM]: {
    // Medium orgs benefit from all features
    },
    [OrganizationSize.LARGE]: {
        // Large orgs need enhanced governance
        scp_enabled: +1,
        tag_policy_enabled: +1,
        backup_policy_enabled: +1
    },
    [OrganizationSize.ENTERPRISE]: {
        // Enterprise requires maximum governance
        scp_enabled: +1,
        tag_policy_enabled: +1,
        backup_policy_enabled: +1,
        control_tower_deployed: +1,
        security_ou_deployed: +1
    }
};
/**
 * Get dynamic weight configuration based on environment context
 */
export function getWeightConfig(framework = ComplianceFramework.AWS_WELL_ARCHITECTED, environment = EnvironmentType.PRODUCTION, orgSize = OrganizationSize.MEDIUM, customOverrides = {}) {
    // Start with framework-specific weights
    const baseWeights = { ...FRAMEWORK_WEIGHTS[framework] };
    // Apply environment modifier
    const envModifier = ENVIRONMENT_MODIFIERS[environment];
    // Apply size-based adjustments
    const sizeAdjustments = SIZE_MODIFIERS[orgSize] || {};
    // Calculate final weights
    const finalWeights = { ...baseWeights };
    // Apply environment modifier (multiply by modifier, round to nearest integer)
    Object.keys(finalWeights).forEach(key => {
        const typedKey = key;
        finalWeights[typedKey] = Math.round(baseWeights[typedKey] * envModifier);
    });
    // Apply size adjustments (add/subtract values)
    Object.keys(sizeAdjustments).forEach(key => {
        const typedKey = key;
        if (finalWeights[typedKey] !== undefined && sizeAdjustments[typedKey] !== undefined) {
            finalWeights[typedKey] = Math.max(1, finalWeights[typedKey] + sizeAdjustments[typedKey]);
        }
    });
    // Apply custom overrides
    Object.keys(customOverrides).forEach(key => {
        const typedKey = key;
        if (customOverrides[typedKey] !== undefined) {
            finalWeights[typedKey] = customOverrides[typedKey];
        }
    });
    return finalWeights;
}
/**
 * Validate weight configuration values
 */
export function validateWeightConfig(config) {
    const errors = [];
    Object.entries(config).forEach(([key, value]) => {
        if (typeof value !== 'number') {
            errors.push(`Weight for ${key} must be a number, got ${typeof value}`);
        }
        else if (value < 1 || value > 10) {
            errors.push(`Weight for ${key} must be between 1 and 10, got ${value}`);
        }
        else if (!Number.isInteger(value)) {
            errors.push(`Weight for ${key} must be an integer, got ${value}`);
        }
    });
    return {
        valid: errors.length === 0,
        errors
    };
}
/**
 * Load weight configuration from environment variables or defaults
 */
export function loadWeightConfigFromEnv() {
    // Load from environment variables with sensible defaults
    const framework = process.env.CFAT_COMPLIANCE_FRAMEWORK
        || ComplianceFramework.AWS_WELL_ARCHITECTED;
    const environment = process.env.CFAT_ENVIRONMENT_TYPE
        || EnvironmentType.PRODUCTION;
    const orgSize = process.env.CFAT_ORG_SIZE
        || OrganizationSize.MEDIUM;
    // Load custom overrides from environment (JSON format)
    let customOverrides = {};
    const customOverridesEnv = process.env.CFAT_WEIGHT_OVERRIDES;
    if (customOverridesEnv) {
        try {
            customOverrides = JSON.parse(customOverridesEnv);
        }
        catch (error) {
            console.warn('Invalid JSON in CFAT_WEIGHT_OVERRIDES, using defaults:', error);
        }
    }
    return {
        framework,
        environment,
        orgSize,
        customOverrides
    };
}
/**
 * Export default configuration for easy importing
 */
export function getDefaultWeightConfig() {
    const envConfig = loadWeightConfigFromEnv();
    return getWeightConfig(envConfig.framework, envConfig.environment, envConfig.orgSize, envConfig.customOverrides);
}
