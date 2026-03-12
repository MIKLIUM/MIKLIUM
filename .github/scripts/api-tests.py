import os
import sys
import json
import glob
import requests

try:
    import toml
except ImportError:
    import pip
    pip.main(["install", "toml"])
    import toml


def load_test_configs(api_dir="api"):
    configs = {}
    for config_path in sorted(glob.glob(os.path.join(api_dir, "*/config.toml"))):
        project_name = os.path.basename(os.path.dirname(config_path))
        with open(config_path, "r") as f:
            parsed = toml.load(f)

        if "test" not in parsed:
            continue

        test_section = parsed["test"]
        configs[project_name] = {
            "endpoint": test_section.get("endpoint", f"/api/{project_name}"),
            "method": test_section.get("method", "POST"),
            "cases": test_section.get("cases", [])
        }

    return configs


def should_test_project(project_name, is_schedule, changed_projects):
    if is_schedule:
        return True
    if changed_projects is None:
        return True
    return project_name in changed_projects


def run_single_test(base_url, endpoint, method, case, timeout=30):
    url = base_url + endpoint
    payload = case.get("payload", {})
    expected_key = case.get("expected_key")
    expected_value = case.get("expected_value")

    try:
        if method.upper() == "POST":
            response = requests.post(url, json=payload, timeout=timeout)
        elif method.upper() == "GET":
            response = requests.get(url, params=payload, timeout=timeout)
        else:
            response = requests.request(method, url, json=payload, timeout=timeout)

        data = response.json()

        if expected_key is not None and expected_value is not None:
            actual = data.get(expected_key)
            passed = actual == expected_value
        elif expected_key is not None:
            passed = expected_key in data
        else:
            passed = response.ok

        return {
            "passed": passed,
            "status_code": response.status_code,
            "response": data,
            "error": None
        }

    except Exception as e:
        return {
            "passed": False,
            "status_code": None,
            "response": None,
            "error": str(e)
        }


def main():
    base_url = os.environ.get("BASE_URL", "https://miklium.vercel.app")
    is_schedule = os.environ.get("IS_SCHEDULE", "false").lower() == "true"

    changed_projects_raw = os.environ.get("CHANGED_PROJECTS")
    changed_projects = None
    if changed_projects_raw and changed_projects_raw != "":
        try:
            changed_projects = json.loads(changed_projects_raw)
        except json.JSONDecodeError:
            changed_projects = None

    configs = load_test_configs()

    if not configs:
        print("No test configurations found.")
        sys.exit(1)

    print(f"MIKLIUM API Tests")
    print(f"Target: {base_url}")
    print(f"Schedule run: {is_schedule}")
    if changed_projects is not None:
        print(f"Changed projects: {', '.join(changed_projects)}")
    print("=" * 60)
    print()

    total = 0
    passed = 0
    failed = 0
    skipped_projects = 0
    failures = []

    for project_name, config in sorted(configs.items()):
        if not should_test_project(project_name, is_schedule, changed_projects):
            print(f"⏭️  {project_name} — skipped (no changes)")
            skipped_projects += 1
            print()
            continue

        cases = config["cases"]
        if not cases:
            print(f"⚠️  {project_name} — no test cases defined")
            print()
            continue

        print(f"📦 {project_name}")
        print(f"   Endpoint: {config['method']} {config['endpoint']}")
        print()

        for case in cases:
            total += 1
            case_name = case.get("name", f"Test #{total}")

            result = run_single_test(
                base_url,
                config["endpoint"],
                config["method"],
                case
            )

            if result["passed"]:
                passed += 1
                print(f"   ✅ {case_name}")
            else:
                failed += 1
                failures.append(f"{project_name}: {case_name}")
                if result["error"]:
                    print(f"   ❌ {case_name} — Error: {result['error']}")
                else:
                    print(f"   ❌ {case_name} — Status: {result['status_code']}")

            if result["response"] is not None:
                response_str = json.dumps(result["response"], indent=2)
                if len(response_str) > 500:
                    response_str = response_str[:500] + "\n      ... (truncated)"
                for line in response_str.split("\n"):
                    print(f"      {line}")

            print()

        print()

    print("=" * 60)
    print(f"Results: {passed}/{total} passed, {failed} failed, {skipped_projects} projects skipped")
    print()

    if failures:
        print("Failed tests:")
        for f in failures:
            print(f"  ❌ {f}")
        print()
        sys.exit(1)
    else:
        print("All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()