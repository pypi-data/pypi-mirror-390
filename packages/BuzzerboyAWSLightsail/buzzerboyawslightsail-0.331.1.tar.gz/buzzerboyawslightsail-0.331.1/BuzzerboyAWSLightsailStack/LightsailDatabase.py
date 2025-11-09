"""
AWS Lightsail Database Infrastructure Stack
==========================================

This module provides a specialized AWS Lightsail database deployment stack
using CDKTF (Cloud Development Kit for Terraform) with Python.

The stack includes:
    * Lightsail Database instance (PostgreSQL)
    * Multiple databases within the instance
    * Individual database users with scoped permissions
    * Secrets Manager for credential storage per database
    * IAM resources for service access

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
from cdktf_cdktf_provider_aws import (
    lightsail_database,
)
#endregion

#region Random Provider and Resources
from cdktf_cdktf_provider_random import password

#endregion

#region Null Provider and Resources
from cdktf_cdktf_provider_null.resource import Resource as NullResource

#endregion

#region ArchitectureFlags 
class ArchitectureFlags(Enum):
    """
    Architecture configuration flags for optional components.

    Includes both base flags and database-specific flags.

    Base flags:
    :param SKIP_DEFAULT_POST_APPLY_SCRIPTS: Skip default post-apply scripts
    :param PRESERVE_EXISTING_SECRETS: Don't overwrite existing secret versions (smart detection)
    :param IGNORE_SECRET_CHANGES: Ignore all changes to secret after initial creation
    
    Database-specific flags:
    :param SKIP_DATABASE_USERS: Skip creating individual database users (use master user only)
    """
    
    # Base flags from BaseLightsailArchitectureFlags
    SKIP_DEFAULT_POST_APPLY_SCRIPTS = "skip_default_post_apply_scripts"
    PRESERVE_EXISTING_SECRETS = "preserve_existing_secrets"
    IGNORE_SECRET_CHANGES = "ignore_secret_changes"
    
    # Database-specific flags
    SKIP_DATABASE_USERS = "skip_database_users"

#endregion


class LightsailDatabaseStack(LightsailBase):
    """
    AWS Lightsail Database Infrastructure Stack.

    A comprehensive database stack that deploys:
        * Lightsail Database instance with PostgreSQL
        * Multiple databases within the instance (automated creation)
        * Individual database users with scoped permissions (automated creation)
        * Secrets Manager for storing all database credentials
        * IAM resources for programmatic access

    :param scope: The construct scope
    :param id: The construct ID
    :param kwargs: Configuration parameters including databases array

    Example:
        >>> stack = LightsailDatabaseStack(
        ...     app, "my-db-stack",
        ...     region="ca-central-1",
        ...     project_name="my-app",
        ...     databases=["app_db", "analytics_db", "logs_db"],
        ...     postApplyScripts=[
        ...         "echo 'Database deployment completed'",
        ...         "psql -h $DB_HOST -U master -d postgres -c '\\l'"
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
        Initialize the AWS Lightsail Database Infrastructure Stack.

        :param scope: The construct scope
        :param id: Unique identifier for this stack
        :param kwargs: Configuration parameters

        **Configuration Parameters:**

        :param region: AWS region (default: "us-east-1")
        :param environment: Environment name (default: "dev")
        :param project_name: Project identifier (default: "bb-aws-lightsail-db")
        :param databases: List of database names to create (required)
        :param flags: List of ArchitectureFlags to modify behavior
        :param profile: AWS profile to use (default: "default")
        :param postApplyScripts: List of shell commands to execute after deployment
        :param secret_name: Custom secret name (default: "{project_name}/{environment}/database-credentials")
        :param db_instance_size: Database instance size (default: "micro_2_0")
        :param db_engine: Database engine version (default: "postgres_14")
        :param master_username: Master database username (default: "dbmasteruser")
        :param db_publicly_accessible: Enable public access to database (default: True, required for automated provisioning)
        """
        # Set database-specific defaults
        if "project_name" not in kwargs:
            kwargs["project_name"] = "bb-aws-lightsail-db"
        if "secret_name" not in kwargs:
            project_name = kwargs["project_name"]
            environment = kwargs.get("environment", "dev")
            kwargs["secret_name"] = f"{project_name}/{environment}/database-credentials"
        
        # ===== Database-Specific Configuration (MUST be set before super().__init__) =====
        self.databases = kwargs.get("databases", [])

        # Validate required parameters
        if not self.databases:
            raise ValueError("The 'databases' parameter is required and must contain at least one database name")

        # ===== Database Configuration =====
        self.master_username = kwargs.get("master_username", "dbmasteruser")
        self.db_instance_size = kwargs.get("db_instance_size", "micro_2_0")
        self.db_engine = kwargs.get("db_engine", "postgres_14")
        self.db_publicly_accessible = kwargs.get("db_publicly_accessible", True)

        # ===== Internal State =====
        self.database_users = {}
        self.database_passwords = {}
        
        # Call parent constructor (this will call _set_default_post_apply_scripts)
        super().__init__(scope, id, **kwargs)

    def _set_default_post_apply_scripts(self):
        """
        Set default post-apply scripts specific to database deployments.
        """
        # Call parent method for base scripts
        super()._set_default_post_apply_scripts()

        # Skip if flag is set
        if BaseLightsailArchitectureFlags.SKIP_DEFAULT_POST_APPLY_SCRIPTS.value in self.flags:
            return

        # Add database-specific scripts before the final message
        databases_list = ", ".join(self.databases)
        database_scripts = [
            f"echo '️  Database Instance: {self.project_name}-db'",
            f"echo '📊 Databases Created: {databases_list}'",
            f"echo '👥 Database Users: {len(self.databases)} individual users created'",
            "echo '🔗 Connection Information:'",
            "echo '   - Instance Endpoint: Available in Terraform outputs'",
            f"echo '   - Master User: {self.master_username}'",
            "echo '   - Port: 5432 (PostgreSQL)'",
            "echo '   - Credentials: Stored in AWS Secrets Manager'",
        ]

        # Insert database-specific scripts before the final "execution started" message
        if self.post_apply_scripts:
            # Find the index of the last script and insert before it
            insert_index = len(self.post_apply_scripts) - 1
            for script in reversed(database_scripts):
                self.post_apply_scripts.insert(insert_index, script)

    def create_lightsail_resources(self):
        """
        Create Lightsail-specific resources for database deployment.

        Creates:
            * Database passwords for master and individual users
            * Lightsail PostgreSQL database instance (with public access enabled)
            * Individual databases within the instance (automated via SQL)
            * Individual database users with scoped permissions (automated via SQL)
        """
        # Generate passwords first
        self.create_database_passwords()
        
        # Create the database instance
        self.create_lightsail_database()
        
        # Prepare database user credentials
        self.create_database_users()

    def create_database_passwords(self):
        """
        Generate secure passwords for master user and individual database users.

        Creates:
            * Master database password for the instance
            * Individual passwords for each database user
            * Stores passwords in internal dictionaries for later use
        """
        # Master database password
        self.master_password = password.Password(
            self, "master_db_password", 
            length=20, 
            special=True, 
            override_special="!#$%&*()-_=+[]{}<>:?"
        )

        # Individual database user passwords
        for db_name in self.databases:
            db_password = password.Password(
                self, f"{db_name}_user_password",
                length=16,
                special=True,
                override_special="!#$%&*()-_=+[]{}<>:?"
            )
            self.database_passwords[db_name] = db_password

    def create_lightsail_database(self):
        """
        Create Lightsail PostgreSQL database instance.

        Creates a PostgreSQL database instance with the specified configuration.
        The instance will host multiple databases as specified in the databases parameter.

        Database Configuration:
            * Engine: PostgreSQL (version specified by db_engine)
            * Size: Configurable (default: micro_2_0)
            * Master database: Uses first database name from the list
            * Public Access: Configurable (default: True for automated provisioning)
            * Final snapshot: Disabled (skip_final_snapshot=True)
            
        .. note::
           Public access is enabled by default to allow automated database creation
           via local-exec provisioners. This can be disabled by setting
           db_publicly_accessible=False, but will require manual database setup.
        """
        # Use the first database name as the master database name
        master_db_name = self.clean_hyphens(self.databases[0])

        self.database = lightsail_database.LightsailDatabase(
            self,
            "database_instance",
            relational_database_name=f"{self.project_name}-db",
            blueprint_id=self.db_engine,
            bundle_id=self.db_instance_size,
            master_database_name=master_db_name,
            master_username=self.master_username,
            master_password=self.master_password.result,
            publicly_accessible=self.db_publicly_accessible,
            skip_final_snapshot=True,
            tags={
                "Environment": self.environment, 
                "Project": self.project_name, 
                "Stack": self.__class__.__name__,
                "DatabaseCount": str(len(self.databases))
            },
        )

        # Store database instance in resources registry
        self.resources["lightsail_database"] = self.database

        # Populate master credentials in secrets
        self.secrets.update({
            "master_username": self.master_username,
            "master_password": self.master_password.result,
            "master_database": master_db_name,
            "host": self.database.master_endpoint_address,
            "port": self.database.master_endpoint_port,
            "engine": self.db_engine,
            "region": self.region
        })

    def create_database_users(self):
        """
        Create individual databases and users within the Lightsail PostgreSQL instance.

        This method automates the creation of databases and users using SQL commands
        executed via null_resource provisioners. For each database in the databases list:
            1. Generates a password for the database user
            2. Stores credentials in the secrets dictionary
            3. Creates the database (if not the first one - master database)
            4. Creates a dedicated user with the generated password
            5. Grants all privileges on the database to the user

        **Automated Database Setup:**
        The following operations are performed automatically for each database:
            * CREATE DATABASE {db_name};
            * CREATE USER "{db_name}-dbuser" WITH PASSWORD '{password}';
            * GRANT ALL PRIVILEGES ON DATABASE {db_name} TO "{db_name}-dbuser";
            * GRANT ALL ON SCHEMA public TO "{db_name}-dbuser";

        .. note::
           The first database in the list is created as the master database during
           instance creation, so it's skipped in this automated provisioning process.
           
        .. note::
           Requires publicly_accessible=True on the database instance for the
           provisioner to connect from the local machine running Terraform.
        """
        if ArchitectureFlags.SKIP_DATABASE_USERS.value in self.flags:
            return

        # Store credentials for all databases
        for db_name in self.databases:
            clean_db_name = self.clean_hyphens(db_name)
            username = f"{clean_db_name}-dbuser"
            password_ref = self.database_passwords[db_name].result
            
            # Store user credentials in secrets
            self.secrets[f"{clean_db_name}_username"] = username
            self.secrets[f"{clean_db_name}_password"] = password_ref
            self.secrets[f"{clean_db_name}_database"] = clean_db_name
            
            # Store in database_users for reference
            self.database_users[clean_db_name] = {
                "username": username,
                "password": password_ref,
                "database": clean_db_name
            }

        # Skip the first database as it's already created as the master database
        databases_to_create = self.databases[1:] if len(self.databases) > 1 else []

        # Create additional databases and users using null_resource
        for db_name in databases_to_create:
            clean_db_name = self.clean_hyphens(db_name)
            username = f"{clean_db_name}-dbuser"
            password_ref = self.database_passwords[db_name].result
            
            # SQL commands to create database and user
            # Using environment variables to avoid Terraform interpolation issues
            sql_commands = f"""#!/bin/bash
set -e

echo "Creating database: {clean_db_name}"

# Wait for database to be ready (add retry logic)
for i in {{1..30}}; do
    if PGPASSWORD="$MASTER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT 1" > /dev/null 2>&1; then
        echo "Database is ready"
        break
    fi
    echo "Waiting for database to be ready... ($i/30)"
    sleep 10
done

# Create database
PGPASSWORD="$MASTER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE \\"{clean_db_name}\\";" || echo "Database {clean_db_name} may already exist"

# Create user
PGPASSWORD="$MASTER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE USER \\"{username}\\" WITH PASSWORD '$USER_PASSWORD';" || echo "User {username} may already exist"

# Grant database privileges
PGPASSWORD="$MASTER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE \\"{clean_db_name}\\" TO \\"{username}\\";"

# Grant schema privileges
PGPASSWORD="$MASTER_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d {clean_db_name} -c "GRANT ALL ON SCHEMA public TO \\"{username}\\";"

echo "Successfully created database: {clean_db_name} with user: {username}"
"""

            # Create null_resource to execute SQL commands
            db_resource = NullResource(
                self,
                f"create_database_{clean_db_name}",
                depends_on=[self.database]
            )
            
            # Add provisioner using override
            db_resource.add_override("provisioner", [{
                "local-exec": {
                    "command": sql_commands,
                    "environment": {
                        "DB_HOST": self.database.master_endpoint_address,
                        "DB_PORT": self.database.master_endpoint_port,
                        "DB_USER": self.master_username,
                        "MASTER_PASSWORD": self.master_password.result,
                        "USER_PASSWORD": password_ref,
                    }
                }
            }])

    def create_outputs(self):
        """
        Create Terraform outputs for important resource information.

        Generates outputs for:
            * Database instance endpoint
            * Master database credentials (sensitive)
            * Individual database credentials (sensitive)
            * IAM access keys (sensitive)
            * Database list and connection information

        .. note::
           Sensitive outputs are marked as such and will be hidden in
           Terraform output unless explicitly requested.
        """
        # Database instance outputs
        TerraformOutput(
            self,
            "database_endpoint",
            value=f"{self.database.master_endpoint_address}:{self.database.master_endpoint_port}",
            description="Database instance connection endpoint",
        )

        TerraformOutput(
            self,
            "database_instance_name",
            value=self.database.relational_database_name,
            description="Lightsail database instance name",
        )

        # Master credentials (sensitive)
        TerraformOutput(
            self,
            "master_username",
            value=self.master_username,
            description="Master database username",
        )

        TerraformOutput(
            self,
            "master_password",
            value=self.master_password.result,
            sensitive=True,
            description="Master database password (sensitive)",
        )

        # Database list
        TerraformOutput(
            self,
            "databases_created",
            value=json.dumps(self.databases),
            description="List of databases created in the instance",
        )

        # Individual database credentials (sensitive)
        if not self.has_flag(ArchitectureFlags.SKIP_DATABASE_USERS.value):
            for db_name in self.databases:
                clean_name = self.clean_hyphens(db_name)
                if clean_name in self.database_users:
                    user_info = self.database_users[clean_name]
                    
                    TerraformOutput(
                        self,
                        f"{clean_name}_username",
                        value=user_info["username"],
                        description=f"Database user for {clean_name}",
                    )

                    TerraformOutput(
                        self,
                        f"{clean_name}_password",
                        value=user_info["password"],
                        sensitive=True,
                        description=f"Database password for {clean_name} (sensitive)",
                    )

        # Use the shared IAM output helper
        self.create_iam_outputs()
