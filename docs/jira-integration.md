# Jira Cloud Integration

This project can optionally create a Jira Cloud issue after triage finishes.
It works with a Jira Cloud free plan by using Jira REST API basic auth with an
Atlassian API token.

## Required `.env` values

```env
JIRA_BASE_URL=https://your-site.atlassian.net
JIRA_EMAIL=your.atlassian.email@example.com
JIRA_API_TOKEN=your_atlassian_api_token
JIRA_PROJECT_KEY=IT
JIRA_ISSUE_TYPE=Task
JIRA_MODE=issue
```

`JIRA_ISSUE_TYPE` defaults to `Task` when omitted. Use an issue type that exists
in your Jira project, such as `Task`, `Bug`, or `Service Request`.

## Jira Service Management Mode

If you want to create Jira Service Management customer requests instead of
plain Jira issues, set:

```env
JIRA_MODE=service_request
JIRA_SERVICE_DESK_ID=1
JIRA_REQUEST_TYPE_ID=1
```

You must use IDs from your own Jira Service Management project. If those IDs
are not configured, the app will skip Jira request creation and keep triage
working normally.

## Behavior

- Triage always completes even when Jira is not configured.
- Admin responses include `jira_created`, `jira_key`, `jira_url`, and
  `jira_message`.
- Regular user responses do not expose Jira integration details.
