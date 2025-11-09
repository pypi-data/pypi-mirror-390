"""
AWS Lightsail Base Infrastructure Stack
======================================

This module provides an abstract base class for AWS Lightsail infrastructure deployment stacks
using CDKTF (Cloud Development Kit for Terraform) with Python.

The abstract base class includes:
    * Common IAM resources for service access
    * AWS Secrets Manager for credential storage
    * Shared configuration and initialization patterns
    * Common utility methods and secret management strategies
    * Template methods for infrastructure creation workflow

This class should be extended by specific Lightsail implementations such as:
    * LightsailContainerStack - For container services
    * LightsailDatabaseStack - For database instances

:author: Generated with GitHub Copilot
:version: 1.0.0
:license: MIT
"""

#region specific imports

import os
import json
from abc import ABC, abstractmethod
from enum import Enum
from constructs import Construct
from cdktf import TerraformOutput

# Import from the correct base architecture package
import sys
sys.path.append('/Repos/AWSArchitectureBase')
from AWSArchitectureBase.AWSArchitectureBaseStack.AWSArchitectureBase import AWSArchitectureBase

#endregion

#region AWS Provider and Resources
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws import (
    iam_user,
    iam_access_key,
    iam_user_policy,
)
#endregion

#region Random Provider and Resources
from cdktf_cdktf_provider_random import password

# AWS Secrets Manager
from cdktf_cdktf_provider_aws.secretsmanager_secret import SecretsmanagerSecret
from cdktf_cdktf_provider_aws.secretsmanager_secret_version import SecretsmanagerSecretVersion
from cdktf_cdktf_provider_aws.data_aws_secretsmanager_secret_version import DataAwsSecretsmanagerSecretVersion

# Null Provider for local-exec provisioner
from cdktf_cdktf_provider_null.resource import Resource as NullResource

#endregion

#region Base ArchitectureFlags 
class BaseLightsailArchitectureFlags(Enum):
    """
    Base architecture configuration flags for optional components.
    
    These flags are common to all Lightsail implementations and can be
    extended by specific implementations with additional flags.

    :param SKIP_DEFAULT_POST_APPLY_SCRIPTS: Skip default post-apply scripts
    :param PRESERVE_EXISTING_SECRETS: Don't overwrite existing secret versions (smart detection)
    :param IGNORE_SECRET_CHANGES: Ignore all changes to secret after initial creation
    """

    SKIP_DEFAULT_POST_APPLY_SCRIPTS = "skip_default_post_apply_scripts"
    PRESERVE_EXISTING_SECRETS = "preserve_existing_secrets"
    IGNORE_SECRET_CHANGES = "ignore_secret_changes"

#endregion


