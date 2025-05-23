# Jira 프로젝트 이슈타입 및 필드 조회 기능 개발 플랜

## 목표

- Jira 프로젝트의 이슈타입 목록 조회 API 연동
- Jira 프로젝트의 이슈타입별 생성 가능한 필드 정보 조회 API 연동
- 특정 이슈타입의 필드만 조회하는 기능 지원

## 🔍 기존 코드 분석 결과

**이미 구현된 기능들 (ProjectsMixin 및 FieldsMixin 활용 가능):**

- ✅ `jira.get_project(project_key)` - 프로젝트 정보 조회
- ✅ `jira.get_project_issue_types(project_key)` - 프로젝트 이슈타입 조회
- ✅ `jira.get_project_components(project_key)` - 프로젝트 컴포넌트 조회
- ✅ `jira.get_project_versions(project_key)` - 프로젝트 버전 조회

**아직 구현되지 않은 기능들:**

- ❌ 프로젝트의 **이슈타입별 필드 정보** 조회 (issue_createmeta)
- ❌ **특정 이슈타입의 필드만** 조회 (issue_createmeta_fieldtypes)

## 구현 방법

### ✅ 이미 완료된 MCP 도구들

1. **프로젝트 정보 받아오기** - `jira_get_project`

   - **기존 함수 활용**: `jira.get_project(project_key)`
   - **구현 상태**: ✅ 완료

2. **프로젝트 이슈타입 받아오기** - `jira_get_project_issue_types`
   - **기존 함수 활용**: `jira.get_project_issue_types(project_key)`
   - **구현 상태**: ✅ 완료

### ❌ 추가 구현 필요한 MCP 도구들

3. **프로젝트 전체 메타데이터 받아오기** - `jira_get_project_createmeta`

   - **Atlassian Python API 함수**: `jira.issue_createmeta(project, expand="projects.issuetypes.fields")`
   - 파라미터: `project` (프로젝트 ID, 예: 10803), `expand` (확장할 필드)
   - 반환: 프로젝트의 이슈타입별 생성 가능한 필드 정보 전체
   - **참고**: Cloud에서 deprecated이지만 우선 시도
   - **로직**: project_key → project_id 변환 → API 호출

4. **특정 이슈타입의 필드만 조회** - `jira_get_issue_type_fields`
   - **Atlassian Python API 함수**: `jira.issue_createmeta_fieldtypes(project, issue_type_id, start=None, limit=None)`
   - 파라미터: `project` (프로젝트 ID, 예: 10803), `issue_type_id` (이슈타입 ID)
   - 반환: 특정 프로젝트/이슈타입에 대해 생성 가능한 필드 정보
   - **로직**: project_key → project_id 변환 → API 호출

## 개발 플로우

### ✅ 완료된 작업들

1. **기존 ProjectsMixin 함수들을 활용한 MCP 도구 구현**
   - `jira_get_project` - 프로젝트 정보 조회
   - `jira_get_project_issue_types` - 프로젝트 이슈타입 조회
   - `jira_get_project_components` - 프로젝트 컴포넌트 조회 (보너스)
   - `jira_get_project_versions` - 프로젝트 버전 조회 (보너스)

### ❌ 남은 작업들

1. **이슈타입별 필드 조회 MCP 도구 구현**
   - `jira_get_project_createmeta` 함수 추가
   - `jira_get_issue_type_fields` 함수 추가
2. **프로젝트 키 → 프로젝트 ID 변환 로직 구현**
3. **테스트 코드 작성 및 실제 Jira 연동 테스트**
4. **문서화 및 예시 추가**

## 예상 함수 시그니처 (jira.py)

### ✅ 이미 구현 완료

```python
@jira_mcp.tool(tags={"jira", "read"})
async def get_project(ctx: Context, project_key: str) -> str:
    """Get project information including project ID."""

@jira_mcp.tool(tags={"jira", "read"})
async def get_project_issue_types(ctx: Context, project_key: str) -> str:
    """Get issue types available for project creation."""
```

### ❌ 추가 구현 필요

```python
@jira_mcp.tool(tags={"jira", "read"})
async def get_project_createmeta(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'GRW')")],
    expand: Annotated[str, Field(description="Fields to expand", default="projects.issuetypes.fields")] = "projects.issuetypes.fields",
) -> str:
    """Get complete create metadata for project including issue type fields."""
    # 1. project_key로 project ID 획득 (get_project 활용)
    # 2. issue_createmeta(project_id, expand) 호출
    pass

@jira_mcp.tool(tags={"jira", "read"})
async def get_issue_type_fields(
    ctx: Context,
    project_key: Annotated[str, Field(description="The project key (e.g., 'GRW')")],
    issue_type_id: Annotated[str, Field(description="The issue type ID")],
) -> str:
    """Get fields available for specific project and issue type."""
    # 1. project_key로 project ID 획득 (get_project 활용)
    # 2. issue_createmeta_fieldtypes(project_id, issue_type_id) 호출
    pass
```

