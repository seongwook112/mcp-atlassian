# MCP-Atlassian ADF 지원 구현 계획

## 개요

현재 MCP-Atlassian 프로젝트는 Jira API의 ADF(Atlassian Document Format) 형식을 완전히 지원하지 않고 있습니다. 테스트 결과에 따르면 직접 Jira API를 호출할 때만 ADF 형식이 정상적으로 작동하고, MCP API를 통한 ADF 문서 업데이트는 실패합니다. 이 문서는 MCP-Atlassian에서 ADF 형식을 완전히 지원하기 위한 구현 계획을 제시합니다.

## 현재 상태 및 문제점

1. **현재 상태**:

   - 일반 텍스트 필드만 성공적으로 업데이트 가능
   - ADF 문서 형식의 구조적 데이터는 MCP API를 통해 전달될 때 손상됨
   - 직접 Jira API 호출은 ADF 형식을 정상적으로 처리함

2. **원인 분석**:
   - MCP API 요청 처리 과정에서 ADF 문서 구조가 변형됨
   - ADF 문서 구조가 중첩된 JSON 객체로 이루어져 있어 MCP의 데이터 전달 방식과 호환되지 않음
   - API 요청 처리 시 직렬화/역직렬화 과정에서 데이터 손실 발생

## 개선 목표

1. MCP API를 통해 ADF 형식의 Jira 이슈 생성 지원
2. MCP API를 통해 ADF 형식의 Jira 이슈 업데이트 지원
3. ADF 문서 구조를 손상 없이 Jira API로 전달하는 메커니즘 구현
4. 기존 코드와의 호환성 유지

## 구현 계획

### 1. 수정이 필요한 파일 및 메서드

- **src/mcp_atlassian/jira/issues.py**:
  - `create_issue` 메서드: ADF 형식 요청 감지 및 직접 API 호출 분기 추가
  - `update_issue` 메서드: ADF 형식 요청 감지 및 직접 API 호출 분기 추가
  - `_format_field_value_for_write` 메서드: ADF 객체 처리 로직 추가

### 2. 주요 변경사항

#### 2.1. ADF 구조 인식 함수 추가

```python
def _is_adf_document(value: Any) -> bool:
    """ADF 문서 구조인지 확인하는 함수"""
    if not isinstance(value, dict):
        return False
    return (
        "version" in value
        and "type" in value
        and value.get("type") == "doc"
        and "content" in value
    )
```

#### 2.2. create_issue 메서드 개선

```python
def create_issue(self, project_key: str, summary: str, issue_type: str,
                 description: str | dict = "", assignee: str | None = None,
                 components: list[str] | None = None, **kwargs: Any) -> JiraIssue:
    """
    Create a new Jira issue with ADF support.

    Args:
        description: Plain text description or ADF document structure
    """
    # ADF 형식 감지
    has_adf_content = False

    # description이 ADF 형식인지 확인
    if isinstance(description, dict) and _is_adf_document(description):
        has_adf_content = True

    # 추가 필드에 ADF 형식이 있는지 확인
    for field_name, field_value in kwargs.items():
        if isinstance(field_value, dict) and _is_adf_document(field_value):
            has_adf_content = True
            break

    # ADF 형식이 있으면 직접 API 호출, 없으면 기존 jiraClient 사용
    if has_adf_content:
        return self._create_issue_with_direct_api(
            project_key, summary, issue_type, description, assignee, components, **kwargs
        )
    else:
        # 기존 jiraClient를 사용한 이슈 생성 코드 (변경 없음)
        # ... 기존 코드 ...
```

#### 2.3. update_issue 메서드 개선

```python
def update_issue(self, issue_key: str, fields: dict[str, Any] | None = None, **kwargs: Any) -> JiraIssue:
    """
    Update a Jira issue with ADF support.
    """
    update_fields = fields or {}

    # ADF 형식 감지
    has_adf_content = False

    # fields에 ADF 형식이 있는지 확인
    for field_name, field_value in update_fields.items():
        if isinstance(field_value, dict) and _is_adf_document(field_value):
            has_adf_content = True
            break

    # kwargs에 ADF 형식이 있는지 확인
    for key, value in kwargs.items():
        if isinstance(value, dict) and _is_adf_document(value):
            has_adf_content = True
            break

    # ADF 형식이 있으면 직접 API 호출, 없으면 기존 jiraClient 사용
    if has_adf_content:
        return self._update_issue_with_direct_api(issue_key, update_fields, **kwargs)
    else:
        # 기존 jiraClient를 사용한 이슈 업데이트 코드 (변경 없음)
        # ... 기존 코드 ...
```

