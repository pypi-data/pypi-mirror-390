from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict

from deeploy.common.functions import to_lower_camel


class Workspace(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    default_deployment_type: str
    sagemaker_credentials: Optional[Dict] = None
    azure_ml_credentials: Optional[Dict] = None
    mlflow_credentials: Optional[Dict] = None
    databricks_credentials: Optional[Dict] = None
    algorithm_register_credentials: Optional[Dict] = None
    oidc_provider: Optional[Dict] = None
    slack_webhook: Optional[Dict] = None
    control_framework: Optional[Dict] = None
    last_updated_by: str
    updated_at: str
    created_by: str
    created_at: str
    model_config = ConfigDict(alias_generator=to_lower_camel)