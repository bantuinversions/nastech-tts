# Pull Request Summary

Describe the user-visible result and the reason for this change.

## Change Type

- [ ] Bug fix
- [ ] Feature or new tool
- [ ] Performance or CPU-operation change
- [ ] Documentation or repository template change
- [ ] Dependency or build-system update

## Verification Evidence

State the commands run and their results.

```text
pytest -q:
make lint:
make verify:
```

## Local Runtime and API Impact

- [ ] No synthesis behavior changed.
- [ ] NastechML parser/compiler behavior changed and has focused tests.
- [ ] Agent API or tool-catalog behavior changed and the OpenAPI schema was regenerated.
- [ ] CPU profile, queue, warm-up, or cache behavior changed and includes safe tests/benchmark evidence.
- [ ] This change does not introduce a cloud synthesis dependency or a second model family.

## Deployment Budget

- [ ] No dependency, model, or release-asset size changed materially.
- [ ] `make budget` was run against the target environment and remains within the 1 GiB cap.
- [ ] The measured impact and any updated budget evidence are described below.

## Documentation and Security

- [ ] README, API, deployment, project summary, or test matrix documentation was updated where required.
- [ ] No API key, bearer token, private audio, customer text, or model asset was added to the change.
- [ ] I reviewed [SECURITY.md](SECURITY.md) for security-sensitive changes.

## Additional Context

Add benchmark output, screenshots, compatibility notes, rollout guidance, or follow-up work.