#### 2.4. \_format_field_value_for_write 메서드 개선

```python
def _format_field_value_for_write(self, field_id: str, value: Any, field_definition: dict | None) -> Any:
    """Formats field values for the Jira API."""
    # ADF 문서 구조 검사
    if _is_adf_document(value):
        return value  # ADF 구조 그대로 반환

    # ... 기존 코드 ...
```

### 3. 직접 API 호출 메서드 구현

```python
def _create_issue_with_direct_api(
    self,
    project_key: str,
    summary: str,
    issue_type: str,
    description: str | dict = "",
    assignee: str | None = None,
    components: list[str] | None = None,
    **kwargs: Any
) -> JiraIssue:
    """ADF 형식을 포함한 이슈를 직접 API 호출로 생성하는 메서드"""
    # 요청 데이터 준비
    fields = {
        "project": {"key": project_key},
        "summary": summary,
        "issuetype": {"name": issue_type}
    }

    # description 추가
    if description:
        fields["description"] = description

    # 기타 필드 처리 (assignee, components 등)
    # ... 필드 처리 코드 ...

    # API v3 엔드포인트로 직접 호출
    api_url = f"{self.config.url}/rest/api/3/issue"

    # 인증 정보
    auth = HTTPBasicAuth(self.config.username, self.config.password)

    # 헤더 설정
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # 요청 데이터
    data = {"fields": fields}

    # API 호출
    response = requests.post(api_url, json=data, headers=headers, auth=auth)

    # 응답 처리
    if response.status_code == 201:  # Created
        result = response.json()
        issue_key = result.get("key")

        # 생성된 이슈 데이터 조회하여 JiraIssue 객체로 변환
        issue_data = self.jira.get_issue(issue_key)
        return JiraIssue.from_api_response(issue_data)
    else:
        raise Exception(f"이슈 생성 실패: {response.status_code} - {response.text}")

def _update_issue_with_direct_api(
    self,
    issue_key: str,
    fields: dict[str, Any] | None = None,
    **kwargs: Any
) -> JiraIssue:
    """ADF 형식을 포함한 이슈를 직접 API 호출로 업데이트하는 메서드"""
    update_fields = fields or {}

    # API v3 엔드포인트로 직접 호출
    api_url = f"{self.config.url}/rest/api/3/issue/{issue_key}"

    # 인증 정보
    auth = HTTPBasicAuth(self.config.username, self.config.password)

    # 헤더 설정
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # 요청 데이터
    data = {"fields": update_fields}

    # API 호출
    response = requests.put(api_url, json=data, headers=headers, auth=auth)

    # 응답 처리
    if response.status_code in [200, 204]:  # OK or No Content
        # 업데이트된 이슈 데이터 조회하여 JiraIssue 객체로 변환
        issue_data = self.jira.get_issue(issue_key)
        return JiraIssue.from_api_response(issue_data)
    else:
        raise Exception(f"이슈 업데이트 실패: {response.status_code} - {response.text}")
```

## 테스트 계획

1. **단위 테스트**:

   - ADF 문서 구조 인식 함수 테스트
   - ADF/일반 텍스트 분기 처리 테스트

2. **통합 테스트**:

   - 다양한 ADF 요소(제목, 목록, 강조, 코드 블록 등)를 포함한 이슈 생성 테스트
   - ADF 문서 업데이트 테스트
   - 직접 API 호출 방식 테스트

3. **비교 테스트**:
   - 일반 텍스트 요청은 기존 jiraClient 사용 확인
   - ADF 형식 요청은 직접 API 호출 사용 확인

## 구현 핵심 원칙

1. **기존 코드 보존**:

   - 일반 텍스트 요청에 대해서는 기존 jiraClient 코드를 그대로 유지
   - 코드 변경의 범위를 최소화하여 기존 기능에 영향을 주지 않음

2. **ADF 요청 분기 처리**:

   - ADF 형식이 감지된 경우에만 직접 API 호출 방식으로 분기
   - 이를 통해 ADF 구조가 손상되지 않고 Jira API로 전달됨

3. **API 버전 분리**:
   - 일반 요청: 기존 v2 API 사용
   - ADF 요청: v3 API 사용 (ADF 지원)

## 예상 어려움 및 해결 방안