## 참고

- 인증은 기존 MCP 인증 체계 활용 (`get_jira_fetcher`)
- 반환값은 JSON string (ensure_ascii=False, indent=2)
- 에러 발생 시 일관된 에러 메시지 반환
- **기존 ProjectsMixin의 함수들을 최대한 활용**하여 중복 구현 방지

## 추가 고려사항

- **프로젝트 키 → 프로젝트 ID 변환**:
  - 기존 `get_project` MCP 도구를 활용하여 프로젝트 ID 획득
  - 또는 내부적으로 `jira.get_project(project_key)`를 호출
- **에러 처리**:
  - 존재하지 않는 프로젝트 키 입력 시 적절한 에러 메시지 반환
  - API 호출 실패 시 상세한 에러 정보 제공
- **기존 MCP 패턴 준수**: 다른 jira.py 함수들과 일관된 스타일 유지
- **deprecated API 대응**: issue_createmeta가 실패할 경우 대안 방법 고려

---

## 🎯 실제 작업 수행과정 및 결과

### 1단계: 기존 코드 중복 발견 및 정리

**문제 발견:**

- 계획 단계에서 새로 구현하려던 `get_project`, `get_project_issue_types` 함수들이 이미 `issues.py`와 `projects.py`에 구현되어 있음을 발견
- JiraFetcher가 ProjectsMixin과 FieldsMixin을 상속받아 이미 필요한 기능들을 포함하고 있었음

**해결:**

- 중복 구현 대신 기존 코드 활용으로 전환
- 기존 mixin 클래스의 함수들을 직접 호출하는 방식으로 구현

### 2단계: API 파라미터 조사 및 수정

**문제 발견:**

- 초기 계획에서 `issue_createmeta_fieldtypes`가 project_id를 파라미터로 받는다고 가정했으나, 실제로는 project_key를 받음을 확인
- Atlassian Python API 소스코드 직접 조사를 통해 확인

**해결:**

- project_key → project_id 변환 로직을 제거
- project_key를 직접 API에 전달하도록 수정

### 3단계: 새 MCP 도구 구현

**구현 완료된 기능:**

1. **`jira_get_project_createmeta`**

   ```python
   @jira_mcp.tool(tags={"jira", "read"})
   async def get_project_createmeta(
       ctx: Context,
       project_key: Annotated[str, Field(description="The project key (e.g., 'GRW')")],
       expand: Annotated[str, Field(description="Fields to expand")] = "projects.issuetypes.fields",
   ) -> str:
       """Get complete create metadata for project including issue type fields."""
   ```

2. **`jira_get_issue_type_fields`**
   ```python
   @jira_mcp.tool(tags={"jira", "read"})
   async def get_issue_type_fields(
       ctx: Context,
       project_key: Annotated[str, Field(description="The project key (e.g., 'GRW')")],
       issue_type_id: Annotated[str, Field(description="The issue type ID")],
   ) -> str:
       """Get fields available for specific project and issue type."""
   ```

### 4단계: 과도한 방어 코드 제거

**문제 발견:**

- 초기 구현에서 API 응답의 타입 변환을 위한 복잡한 방어 코드를 구현
- 실제로는 API가 타입 멱등성(type idempotency)을 가져 항상 dict 객체를 반환함을 확인

**해결:**

- 복잡한 타입 변환 로직 제거
- 단순히 `json.dumps()` 사용으로 간소화

### 5단계: 테스트 및 검증

**테스트 결과:**

- ✅ `jira_get_project_createmeta` - 정상 작동 확인
- ✅ `jira_get_issue_type_fields` - 정상 작동 확인
- ✅ 기존 기능들과의 호환성 확인
- ✅ 에러 처리 검증 완료

### 최종 구현 결과

**총 4개의 MCP 도구 제공:**

1. **`jira_get_project`** - 프로젝트 정보 조회 (기존 코드 활용)
2. **`jira_get_project_issue_types`** - 프로젝트 이슈타입 조회 (기존 코드 활용)
3. **`jira_get_project_createmeta`** - 프로젝트 전체 생성 메타데이터 조회 (신규 구현) ✨
4. **`jira_get_issue_type_fields`** - 특정 이슈타입 필드 조회 (신규 구현) ✨

**핵심 성과:**

- 기존 코드베이스의 중복을 제거하고 효율적으로 활용
- Atlassian API의 실제 파라미터 요구사항을 정확히 파악하여 구현
- 과도한 방어 코드를 제거하여 깔끔하고 유지보수 가능한 코드 작성
- 포괄적인 테스트를 통해 실제 Jira 환경에서의 동작 검증 완료

**상태: 🎉 작업 완료**
