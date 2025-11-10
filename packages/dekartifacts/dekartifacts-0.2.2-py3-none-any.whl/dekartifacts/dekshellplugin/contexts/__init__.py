from ...artifacts import DockerArtifact, HelmCommonArtifact, HelmCodingArtifact, HelmGitArtifact, \
    StaticfilesArtifact
from ...allinone import DockerAllInOne, HelmCommonAllInOne, HelmCodingAllInOne, HelmGitAllInOne, StaticfilesAllInOne

context = {
    'artifacts': {
        'Docker': DockerArtifact,
        'docker': DockerArtifact(),
        'Helm': {
            'common': HelmCommonArtifact,
            'git': HelmGitArtifact,
            'coding': HelmCodingArtifact,
        },
        'helm': {
            'common': HelmCommonArtifact(),
            'git': HelmGitArtifact(),
            'coding': HelmCodingArtifact(),
        },
        'Static': StaticfilesArtifact,
        'static': StaticfilesArtifact(),
        'aio': {
            'docker': DockerAllInOne,
            'helm': {
                'common': HelmCommonAllInOne,
                'git': HelmGitAllInOne,
                'coding': HelmCodingAllInOne,
            },
            'static': StaticfilesAllInOne,
        }
    }
}