1. **ADF 감지 정확도**:

   - 문제: ADF 문서 구조를 정확히 감지하지 못할 수 있음
   - 해결: 보수적인 검사 로직 구현 및 테스트 케이스 확대

2. **API 버전 차이**:

   - 문제: Jira API v2와 v3의 필드 형식 차이
   - 해결: API v3(ADF 지원)을 ADF 요청에만 사용하고 다른 요청은 v2 API 사용

3. **성능 영향**:
   - 문제: 직접 API 호출 방식은 추가적인 네트워크 요청 발생
   - 해결: 캐싱 및 최적화를 통해 성능 영향 최소화

## 구현 단계

1. ADF 구조 인식 함수 구현
2. create_issue 메서드에 ADF 감지 및 분기 로직 추가
3. update_issue 메서드에 ADF 감지 및 분기 로직 추가
4. 직접 API 호출 메서드 구현
5. 단위 테스트 작성
6. 통합 테스트 작성
7. 문서화 및 예제 코드 업데이트

## 결론

이 구현 계획을 통해 MCP-Atlassian에서 ADF 형식을 완전히 지원할 수 있게 되며, 사용자는 풍부한 텍스트 형식의 이슈를 생성하고 업데이트할 수 있게 됩니다. 기존 코드는 그대로 유지하면서 ADF 형식 요청에 대해서만 직접 API 호출을 사용하는 분기 방식을 통해 안정성과 호환성을 확보할 수 있습니다.

---

## 구현 결과 및 테스트 내역 (2024-06)

### 1. 실제 구현 내역

- `src/mcp_atlassian/jira/issues.py`에 ADF 분기 및 직접 API 호출 로직 구현
  - `_is_adf_document` 함수로 description이 ADF 문서인지 판별
  - ADF 문서일 때만 `_create_issue_with_adf`, `_update_issue_with_adf`를 통해 Jira REST API(v3) 직접 호출
  - 반환값을 기존 플로우와 동일하게 맞춰 Epic 처리 등 후처리도 정상 동작
  - 인증 방식은 Basic Auth(username:api_token)로 통일
- 기존 일반 텍스트/필드 요청은 기존 jiraClient 로직을 그대로 사용하여 호환성 유지
- 테스트 코드(`test_jira_mcp.py`)에서 다양한 ADF 본문으로 이슈 업데이트 테스트 구현
  - ADF 생성 유틸리티 함수 시그니처에 맞춰 코드블록, 패널 등 다양한 구조 테스트
  - 직접 API 호출 코드는 테스트에서 제거, MCP만으로 동작 검증

### 2. 테스트 결과

- MCP를 통한 ADF 이슈 업데이트가 실제 Jira 이슈(GRW-4701)에 정상 반영됨을 확인
- 다양한 ADF 구조(제목, 리스트, 코드블록, 패널 등)도 손상 없이 반영됨
- 기존 일반 텍스트/필드 업데이트도 문제없이 동작
- Epic 등 후처리 플로우도 ADF 분기에서 동일하게 정상 동작

### 3. 결론

- MCP-Atlassian에서 ADF description 지원이 완전히 구현됨
- MCP 서버만으로 Jira ADF description 업데이트가 가능함을 실제 테스트로 검증
- 기존 코드와의 호환성, Epic 등 후처리, 인증 등 모든 요구사항 충족

---

## 테스트 경험 요약 및 개선 히스토리

- **API 응답 타입 이슈**: MCP의 일부 응답이 dict가 아닌 list로 반환되어, 응답 처리 로직을 타입 체크 및 분기 처리 방식으로 개선함
- **fields 매개변수 처리**: MCP API는 fields를 반드시 딕셔너리로 직접 전달해야 하며, JSON 문자열로 전달하면 오류가 발생함. 모든 테스트 코드와 가이드에서 이를 표준화함
- **ADF 지원 한계 → 완전 지원으로 개선**:
  - 과거: 복잡한 ADF 문서 구조 업데이트는 MCP에서 실패, 일반 텍스트만 성공
  - 현재: MCP 서버 및 클라이언트 개선을 통해 description의 ADF 문서도 완전히 지원, Epic 등 후처리도 정상 동작
- **테스트 자동화**: 다양한 ADF 구조(제목, 리스트, 코드블록, 패널 등)와 일반 텍스트 모두에 대해 통합 테스트를 수행하여, 모든 케이스가 성공적으로 동작함을 검증
- **향후 권장사항**: 응답 타입 체크, fields 직접 전달, ADF 유틸리티 함수 활용 등 가이드에 명확히 반영

---
