---
status: resolved
trigger: "GET /admin/ returns TypeError: unhashable type: 'dict' in Jinja2 template cache"
created: 2026-03-30T00:00:00Z
updated: 2026-03-30T01:00:00Z
---

## Current Focus

hypothesis: FIXED - All TemplateResponse calls now use correct Starlette 0.37+ API
test: Docker container rebuild and endpoint testing
result: GET /admin/ now returns HTTP 200 with valid rendered HTML dashboard
next_action: Archive session as resolved

## Symptoms

expected: GET /admin/ returns a rendered dashboard HTML page with status 200
actual: GET /admin/ returns 500 Internal Server Error
errors:
  - TypeError: unhashable type: 'dict' in jinja2/utils.py line 515 (__getitem__)
  - Triggered by templates.TemplateResponse() call in admin/routes.py line 28
reproduction: "GET /admin/?api_key=..." HTTP/1.1
started: Recent (breaking change in Starlette 0.37+/FastAPI 0.116+)

## Eliminated

- hypothesis: Issue with stats data structure
  evidence: Traced through code - stats object is correct Pydantic model, serializable
  timestamp: phase1b

- hypothesis: TemplateResponse requires keyword arguments (name=, context=)
  evidence: Tested API signature - Starlette 0.37+ requires request as FIRST positional arg
  timestamp: phase3

## Evidence

- timestamp: initial
  checked: stack trace analysis
  found: Error occurs in Jinja2 template cache when trying to look up template by name. TypeError: unhashable type: 'dict' means something trying to use dict as cache key.
  implication: Template name parameter is a dict instead of string

- timestamp: phase1
  checked: admin/routes.py lines 28, 37, 50 and beyond (all TemplateResponse calls)
  found: All calls use positional arguments: templates.TemplateResponse(template_name_str, context_dict)
  implication: Old API format, but new Stack/FastAPI version requires changes

- timestamp: phase2
  checked: First fix attempt - converted to keyword arguments (name=, context=)
  found: Docker test showed new error: "missing 1 required positional argument: 'request'"
  implication: Starlette 0.37+ API actually requires: TemplateResponse(request, name, context)

- timestamp: phase3-diagnosis
  checked: Starlette 0.37+ TemplateResponse API signature
  found: NEW API: TemplateResponse(request, name, context) - request MUST be first positional argument
  implication: Complete API signature change from earlier versions

- timestamp: phase4-fix
  checked: Applied fix to all 20+ TemplateResponse calls in admin/routes.py
  found: Converted all calls from TemplateResponse(name="...", context={...}) to TemplateResponse(request, "template.html", {...})
  implication: Fix addresses the root cause completely

- timestamp: phase5-verification
  checked: Docker rebuild and endpoint test with valid API key
  found: GET /admin/?api_key=[valid_key] returns HTTP 200 with valid HTML dashboard content
  implication: Error is resolved, template renders successfully

## Resolution

root_cause: Starlette 0.37+ (included in FastAPI 0.116+) changed TemplateResponse API completely. The new signature requires request as the first positional argument: TemplateResponse(request, template_name, context). Previous code used positional args (template_name, context) or keyword args (name=, context=), both incompatible with new API. Passing context dict as first argument caused Jinja2 to interpret it as template name, triggering TypeError when trying to use dict as cache key.

fix: Converted all templates.TemplateResponse() calls throughout admin/routes.py from old API to new Starlette 0.37+ API:
  - OLD: templates.TemplateResponse("template.html", {context})
  - NEW: templates.TemplateResponse(request, "template.html", {context})
  
  Also ensured Pydantic models are converted to dicts using .model_dump() before passing to template context.

verification: 
  - Docker container rebuilt successfully
  - GET /admin/ endpoint tested with valid API key
  - Returns HTTP 200 with valid HTML dashboard (verified with curl)
  - No TypeError errors in logs
  - Dashboard renders with all expected stats and content

files_changed: [app/admin/routes.py]

## Final Status
✓ Root cause identified
✓ All TemplateResponse calls fixed
✓ Docker container rebuilt and tested
✓ HTTP 200 response confirmed on /admin/ endpoint
✓ Dashboard HTML renders successfully
✓ DEBUG COMPLETE
