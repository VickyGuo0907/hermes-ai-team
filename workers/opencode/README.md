# OpenCode local worker — planned integration

This is an optional Development worker, not a new department or a tested automatic adapter. No live OpenCode or Hermes Agent configuration was changed.

## Version and configuration

`opencode.v1.analysis.example.json` follows the documented v1 `provider` and `permission` shape. Check `opencode --version` and the configuration schema for your installed release first. V2 uses different provider and permission shapes; do not copy this v1 example into a v2 installation. See https://opencode.ai/docs/providers/ and https://opencode.ai/v2/docs/permissions/.

Replace both `YOUR_LOCAL_MODEL_ID` occurrences and the model-map key with the exact identifier served by LM Studio. The default endpoint is `http://127.0.0.1:1234/v1` on the same Mac. Merge deliberately with the project's existing configuration; this example is not an installer and grants only repository search/read tools while denying other tools, edits, commands, subagents, and web access. Confirm the effective permissions, including plugin and agent overrides, before a trial. Permission rules do not replace filesystem or process isolation.

## Trial checklist

1. Select a disposable repository/worktree and the intended local model. Confirm this session is local; disable sharing and unrelated plugins/cloud connections for the trial.
2. With writes and shell execution denied, ask it to locate a feature and explain the files using evidence. Verify file paths and findings yourself. Confirm no files changed.
3. Check tool-call reliability and usable context capacity with the model actually loaded; do not infer coding quality from successful chat responses.
4. For an approved small Build task, create a separate, explicitly reviewed permission configuration for approved paths and check commands. This kit does not enable Build permissions.
5. Designate one code writer per task/worktree. Record the task, model, branch and commit. A replacement session receives the handoff packet before it resumes work.
6. Submit the frozen commit and actual check results to separate verification and review. Owner approval for merge/release remains required by this workforce's operating policy.

No Hermes Agent dispatch adapter, Orca binding, provider-limit detection, or automatic takeover is implemented here. Select the worker manually and record that choice on the existing card. The owner's supplied overview image remains unchanged; this README and the article describe the optional worker extension.
