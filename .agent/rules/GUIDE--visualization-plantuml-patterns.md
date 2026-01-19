---
trigger: model_decision
---

# GUIDE-1.4 - Documentation & Visualization Standards - PATTERNS

**Version:** 1.4
**Date:** 2026-01-09  
**Status:** Active  
**Fragment:** PATTERNS - Diagram Patterns for Plans, Architecture, Testing
**Scope:** Reusable PlantUML patterns for different use cases

---

## Part 1: Plan Phase Versioning with PlantUML

### 1.1 Plan Hierarchy Diagram

**Purpose:** Show parent plan and child phases relationship
**Best for:** Feature plans, test case investigations
**Diagram Type:** Rectangle diagram (hierarchy)

#### Standard Feature Plan Hierarchy

```plantuml
@startuml
skinparam backgroundColor white
skinparam defaultFontName Arial
skinparam shadowing false

' Define skinparams
skinparam rectangle<<planning>> {
    BackgroundColor #e1f5ff
    BorderColor #01579b
    FontColor #01579b
    BorderThickness 2
}

skinparam rectangle<<complete>> {
    BackgroundColor #c8e6c9
    BorderColor #1b5e20
    FontColor #1b5e20
    BorderThickness 2
}

skinparam rectangle<<inProgress>> {
    BackgroundColor #fff9c4
    BorderColor #f57f17
    FontColor #f57f17
    BorderThickness 2
}

skinparam rectangle<<info>> {
    BackgroundColor #e0e0e0
    BorderColor #212121
    FontColor #212121
    BorderThickness 2
}

' Define nodes
rectangle "📋 Plan 4.1\\nVector Store Improvements" <<planning>> as Plan

rectangle "✅ Phase 4.1.1\\nDatabase Schema Refactor" <<complete>> as Phase1
rectangle "✅ Phase 4.1.2\\nSearch API Implementation" <<complete>> as Phase2
rectangle "⚙️ Phase 4.1.3\\nUI Integration" <<inProgress>> as Phase3

rectangle "📦 Deliverables\\nSchema, Migration Scripts" <<info>> as P1Deliver
rectangle "📦 Deliverables\\nREST Endpoints, Query Parser" <<info>> as P2Deliver
rectangle "📦 Deliverables\\nFilter UI, Preferences" <<info>> as P3Deliver

' Define connections
Plan --> Phase1
Plan --> Phase2
Plan --> Phase3

Phase1 --> P1Deliver
Phase2 --> P2Deliver
Phase3 --> P3Deliver
@enduml
```

### 1.2 Timeline Diagram

**Purpose:** Show chronological progression of phases
**Best for:** Release planning, sprint timelines
**Diagram Type:** Activity diagram (timeline)

```plantuml
@startuml
skinparam backgroundColor white
skinparam activityBackgroundColor #e1f5ff
skinparam activityBorderColor #01579b
skinparam activityFontColor #01579b
skinparam activityDiamondBackgroundColor #fff9c4

start
:📋 Plan Created;
:✅ Phase 1 Complete;
:✅ Phase 2 Complete;
:⚙️ Phase 3 In Progress;
stop
@enduml
```

---

## Part 2: Coding Conventions & Architecture

### 2.1 MVVM Architecture Diagram

**Purpose:** Show Model-View-ViewModel relationships and data flow
**Best for:** MAUI architecture documentation
**Diagram Type:** Class diagram

#### MAUI MVVM Pattern with Dependency Injection

```plantuml
@startuml
' Kényszerítsük a Class diagram módot az elején
allow_mixing 

skinparam backgroundColor white
skinparam classBackgroundColor white
skinparam classBorderColor black
skinparam classFontSize 12

' Style customization per class
skinparam class<<View>> {
    BackgroundColor #e1f5ff
    BorderColor #01579b
    FontColor #01579b
    BorderThickness 2
}

skinparam class<<ViewModel>> {
    BackgroundColor #fff9c4
    BorderColor #f57f17
    FontColor #f57f17
    BorderThickness 2
}

skinparam class<<Service>> {
    BackgroundColor #c8e6c9
    BorderColor #1b5e20
    FontColor #1b5e20
    BorderThickness 2
}

skinparam class<<Repository>> {
    BackgroundColor #bbdefb
    BorderColor #0d47a1
    FontColor #0d47a1
    BorderThickness 2
}

skinparam class<<Model>> {
    BackgroundColor #ffccbc
    BorderColor #d84315
    FontColor #d84315
    BorderThickness 2
}

title MVVM Architecture - Data Binding Flow

class "View" <<View>> {
    +InitializeComponent()
    -BindingContext
    -OnPropertyChanged()
}

class ViewModel <<ViewModel>> {
    +ObservableProperty<T>
    +ICommand RelayCommand
    +RelayCommandAsync()
    -Model: IService
}

class Service <<Service>> {
    +GetDataAsync()
    +SaveDataAsync()
    -Repository: IRepository
}

class Repository <<Repository>> {
    +QueryAsync()
    +InsertAsync()
    -DbContext: SQLiteAsyncConnection
}

class Model <<Model>> {
    -Id: int
    -Name: string
    -CreatedDate: DateTime
}

View --> ViewModel : DataBinding
ViewModel --> Service : Dependency Injection
Service --> Repository : Abstraction
Repository --> Model : Entities
@enduml
```

