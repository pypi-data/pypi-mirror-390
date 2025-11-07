from typing import Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict

from deeploy.common.functions import to_lower_camel


class Deployment(BaseModel):
    id: str
    team_id: str
    name: str
    workspace_id: str
    deployment_authorization: Dict
    use_case_id: str
    public_url: Optional[str] = None
    description: Optional[str] = None
    active_version: Optional[Union[Dict, str]] = None
    updating_to: Optional[Union[Dict, str]] = None
    last_version: Optional[Union[Dict, str]] = None
    use_case: Optional[Union[Dict, str]] = None
    status: int
    created_at: str
    updated_at: str
    error_details: Optional[List[Dict]] = None
    documentation_templates: Optional[List[Dict]] = None
    algorithm_register_lars_codes: Optional[str] = None
    model_config = ConfigDict(alias_generator=to_lower_camel)
