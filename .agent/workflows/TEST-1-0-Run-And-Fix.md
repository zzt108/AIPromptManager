---
description: Run automated tests, analyze failures, and generate a prioritized fix plan
version: "1.0"
---

1. **Preparation (Build):**
    Ensure the solution is built to catch compilation errors first.

    ```bash
    dotnet build
    ```

2. **Execution (Run Tests):**
    // turbo
    Run all tests and capture the output. Using `verbosity normal` ensures we see meaningful failure details.

    ```bash
    dotnet test --verbosity normal
    ```

3. **Analysis & Reporting:**
    Analyze the test output. If there are failures, create a step-by-step plan to fix them.

    **Prioritization Strategy (Low Hanging Fruit):**
    * **Priority 1 (Typo/Syntax):** Simple compilation errors or assertion typos.
    * **Priority 2 (Logic):** Clear assertion failures (Expected X, got Y).
    * **Priority 3 (Environment/Config):** Missing files, bad paths, or setup issues.
    * **Priority 4 (Complex):** Concurrency issues, flaky tests, or deep architectural problems.

    **Response Template:**

    # 🧪 Test Run & Fix Plan

    ## 📊 Summary

    * **Total Tests:** [N]
    * **Passed:** [N]
    * **Failed:** [N]
    * **Status:** [✅ PASS / ❌ FAIL]

    ## 🐛 Failure Analysis (Prioritized)

    ### [Priority 1/2/3] - [TestClassName.MethodName]

    * **Error:** `[Brief error message]`
    * **Root Cause:** [Hupothesis or identified cause]
    * **Fix Plan:** [Specific steps to fix]

    ## 📉 Visualization

    *Create a PlantUML diagram visualizing the failure state or the fix logic.*

    ```plantuml
    @startuml
    skinparam backgroundColor white
    skinparam defaultFontName Arial
    skinparam shadowing false
    
    ' Use standard styles
    skinparam rectangle<<pass>> {
        BackgroundColor #c8e6c9
        BorderColor #1b5e20
        FontColor #1b5e20
    }
    
    skinparam rectangle<<fail>> {
        BackgroundColor #ffcdd2
        BorderColor #b71c1c
        FontColor #b71c1c
    }

    rectangle "✅ AuthTests" <<pass>>
    rectangle "✅ parserTests" <<pass>>
    rectangle "❌ UserTests" <<fail>> {
        rectangle "❌ Login_InvalidCredentials" <<fail>>
    }

    @enduml
    ```