### 2.2 Class Dependency Diagram (CORRECTED)

**Purpose:** Show class relationships and dependencies
**Best for:** Refactoring documentation, architecture reviews
**Correction:** **Uses Bracket Notation `[...]` instead of explicit `component` keyword.**

```plantuml
@startuml
skinparam backgroundColor white
skinparam packageBackgroundColor #e1f5ff
skinparam packageBorderColor #01579b
skinparam packageFontColor #01579b

package "UI Layer" {
    [MainPage] <<View>>
    [HexagramViewModel] <<ViewModel>>
}

package "Service Layer" {
    [IChingService] <<Service>>
    [DivinationService] <<Service>>
}

package "Data Layer" {
    [HexagramRepository] <<Repository>>
    [SQLiteContext] <<Data>>
}

[MainPage] --> [HexagramViewModel]
[HexagramViewModel] --> [IChingService]
[HexagramViewModel] --> [DivinationService]
[IChingService] --> [HexagramRepository]
[DivinationService] --> [HexagramRepository]
[HexagramRepository] --> [SQLiteContext]
@enduml
```

---

## Part 3: Logging & Diagnostics

### 3.1 NLog Processing Pipeline

**Purpose:** Show how log messages flow through NLog targets
**Best for:** Logging architecture documentation
**Diagram Type:** Sequence diagram

#### NLog Event Processing

```plantuml
@startuml
skinparam backgroundColor white
skinparam sequenceArrowColor black
skinparam sequenceLifeLineBorderColor black
skinparam participantBackgroundColor #e1f5ff
skinparam participantBorderColor #01579b
skinparam participantFontColor #01579b

participant "App Code" as Code
participant "NLog Service" as NLog
participant "Log Target" as Target
participant "File System" as File
participant "Debug Console" as Console

Code -> NLog: Log.Error("Crash")
activate NLog

NLog -> Target: Filter & Format
activate Target

par Parallel Write
    Target -> File: Write Async
    Target -> Console: WriteLine
else Error Handling
    note over Target: If File locked
    Target -> Target: Retry Queue
end

deactivate Target
NLog --> Code: Complete
deactivate NLog
@enduml
```

### 3.2 Error Handling Flow

**Purpose:** Show exception handling and recovery flow
**Best for:** Error handling documentation

```plantuml
@startuml
skinparam backgroundColor white
start
:User Action;
if (Try Operation) then (success)
    :✅ Process Result;
    :Log Info;
else (exception)
    :🐛 Catch Exception;
    :Log Error with Stack Trace;
    if (Recoverable?) then (yes)
        :⚙️ Retry Logic;
    else (no)
        :🚧 Show User Error;
        :Save Crash Report;
    endif
endif
stop
@enduml
```

---

## Part 4: Testing & CI/CD

### 4.1 Test Execution Flow

**Purpose:** Show test execution pipeline
**Best for:** Testing strategy documentation

```plantuml
@startuml
skinparam backgroundColor white

skinparam rectangle<<complete>> {
    BackgroundColor #c8e6c9
    BorderColor #1b5e20
    FontColor #1b5e20
}

skinparam rectangle<<testing>> {
    BackgroundColor #bbdefb
    BorderColor #0d47a1
    FontColor #0d47a1
}

skinparam rectangle<<blocked>> {
    BackgroundColor #ffcdd2
    BorderColor #b71c1c
    FontColor #b71c1c
}

rectangle "✅ Unit Tests\\n(NUnit + Shouldly)" <<complete>> as Unit
rectangle "🧪 Integration Tests\\n(SQLite In-Memory)" <<testing>> as Integration
rectangle "🧪 UI Tests\\n(MAUI Handler Tests)" <<testing>> as UI
rectangle "🚧 E2E Tests\\n(Not Implemented)" <<blocked>> as E2E

Unit --> Integration : If Pass
Integration --> UI : If Pass
UI --> E2E : Future
@enduml
```

---

## Related Guides

- See **[GUIDE--visualization-plantuml-core.md](GUIDE--visualization-plantuml-core.md)** for PlantUML basics and accessibility
- See **[GUIDE--visualization-plantuml-styling.md](GUIDE--visualization-plantuml-styling.md)** for skinparams and color palettes

---

**Fragment Status:** This is the PATTERNS fragment covering reusable diagram patterns for plans, architecture, logging, and testing.
