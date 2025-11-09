"""
AWS Lightsail Mini Infrastructure Stack
======================================

This module provides a comprehensive AWS Lightsail infrastructure deployment stack
using CDKTF (Cloud Development Kit for Terraform) with Python.

The stack includes:
    * Lightsail Container Service with automatic custom domain attachment
    * PostgreSQL Database (optional)
    * DNS management with CNAME records
    * SSL certificate management with automatic validation
    * IAM resources for service access
    * S3 bucket for application data
    * Secrets Manager for credential storage

:author: Generated with GitHub Copilot
:version: 1.0.0
:license: MIT
"""


#region specific imports

import os
import json
from enum import Enum
from constructs import Construct
from cdktf import TerraformOutput

# Import the base class
from .LightsailBase import LightsailBase, BaseLightsailArchitectureFlags

#endregion

#region AWS Provider and Resources
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws import (
    lightsail_container_service,
    lightsail_database,
    cloudfront_distribution,
    s3_bucket,
)
#endregion

#region Random Provider and Resources
from cdktf_cdktf_provider_random import password

# AWS WAF (currently unused but imported for future use)
from cdktf_cdktf_provider_aws.wafv2_web_acl import (
    Wafv2WebAcl,
    Wafv2WebAclDefaultAction,
    Wafv2WebAclRule,
    Wafv2WebAclVisibilityConfig,
    Wafv2WebAclDefaultActionAllow,
    Wafv2WebAclRuleOverrideAction,
    Wafv2WebAclRuleOverrideActionNone,
    Wafv2WebAclRuleOverrideActionCount,
    Wafv2WebAclRuleVisibilityConfig,
)
from cdktf_cdktf_provider_aws.wafv2_web_acl_association import Wafv2WebAclAssociation
from cdktf_cdktf_provider_aws.wafv2_rule_group import Wafv2RuleGroupRuleVisibilityConfig

#endregion



#region ArchitectureFlags 
class ArchitectureFlags(Enum):
    """
    Architecture configuration flags for optional components.

    Includes both base flags and container-specific flags.

    Base flags:
    :param SKIP_DEFAULT_POST_APPLY_SCRIPTS: Skip default post-apply scripts
    :param PRESERVE_EXISTING_SECRETS: Don't overwrite existing secret versions (smart detection)
    :param IGNORE_SECRET_CHANGES: Ignore all changes to secret after initial creation
    
    Container-specific flags:
    :param SKIP_DATABASE: Skip database creation
    :param SKIP_DOMAIN: Skip domain and DNS configuration
    """
    
    # Base flags from BaseLightsailArchitectureFlags
    SKIP_DEFAULT_POST_APPLY_SCRIPTS = "skip_default_post_apply_scripts"
    PRESERVE_EXISTING_SECRETS = "preserve_existing_secrets"
    IGNORE_SECRET_CHANGES = "ignore_secret_changes"
    
    # Container-specific flags
    SKIP_DATABASE = "skip_database"
    SKIP_DOMAIN = "skip_domain"

#endregion


