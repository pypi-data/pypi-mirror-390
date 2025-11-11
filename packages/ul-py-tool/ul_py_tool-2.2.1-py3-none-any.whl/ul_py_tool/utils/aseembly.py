from pydantic import BaseModel


class AssemblyComponent(BaseModel):
    repository: str
    directory: str
    tag: str
    force_disable: bool
    helm_repo_name: str
    helm_chart_name: str
    helm_chart_version: str


class AssemblyTarget(BaseModel):
    environment: str
    cluster_name: str
    kubeconfig_file: str
    encryption_key_name: str
    recreate: bool = False


class AssemblyFile(BaseModel):
    targets: dict[str, AssemblyTarget]
    components: dict[str, AssemblyComponent]
