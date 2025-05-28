# Jira MCP 서버 개선 프로젝트

## 🤖 MCP란?
**MCP(Model Context Protocol)**는 Claude AI 같은 인공지능이 외부 시스템과 연결할 수 있게 해주는 프로토콜입니다. 쉽게 말해서 Claude가 다른 프로그램들과 대화할 수 있게 해주는 연결 도구예요.

## 💡 MCP로 무엇을 할 수 있나요?
이 Jira MCP 서버를 사용하면 Claude가 직접:
- **Jira 이슈 생성**: "버그 리포트 이슈 만들어줘"라고 하면 자동으로 생성
- **이슈 업데이트**: 상태 변경, 담당자 지정, 설명 수정 등
- **이슈 조회**: 프로젝트의 이슈들을 검색하고 정보 확인
- **워크플로 관리**: 스프린트 관리, 이슈 연결 등

즉, 복잡한 Jira 작업을 자연어로 Claude에게 요청만 하면 자동으로 처리됩니다!

---

## 🚨 기존 도구의 문제점
> **Jira 공식 MCP는 Claude Max(클로드 맥스) 를 사용해야 사용할 수 있어서, ghcr.io/sooperset/mcp-atlassian:latest 이미지를 사용해야 했습니다.** 하지만 이 도구에는 다음과 같은 문제들이 있었습니다:

### ❌ 무엇이 문제였나요?

1. **이슈 종류를 모름 → 오류 발생!**
   - Claude가 "Task", "Bug", "Feature" 같은 일반적인 이슈 타입 이름으로 이슈를 생성하려고 시도
   - 하지만 실제로는 "작업: 기술", "스토리", "결함" 같은 프로젝트별 이름을 사용해야 함
   - 결과: **"이슈 타입을 찾을 수 없습니다" 오류가 계속 발생**

2. **필수 항목을 모름 → 불완전한 이슈 생성**
   - Claude가 기본적인 필드(제목, 설명)만 채워서 이슈 생성
   - "작업시간" 같은 필수 필드가 빈 상태로 남아있음
   - 나중에 사용자가 수동으로 채워야 하는 번거로움

3. **이슈 내용이 깨져 보임**
   - Jira는 ADF라는 특별한 형식으로 텍스트를 저장하는데, 이를 지원하지 않아서
   - 이슈를 만든 후 내용을 보면 이상하게 표시되거나 읽기 어려웠어요

---

## 💡 실제 업무에서의 어려움
예를 들어 **"페이지 로딩 속도 개선 작업 이슈 만들어줘"**라고 요청하면:

**기존 버전의 실패 과정:**
- Claude: "Task 타입으로 이슈를 생성하겠습니다"
- Jira: (X) "Task 이슈 타입이 존재하지 않습니다"
- Claude: "Bug 타입으로 다시 시도하겠습니다"
- Jira: (X) "Bug 이슈 타입이 존재하지 않습니다"
- 사용자: (좌절) "결국 수동으로 해야 하는구나..."

**추가 문제:**
- Claude가 추측으로 여러 번 시도해도 계속 실패
- 사용자가 직접 이슈 타입 이름을 알려줘야 함
- 이슈가 생성되어도 중요한 필드들이 비어있음

---

## ✅ 개선된 버전의 장점
새로운 **seongwookbyeon/mcp-atlassian:latest** 버전에서는 이 모든 문제를 해결했습니다!

### 🎯 무엇이 개선되었나요?

1. **이슈 타입을 정확히 확인 → 한 번에 성공!**
   - "이 프로젝트에서 사용할 수 있는 이슈 타입이 뭐야?" 라고 물어보면 바로 답변
   - Claude가 실제 존재하는 이슈 타입으로만 생성 시도
   - 결과: **첫 번째 시도에서 바로 성공!**

2. **필수 항목을 미리 알려줌 → 완성된 이슈 생성!**
   - "작업: 기술 이슈에는 어떤 필드가 필요해?" 라고 물어보면 상세히 알려줌
   - 필수/선택 구분, 기본값, 선택 가능한 옵션까지 모두 제공
   - 결과: **모든 필수 필드가 채워진 완성된 이슈 생성!**

3. **읽기 쉬운 이슈 내용**
   - ADF 지원으로 제목, 목록, 구분선 등이 원래 의도대로 예쁘게 표시
   - 이슈 템플릿의 구조를 그대로 유지

---

## 🔧 설치 및 사용 방법

### 1. API 토큰 인증 (Cloud)
- https://id.atlassian.com/manage-profile/security/api-tokens 에 접속
- 'API 토큰 생성(Create API token)' 클릭, 이름 지정
- 생성된 토큰을 즉시 복사해 두세요

### 2. 설치
- MCP Atlassian은 Docker 이미지로 배포됩니다. (IDE 연동 시 권장)
- Docker가 설치되어 있어야 합니다.

**미리 빌드된 이미지 받기:**
```bash
docker pull seongwookbyeon/mcp-atlassian:latest
```

### 3. IDE 연동
- MCP Atlassian은 AI 어시스턴트와 IDE 연동을 위해 설계되었습니다.

> **Tip**
> - Claude Desktop: 설정 파일을 직접 수정
>   - Windows: %APPDATA%/Claude/claude_desktop_config.json
>   - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
>   - Linux: ~/.config/Claude/claude_desktop_config.json
> - Cursor: Settings → MCP → + Add new global MCP server

### 4. 설정 예시
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME",
        "-e", "CONFLUENCE_API_TOKEN",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_API_TOKEN",
        "seongwookbyeon/mcp-atlassian:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@company.com",
        "CONFLUENCE_API_TOKEN": "your_confluence_api_token",
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your_jira_api_token"
      }
    }
  }
}
```

---

## 📋 ADF란?
**ADF(Atlassian Document Format)**는 Jira에서 텍스트를 저장할 때 사용하는 특별한 형식입니다. 기존 버전에서는 이를 지원하지 않아 이슈 내용이 깨져 보였지만, 개선된 버전에서는 완벽하게 지원하여 이슈 템플릿과 서식이 정확하게 표시됩니다.

---

## 🎉 이제 무엇이 가능한가요?
개선된 버전을 사용하면:

- **"GRW 프로젝트에서 사용할 수 있는 이슈 타입 알려줘"**
  - 7개 이슈 타입과 각각의 용도를 친절히 설명
- **"작업: 기타 이슈 만들 때 어떤 필드가 필요해?"**
  - 필수 필드 4개, 선택 필드들, 그리고 각 필드에 들어갈 수 있는 값들을 모두 알려줌
- **"페이지 로딩 최적화 작업 이슈 만들어줘"**
  - 적절한 이슈 타입 선택, 필수 필드 채우기, 읽기 쉬운 형태로 결과 확인까지 한 번에!

이제 오류 없이 Claude가 첫 번째 시도에서 완벽한 이슈를 생성합니다! 🚀

개발팀이 아니어도 이해할 수 있도록 작성했지만, 설치나 설정에 어려움이 있으시면 언제든 개발팀에 문의해 주세요.