class LightsailContainerStack(LightsailBase):
    """
    AWS Lightsail Mini Infrastructure Stack.

    A comprehensive infrastructure stack that deploys:
        * Lightsail Container Service with custom domain support
        * PostgreSQL database (optional)
        * IAM resources and S3 storage

    :param scope: The construct scope
    :param id: The construct ID
    :param kwargs: Configuration parameters including region, domains, flags, etc.

    Example:
        >>> stack = LightsailContainerStack(
        ...     app, "my-stack",
        ...     region="ca-central-1",
        ...     domains=["app.example.com"],
        ...     project_name="my-app",
        ...     postApplyScripts=[
        ...         "echo 'Deployment completed'",
        ...         "curl -X POST https://webhook.example.com/notify"
        ...     ]
        ... )
    """

    @staticmethod
    def get_architecture_flags():
        """
        Get the ArchitectureFlags enum for configuration.

        :returns: ArchitectureFlags enum class
        :rtype: type[ArchitectureFlags]
        """
        return ArchitectureFlags

    def __init__(self, scope, id, **kwargs):
        """
        Initialize the AWS Lightsail Mini Infrastructure Stack.

        :param scope: The construct scope
        :param id: Unique identifier for this stack
        :param kwargs: Configuration parameters

        **Configuration Parameters:**

        :param region: AWS region (default: "us-east-1")
        :param environment: Environment name (default: "dev")
        :param project_name: Project identifier (default: "bb-aws-lightsail-mini-v1a-app")
        :param domain_name: Primary domain name
        :param domains: List of custom domains to configure
        :param flags: List of ArchitectureFlags to modify behavior
        :param profile: AWS profile to use (default: "default")
        :param postApplyScripts: List of shell commands to execute after deployment

        .. warning::
           Lightsail domain operations must use us-east-1 region regardless of
           the main stack region.
        """
        # Set container-specific defaults
        if "project_name" not in kwargs:
            kwargs["project_name"] = "bb-aws-lightsail-mini-v1a-app"
        
        # Call parent constructor which handles all the base initialization
        super().__init__(scope, id, **kwargs)

        # ===== Container-Specific Configuration =====
        self.domains = kwargs.get("domains", []) or []

        # ===== Database Configuration =====
        self.default_db_name = kwargs.get("default_db_name", self.project_name)
        self.default_db_username = kwargs.get("default_db_username", "dbadmin")

    def _initialize_providers(self):
        """Initialize all required Terraform providers."""
        # Call parent class to initialize base providers
        super()._initialize_providers()
        
        # Add Lightsail-specific provider for domain operations (must be us-east-1)
        self.aws_domain_provider = AwsProvider(
            self, "aws_domain", region="us-east-1", profile=self.profile, alias="domain"
        )
        self.resources["aws_domain"] = self.aws_domain_provider

    def _set_default_post_apply_scripts(self):
        """
        Set default post-apply scripts specific to container deployments.
        """
        # Call parent method for base scripts
        super()._set_default_post_apply_scripts()

        # Skip if flag is set
        if BaseLightsailArchitectureFlags.SKIP_DEFAULT_POST_APPLY_SCRIPTS.value in self.flags:
            return

        # Add container-specific scripts
        container_scripts = [
            f"echo '🚀 Container Service URL: https://{self.project_name}.{self.region}.cs.amazonlightsail.com'",
        ]

        # Insert container-specific scripts before the final "execution started" message
        if self.post_apply_scripts:
            # Find the index of the last script and insert before it
            insert_index = len(self.post_apply_scripts) - 1
            for script in reversed(container_scripts):
                self.post_apply_scripts.insert(insert_index, script)

    def create_lightsail_resources(self):
        """
        Create core Lightsail resources.

        Creates:
            * Lightsail Container Service with nano power and scale of 1
            * Random password for database authentication (if database not skipped)

        .. note::
           Custom domains are configured separately through DNS records and
           post-deployment automation rather than the public_domain_names parameter
           due to CDKTF type complexity.
        """
        # Lightsail Container Service
        self.container_service = lightsail_container_service.LightsailContainerService(
            self,
            "app_container",
            name=f"{self.project_name}",
            power="nano",
            region=self.region,
            scale=1,
            is_disabled=False,
            # Note: Custom domains are configured separately via DNS records
            # The public_domain_names parameter has complex type requirements
            tags={"Environment": self.environment, "Project": self.project_name, "Stack": self.__class__.__name__},
        )
        self.container_service_url = self.get_lightsail_container_service_domain()

        # Create Lightsail database if not skipped
        if not self.has_flag(ArchitectureFlags.SKIP_DATABASE.value):
            self.create_lightsail_database()

        # Create S3 bucket for application data
        self.create_s3_bucket()

        self.resources["lightsail_container_service"] = self.container_service

    def create_lightsail_database(self):
        """
        Create Lightsail PostgreSQL database (optional).

        Creates a micro PostgreSQL 14 database instance if the SKIP_DATABASE flag
        is not set. Also populates the secrets dictionary with database connection
        information for use in Secrets Manager.

        Database Configuration:
            * Engine: PostgreSQL 14
            * Size: micro_2_0
            * Final snapshot: Disabled (skip_final_snapshot=True)

        .. note::
           Database creation can be skipped by including ArchitectureFlags.SKIP_DATABASE
           in the flags parameter during stack initialization.
        """
        # Database Password Generation
        self.db_password = password.Password(
            self, "db_password", length=16, special=True, override_special="!#$%&*()-_=+[]{}<>:?"
        )

        self.database = lightsail_database.LightsailDatabase(
            self,
            "app_database",
            relational_database_name=f"{self.project_name}-db",
            blueprint_id="postgres_14",
            bundle_id="micro_2_0",
            master_database_name=self.clean_hyphens(f"{self.project_name}"),
            master_username=self.default_db_username,
            master_password=self.db_password.result,
            skip_final_snapshot=True,
            tags={"Environment": self.environment, "Project": self.project_name, "Stack": self.__class__.__name__},
        )

        # Populate secrets for database connection
        self.secrets.update(
            {
                "password": self.db_password.result,
                "username": self.default_db_username,
                "dbname": self.default_db_name,
                "host": self.database.master_endpoint_address,
                "port": self.database.master_endpoint_port,
            }
        )

    def create_s3_bucket(self, bucket_name=None):
        """
        Create S3 bucket for application data storage.

        Creates a private S3 bucket with proper tagging for application data storage
        and security configurations:
        - Bucket versioning enabled
        - Server-side encryption with Amazon S3 managed keys (SSE-S3)
        - Bucket key enabled to reduce encryption costs
        - Private ACL

        The bucket name follows the pattern: {project_name}-s3

        .. note::
           The ACL parameter is deprecated in favor of aws_s3_bucket_acl resource
           but is retained for backwards compatibility.
        """
        if bucket_name is None:
            bucket_name = self.properize_s3_bucketname(f"{self.project_name}-s3")

        self.s3_bucket = s3_bucket.S3Bucket(
            self,
            "app_data_bucket",
            bucket=bucket_name,
            acl="private",
            versioning={"enabled": True},
            server_side_encryption_configuration=({
                "rule": ({
                    "apply_server_side_encryption_by_default": {
                        "sse_algorithm": "AES256"
                    },
                    "bucket_key_enabled": True
                })
            }),
            tags={"Environment": self.environment, "Project": self.project_name, "Stack": self.__class__.__name__},
        )

        # Store the S3 bucket in resources registry
        self.resources["s3_bucket"] = self.s3_bucket
        self.bucket_name = bucket_name

    def get_lightsail_container_service_domain(self):
        """
        Retrieve the actual Lightsail container service domain from AWS.

        Returns a default format domain since we cannot query AWS at synthesis time.

        :returns: The public domain URL for the container service
        :rtype: str
        """
        return f"{self.project_name}.{self.region}.cs.amazonlightsail.com"

    def create_outputs(self):
        """
        Create Terraform outputs for important resource information.

        Generates outputs for:
            * Container service public URL
            * Database endpoint (if database is enabled)
            * Database password (sensitive, if database is enabled)
            * IAM access keys (sensitive)

        .. note::
           Sensitive outputs are marked as such and will be hidden in
           Terraform output unless explicitly requested.
        """
        # Container service public URL
        TerraformOutput(
            self,
            "container_service_url",
            value=self.container_service_url,
            description="Public URL of the Lightsail container service",
        )

        # Database outputs (if database is enabled)
        if not self.has_flag(ArchitectureFlags.SKIP_DATABASE.value) and hasattr(self, 'database'):
            TerraformOutput(
                self,
                "database_endpoint",
                value=f"{self.database.master_endpoint_address}:{self.database.master_endpoint_port}",
                description="Database connection endpoint",
            )
            TerraformOutput(
                self,
                "database_password",
                value=self.database.master_password,
                sensitive=True,
                description="Database master password (sensitive)",
            )

        # Use the shared IAM output helper
        self.create_iam_outputs()

        """Placeholder for networking resources creation."""
        pass