class LightsailBase(AWSArchitectureBase):
    """
    Abstract base class for AWS Lightsail Infrastructure Stacks.

    This abstract class provides common functionality for Lightsail-based
    infrastructure deployments including:
        * IAM resources for service access
        * AWS Secrets Manager for credential storage
        * Common configuration patterns and initialization
        * Shared utility methods and helper functions
        * Template methods for infrastructure creation workflow

    Subclasses must implement abstract methods to define their specific
    infrastructure components while leveraging the shared functionality.

    :param scope: The construct scope
    :param id: The construct ID
    :param kwargs: Configuration parameters

    **Common Configuration Parameters:**

    :param region: AWS region (default: "us-east-1")
    :param environment: Environment name (default: "dev")
    :param project_name: Project identifier (required)
    :param flags: List of ArchitectureFlags to modify behavior
    :param profile: AWS profile to use (default: "default")
    :param postApplyScripts: List of shell commands to execute after deployment
    :param secret_name: Custom secret name (default: "{project_name}/{environment}/credentials")
    :param default_signature_version: AWS signature version (default: "s3v4")
    :param default_extra_secret_env: Environment variable for additional secrets (default: "SECRET_STRING")

    Example:
        >>> class MyLightsailStack(LightsailBase):
        ...     def create_lightsail_resources(self):
        ...         # Implement specific Lightsail resources
        ...         pass
        ...     
        ...     def get_architecture_flags(self):
        ...         return MyArchitectureFlags
    """

    # Class-level resource registry
    resources = {}

    # Default post-apply scripts executed after deployment
    default_post_apply_scripts = []

    def get_architecture_flags(self):
        """
        Get the ArchitectureFlags enum for configuration.

        :returns: ArchitectureFlags enum class
        :rtype: type[ArchitectureFlags]
        """
        super_flags = super.get_architecture_flags()
        this_flags = ArchitectureFlags
        for flag in super_flags:
            this_flags[flag.name] = flag.value

        return this_flags

    def __init__(self, scope, id, **kwargs):
        """
        Initialize the AWS Lightsail Base Infrastructure Stack.

        :param scope: The construct scope
        :param id: Unique identifier for this stack
        :param kwargs: Configuration parameters
        """
        # Initialize configuration before parent class to ensure proper state bucket setup
        self.region = kwargs.get("region", "us-east-1")
        self.environment = kwargs.get("environment", "dev")
        self.project_name = kwargs.get("project_name")
        self.profile = kwargs.get("profile", "default")
        
        if not self.project_name:
            raise ValueError("project_name is required and cannot be empty")
        
        # Ensure we pass all kwargs to parent class
        super().__init__(scope, id, **kwargs)

        # ===== Stack Configuration =====
        self.flags = kwargs.get("flags", [])
        self.post_apply_scripts = kwargs.get("postApplyScripts", []) or []

        # ===== Security Configuration =====
        default_secret_name = f"{self.project_name}/{self.environment}/credentials"
        self.secret_name = kwargs.get("secret_name", default_secret_name)
        self.default_signature_version = kwargs.get("default_signature_version", "s3v4")
        self.default_extra_secret_env = kwargs.get("default_extra_secret_env", "SECRET_STRING")

        # ===== Storage Configuration =====
        default_bucket_name = self.properize_s3_bucketname(f"{self.region}-{self.project_name}-tfstate")
        self.state_bucket_name = kwargs.get("state_bucket_name", default_bucket_name)

        # ===== Internal State =====
        self.secrets = {}
        self.post_terraform_messages = []
        self._post_plan_guidance: list[str] = []

        # ===== Infrastructure Setup =====
        # Base infrastructure is already set up by parent class
        # Initialize our specific components using template method pattern
        self._set_default_post_apply_scripts()
        self._create_infrastructure_components()

    def _initialize_providers(self):
        """
        Initialize all required Terraform providers.
        
        Calls the parent class to initialize base providers and can be
        extended by subclasses to add additional provider configurations.
        """
        # Call parent class to initialize base providers (AWS, Random, Null)
        super()._initialize_providers()

    def _set_default_post_apply_scripts(self):
        """
        Set default post-apply scripts and merge with user-provided scripts.

        This method configures the default post-apply scripts that provide
        deployment status information and basic verification. These scripts
        are automatically added to the post_apply_scripts list unless the
        SKIP_DEFAULT_POST_APPLY_SCRIPTS flag is set.

        Subclasses can override this method to provide their own default scripts
        while optionally calling the parent method.

        **Default Scripts Include:**

        * Deployment completion notification
        * Infrastructure summary information
        * Environment and project details
        * Basic system information

        **Script Merging:**

        * Default scripts are prepended to user-provided scripts
        * User scripts execute after default scripts
        * Duplicates are not automatically removed

        .. note::
           Default scripts can be skipped by including the SKIP_DEFAULT_POST_APPLY_SCRIPTS
           flag in the flags parameter during stack initialization.

        .. warning::
           Default scripts use environment variables and command substitution.
           Ensure the execution environment supports bash-style commands.
        """
        # Define base default post-apply scripts
        self.default_post_apply_scripts = [
            "echo '============================================='",
            "echo '🎉 AWS Lightsail Infrastructure Deployment Complete!'",
            "echo '============================================='",
            f"echo '📦 Project: {self.project_name}'",
            f"echo '🌍 Environment: {self.environment}'",
            f"echo '📍 Region: {self.region}'",
            "echo '⏰ Deployment Time: '$(date)",
            "echo '============================================='",
            "echo '💻 System Information:'",
            "echo '   - OS: '$(uname -s)",
            "echo '   - Architecture: '$(uname -m)",
            "echo '   - User: '$(whoami)",
            "echo '   - Working Directory: '$(pwd)",
            "echo '============================================='",
            "echo '✅ Post-deployment scripts execution started'",
        ]

        # Skip default scripts if flag is set
        if BaseLightsailArchitectureFlags.SKIP_DEFAULT_POST_APPLY_SCRIPTS.value in self.flags:
            return

        # Merge default scripts with user-provided scripts
        # Default scripts execute first, then user scripts
        self.post_apply_scripts = self.default_post_apply_scripts + self.post_apply_scripts

    def _create_infrastructure_components(self):
        """
        Template method for creating all infrastructure components in the correct order.
        
        This method defines the overall workflow for infrastructure creation
        and calls abstract methods that must be implemented by subclasses.
        The order of operations is:
        
        1. Create IAM resources (concrete implementation provided)
        2. Create Lightsail-specific resources (abstract - implemented by subclasses)
        3. Create security resources (concrete implementation provided)
        4. Execute post-apply scripts (concrete implementation provided)
        5. Create outputs (abstract - implemented by subclasses)
        """
        # Core infrastructure - provided by base class
        self.create_iam_resources()
        
        # Lightsail-specific resources - implemented by subclasses
        self.create_lightsail_resources()
        
        # Security and storage - provided by base class
        self.create_security_resources()

        # Post-apply scripts - provided by base class
        self.execute_post_apply_scripts()

        # Output generation - implemented by subclasses
        self.create_outputs()

    # ==================== ABSTRACT METHODS ====================

    @abstractmethod
    def create_lightsail_resources(self):
        """
        Create Lightsail-specific resources.
        
        This method must be implemented by subclasses to create their
        specific Lightsail resources such as:
        * Container services
        * Database instances
        * Storage volumes
        * Networking components
        
        The method should populate the self.secrets dictionary with
        any credentials or connection information that should be stored
        in AWS Secrets Manager.
        """
        pass

    @abstractmethod
    def create_outputs(self):
        """
        Create Terraform outputs for important resource information.
        
        This method must be implemented by subclasses to create
        appropriate Terraform outputs for their specific resources.
        
        Common patterns include:
        * Resource endpoints and URLs
        * Connection information
        * Sensitive credentials (marked as sensitive=True)
        * Resource identifiers and names
        """
        pass

    # ==================== CONCRETE SHARED METHODS ====================

    def create_iam_resources(self):
        """
        Create IAM resources for service access.

        Creates:
            * IAM user for programmatic access to AWS services
            * Access key pair for the IAM user
            * IAM policy loaded from external JSON file (if exists)

        The IAM user follows the naming pattern: {project_name}-service-user
        """
        # Create IAM User and Access Key 
        user_name = f"{self.project_name}-service-user"
        self.service_user = iam_user.IamUser(
            self, "service_user", name=user_name
        )

        # Create IAM Access Key
        self.service_key = iam_access_key.IamAccessKey(
            self, "service_key", user=self.service_user.name
        )

        # IAM Policy from external file (optional)
        try:
            self.service_policy = self.create_iam_policy_from_file()
            self.resources["iam_policy"] = self.service_policy
        except FileNotFoundError:
            # Policy file doesn't exist, skip policy creation
            pass

    def create_iam_policy_from_file(self, file_path="iam_policy.json"):
        """
        Create IAM policy from JSON file.

        :param file_path: Path to IAM policy JSON file relative to this module
        :type file_path: str
        :returns: IAM user policy resource
        :rtype: IamUserPolicy
        :raises FileNotFoundError: If policy file doesn't exist

        .. note::
           The policy file should be located in the same directory as this module.
        """
        file_to_open = os.path.join(os.path.dirname(__file__), file_path)

        with open(file_to_open, "r") as f:
            policy = f.read()

        return iam_user_policy.IamUserPolicy(
            self,
            f"{self.project_name}-{self.environment}-service-policy",
            name=f"{self.project_name}-{self.environment}-service-policy",
            user=self.service_user.name,
            policy=policy,
        )

    def get_extra_secret_env(self, env_var_name=None):
        """
        Load additional secrets from environment variable.

        Attempts to load and parse a JSON string from the environment variable
        specified in default_extra_secret_env. Any valid JSON key-value pairs
        are added to the secrets dictionary if they don't already exist.

        :param env_var_name: Environment variable name to load secrets from
        :raises: No exceptions - silently continues if JSON parsing fails
        """
        if env_var_name is None:
            env_var_name = self.default_extra_secret_env
            
        extra_secret_env = os.environ.get(env_var_name, None)

        if extra_secret_env:
            try:
                extra_secret_json = json.loads(extra_secret_env)
                for key, value in extra_secret_json.items():
                    if key not in self.secrets:
                        self.secrets[key] = value
            except json.JSONDecodeError:
                # Silently continue if JSON parsing fails
                pass

    def create_security_resources(self):
        """
        Create AWS Secrets Manager resources for credential storage.

        Creates:
            * Secrets Manager secret for storing application credentials
            * Secret version with JSON-formatted credential data (conditionally)

        **Secret Management Strategy:**

        If PRESERVE_EXISTING_SECRETS flag is set:
        - Checks if secret already exists with content
        - Only creates new version if secret is empty or doesn't exist
        - Preserves manual secret updates and rotations

        **Stored Credentials:**

        * IAM access keys for service authentication
        * AWS region and signature version configuration
        * Any additional secrets from environment variables
        * Subclass-specific credentials (added by create_lightsail_resources)

        .. note::
           All secrets are stored as a single JSON document in Secrets Manager
           for easy retrieval by applications.
        """
        # Create Secrets Manager secret
        self.secrets_manager_secret = SecretsmanagerSecret(self, self.secret_name, name=f"{self.secret_name}")
        self.resources["secretsmanager_secret"] = self.secrets_manager_secret

        # Populate IAM and AWS configuration secrets
        self.secrets.update({
            "service_user_access_key": self.service_key.id,
            "service_user_secret_key": self.service_key.secret,
            "access_key": self.service_key.id,
            "secret_access_key": self.service_key.secret,
            "region_name": self.region,
            "signature_version": self.default_signature_version
        })

        # Load additional secrets from environment
        self.get_extra_secret_env()

        # Conditional secret version creation
        if self.has_flag(BaseLightsailArchitectureFlags.PRESERVE_EXISTING_SECRETS.value):
            self._create_secret_version_conditionally()
        elif self.has_flag(BaseLightsailArchitectureFlags.IGNORE_SECRET_CHANGES.value):
            self._create_secret_version_with_lifecycle_ignore()
        else:
            # Create secret version with all credentials (original behavior)
            SecretsmanagerSecretVersion(
                self,
                self.secret_name + "_version",
                secret_id=self.secrets_manager_secret.id,
                secret_string=(json.dumps(self.secrets, indent=2, sort_keys=True) if self.secrets else None),
            )

    def _create_secret_version_conditionally(self):
        """
        Create secret version only if one doesn't already exist or is empty.
        
        This method implements smart secret management:
        1. Attempts to read existing secret using data source
        2. Only creates new version if secret is empty or doesn't exist
        3. Preserves manual updates and rotations made outside Terraform
        
        **Use Cases:**
        - Initial deployment when no secret exists
        - Secret exists but has no content (empty)
        - Avoid overwriting manually rotated credentials
        - Preserve additional keys added through AWS console/CLI
        """
        try:
            # Try to read existing secret version to check if it has content
            existing_secret = DataAwsSecretsmanagerSecretVersion(
                self,
                self.secret_name + "_existing_check",
                secret_id=self.secrets_manager_secret.id,
                version_stage="AWSCURRENT"
            )
            
            # Create a conditional secret version
            conditional_secret = SecretsmanagerSecretVersion(
                self,
                self.secret_name + "_version_conditional",
                secret_id=self.secrets_manager_secret.id,
                secret_string=json.dumps(self.secrets, indent=2, sort_keys=True) if self.secrets else None,
                lifecycle={
                    "ignore_changes": ["secret_string"],
                    "create_before_destroy": False
                }
            )
            
            # Add dependency to ensure secret exists before checking
            conditional_secret.add_override("count", 
                "${length(try(jsondecode(data.aws_secretsmanager_secret_version." + 
                self.secret_name.replace("/", "_").replace("-", "_") + "_existing_check.secret_string), {})) == 0 ? 1 : 0}"
            )
            
        except Exception:
            # If data source fails (secret doesn't exist), create the version
            SecretsmanagerSecretVersion(
                self,
                self.secret_name + "_version_fallback",
                secret_id=self.secrets_manager_secret.id,
                secret_string=json.dumps(self.secrets, indent=2, sort_keys=True) if self.secrets else None,
            )

    def _create_secret_version_with_lifecycle_ignore(self):
        """
        Create secret version with lifecycle rule to ignore future changes.
        
        This is a simpler approach that:
        1. Creates the secret version with initial values on first deployment
        2. Ignores all future changes to the secret_string
        3. Allows manual updates in AWS console/CLI to persist
        
        **Pros:**
        - Simple implementation
        - Reliable behavior
        - Preserves manual changes after initial creation
        
        **Cons:**
        - Cannot update secrets through Terraform after initial deployment
        - Requires manual secret management for infrastructure changes
        """
        secret_version = SecretsmanagerSecretVersion(
            self,
            self.secret_name + "_version_ignored",
            secret_id=self.secrets_manager_secret.id,
            secret_string=json.dumps(self.secrets, indent=2, sort_keys=True) if self.secrets else None,
        )
        
        # Add lifecycle rule to ignore changes to secret_string
        secret_version.add_override("lifecycle", {
            "ignore_changes": ["secret_string"]
        })

    def execute_post_apply_scripts(self):
        """
        Execute post-apply scripts using local-exec provisioners.

        Creates a null resource with local-exec provisioner for each script
        in the post_apply_scripts list. Scripts are executed sequentially
        after all other infrastructure resources are created.

        **Script Execution:**

        * Each script runs as a separate null resource
        * Scripts execute in the order they appear in the list
        * Failures in scripts don't prevent deployment completion
        * All scripts depend on core infrastructure being ready

        **Error Handling:**

        * Scripts use "on_failure: continue" to prevent deployment failures
        * Failed scripts are logged but don't halt the deployment process
        * Manual intervention may be required if critical scripts fail

        .. note::
           Post-apply scripts can be provided via the postApplyScripts parameter
           during stack initialization. If no scripts are provided, this method
           returns without creating any resources.

        .. warning::
           Scripts have access to the local environment where Terraform runs.
           Ensure scripts are safe and don't expose sensitive information.
        """
        if not self.post_apply_scripts:
            return

        # Collect dependencies for post-apply scripts
        dependencies = []
        if hasattr(self, 'secrets_manager_secret'):
            dependencies.append(self.secrets_manager_secret)

        # Create a null resource for each post-apply script
        for i, script in enumerate(self.post_apply_scripts):
            script_resource = NullResource(
                self,
                f"post_apply_script_{i}",
                depends_on=dependencies if dependencies else None
            )
            
            # Add provisioner using override
            script_resource.add_override("provisioner", [{
                "local-exec": {
                    "command": script,
                    "on_failure": "continue"
                }
            }])

    # ==================== UTILITY METHODS ====================

    def has_flag(self, flag_value):
        """
        Check if a specific flag is set in the configuration.

        :param flag_value: The flag value to check for
        :type flag_value: str
        :returns: True if the flag is set, False otherwise
        :rtype: bool
        """
        return flag_value in self.flags

    def clean_hyphens(self, text):
        """
        Remove hyphens from text for database/resource naming.

        :param text: Text to clean
        :type text: str
        :returns: Text with hyphens replaced by underscores
        :rtype: str
        """
        return text.replace("-", "_")

    def properize_s3_bucketname(self, bucket_name):
        """
        Ensure S3 bucket name follows AWS naming conventions.

        :param bucket_name: Proposed bucket name
        :type bucket_name: str
        :returns: Properly formatted bucket name
        :rtype: str
        """
        # Convert to lowercase and replace invalid characters
        clean_name = bucket_name.lower().replace("_", "-")
        # Ensure it starts and ends with alphanumeric characters
        clean_name = clean_name.strip("-.")
        return clean_name

    # ==================== SHARED OUTPUT HELPERS ====================

    def create_iam_outputs(self):
        """
        Create standard IAM-related Terraform outputs.
        
        This helper method can be called by subclasses to create
        consistent IAM outputs across all Lightsail implementations.
        """
        # IAM credentials (sensitive)
        TerraformOutput(
            self,
            "iam_user_access_key",
            value=self.service_key.id,
            sensitive=True,
            description="IAM user access key ID (sensitive)",
        )

        TerraformOutput(
            self,
            "iam_user_secret_key",
            value=self.service_key.secret,
            sensitive=True,
            description="IAM user secret access key (sensitive)",
        )

        # Secret name for reference
        TerraformOutput(
            self,
            "secrets_manager_secret_name",
            value=self.secret_name,
            description="AWS Secrets Manager secret name containing all credentials",
        )
