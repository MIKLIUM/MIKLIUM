import os
import sys
import json
import glob
import time
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


def run_single_test(base_url, endpoint, method, case, timeout=30, retries=3):
    url = base_url + endpoint
    payload = case.get("payload", {})
    expected_key = case.get("expected_key")
    expected_value = case.get("expected_value")

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=payload, timeout=timeout)
            elif method.upper() == "GET":
                response = requests.get(url, params=payload, timeout=timeout)
            else:
                response = requests.request(method, url, json=payload, timeout=timeout)

            raw_text = response.text

            if not raw_text.strip():
                last_error = f"Empty response (HTTP {response.status_code}), attempt {attempt}/{retries}"
                if attempt < retries:
                    time.sleep(5)
                    continue
                return {
                    "passed": False,
                    "status_code": response.status_code,
                    "response": None,
                    "raw": "",
                    "error": last_error
                }

            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError:
                last_error = f"Non-JSON response (HTTP {response.status_code}), attempt {attempt}/{retries}"
                if attempt < retries:
                    time.sleep(5)
                    continue
                return {
                    "passed": False,
                    "status_code": response.status_code,
                    "response": None,
                    "raw": raw_text[:1000],
                    "error": last_error
                }

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
                "raw": None,
                "error": None
            }

        except requests.exceptions.Timeout:
            last_error = f"Request timed out ({timeout}s), attempt {attempt}/{retries}"
            if attempt < retries:
                time.sleep(5)
                continue
        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection error: {e}, attempt {attempt}/{retries}"
            if attempt < retries:
                time.sleep(5)
                continue
        except Exception as e:
            last_error = str(e)
            break

    return {
        "passed": False,
        "status_code": None,
        "response": None,
        "raw": None,
        "error": last_error
    }


def warmup(base_url, configs):
    print("Warming up deployment...")

    endpoints = []
    for project_name, config in configs.items():
        endpoints.append(config["endpoint"])

    if not endpoints:
        print("  No endpoints to warm up")
        return

    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            r = requests.post(url, json={}, timeout=15)
            print(f"  POST {endpoint} -> HTTP {r.status_code}")
        except Exception as e:
            print(f"  POST {endpoint} -> failed: {e}")

    print(f"  Waiting 10 seconds for cold start...")
    time.sleep(10)

    first_endpoint = endpoints[0]
    url = base_url + first_endpoint
    try:
        r = requests.post(url, json={}, timeout=15)
        print(f"  POST {first_endpoint} -> HTTP {r.status_code} (after wait)")
    except Exception as e:
        print(f"  POST {first_endpoint} -> failed: {e}")

    print()


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
    print()

    warmup(base_url, configs)

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
                    print(f"   ❌ {case_name} — {result['error']}")
                else:
                    print(f"   ❌ {case_name} — HTTP {result['status_code']}")

            if result["response"] is not None:
                response_str = json.dumps(result["response"], indent=2)
                if len(response_str) > 500:
                    response_str = response_str[:500] + "\n      ... (truncated)"
                for line in response_str.split("\n"):
                    print(f"      {line}")
            elif result["raw"]:
                print(f"      Raw response: {result['raw'][:300]}")

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