
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** MaidsNew
- **Date:** 2025-10-09
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001
- **Test Name:** test_user_registration_api
- **Test Code:** [TC001_test_user_registration_api.py](./TC001_test_user_registration_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 28, in <module>
  File "<string>", line 25, in test_user_registration_api
AssertionError: Expected status code 200, got 404

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d0a0374-4f04-4c4a-b987-a6f089c6c3a9/d27967ae-7967-43ce-bb57-b081a6c3510b
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002
- **Test Name:** test_user_login_api
- **Test Code:** [TC002_test_user_login_api.py](./TC002_test_user_login_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 31, in <module>
  File "<string>", line 20, in test_user_login_api
AssertionError: Expected status code 200 but got 401

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d0a0374-4f04-4c4a-b987-a6f089c6c3a9/1292c5a1-9ddc-4a76-b5a8-364434dc8db0
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003
- **Test Name:** test_get_current_user_info_api
- **Test Code:** [TC003_test_get_current_user_info_api.py](./TC003_test_get_current_user_info_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 41, in <module>
  File "<string>", line 21, in test_get_current_user_info_api
AssertionError: Login failed with status code 401

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d0a0374-4f04-4c4a-b987-a6f089c6c3a9/fc2e3c94-85a6-475b-8ccd-c98c83ef0bed
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004
- **Test Name:** test_get_all_services_api
- **Test Code:** [TC004_test_get_all_services_api.py](./TC004_test_get_all_services_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 24, in <module>
  File "<string>", line 13, in test_get_all_services_api
AssertionError: Expected status code 200, got 404

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d0a0374-4f04-4c4a-b987-a6f089c6c3a9/7892f81c-fb36-43c7-8099-bfa0c765ccff
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005
- **Test Name:** test_get_standard_services_api
- **Test Code:** [TC005_test_get_standard_services_api.py](./TC005_test_get_standard_services_api.py)
- **Test Error:** Traceback (most recent call last):
  File "<string>", line 14, in test_get_standard_services_api
  File "/var/task/requests/models.py", line 1024, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: http://localhost:8000/api/services/standard

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 28, in <module>
  File "<string>", line 16, in test_get_standard_services_api
AssertionError: Request to get standard services failed: 404 Client Error: Not Found for url: http://localhost:8000/api/services/standard

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d0a0374-4f04-4c4a-b987-a6f089c6c3a9/8ed10177-d283-4848-9185-0df24d5c523f
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC006
- **Test Name:** test_get_a_la_carte_services_api
- **Test Code:** [TC006_test_get_a_la_carte_services_api.py](./TC006_test_get_a_la_carte_services_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 26, in <module>
  File "<string>", line 16, in test_get_a_la_carte_services_api
AssertionError: Expected status code 200 but got 404

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d0a0374-4f04-4c4a-b987-a6f089c6c3a9/7308808a-eabd-4d67-b6ff-838daef9aae2
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC007
- **Test Name:** test_get_pricing_for_house_size_and_frequency_api
- **Test Code:** [TC007_test_get_pricing_for_house_size_and_frequency_api.py](./TC007_test_get_pricing_for_house_size_and_frequency_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 25, in <module>
  File "<string>", line 15, in test_get_pricing_for_house_size_and_frequency_api
AssertionError: Expected status code 200 but got 404

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d0a0374-4f04-4c4a-b987-a6f089c6c3a9/da3be269-c8e5-4a70-b617-482a960b7a7e
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC008
- **Test Name:** test_get_room_pricing_information_api
- **Test Code:** [TC008_test_get_room_pricing_information_api.py](./TC008_test_get_room_pricing_information_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 21, in <module>
  File "<string>", line 13, in test_get_room_pricing_information_api
AssertionError: Expected 200 OK, got 404

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d0a0374-4f04-4c4a-b987-a6f089c6c3a9/9d4cdcfe-b8a6-4b99-a0f5-4b3fc120b1ee
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC009
- **Test Name:** test_create_new_booking_api
- **Test Code:** [TC009_test_create_new_booking_api.py](./TC009_test_create_new_booking_api.py)
- **Test Error:** Traceback (most recent call last):
  File "<string>", line 12, in test_create_new_booking_api
  File "/var/task/requests/models.py", line 1024, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: http://localhost:8000/api/services

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 61, in <module>
  File "<string>", line 18, in test_create_new_booking_api
Exception: Failed to get valid service_id for booking creation: 404 Client Error: Not Found for url: http://localhost:8000/api/services

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d0a0374-4f04-4c4a-b987-a6f089c6c3a9/8b2ff536-9139-49f2-a906-ba083881f386
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC010
- **Test Name:** test_get_user_bookings_api
- **Test Code:** [TC010_test_get_user_bookings_api.py](./TC010_test_get_user_bookings_api.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 25, in <module>
  File "<string>", line 18, in test_get_user_bookings_api
AssertionError: Expected status 200 but got 404

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/4d0a0374-4f04-4c4a-b987-a6f089c6c3a9/478e522a-f544-4772-b73a-49764a2bd5a1
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **0.00** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---