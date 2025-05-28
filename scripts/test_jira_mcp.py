import asyncio
import json
import os
import requests
from requests.auth import HTTPBasicAuth
from fastmcp import Client
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ---------- ADF 유틸리티 함수 추가 ----------
def create_adf_document(content_nodes=None):
    """기본 ADF 문서 구조 생성"""
    return {
        "version": 1,
        "type": "doc",
        "content": content_nodes or []
    }

def create_paragraph(text_nodes=None):
    """단락 노드 생성"""
    return {
        "type": "paragraph",
        "content": text_nodes or []
    }

def create_text(text, marks=None):
    """텍스트 노드 생성"""
    node = {
        "type": "text",
        "text": text
    }
    if marks:
        node["marks"] = marks
    return node

def create_heading(text_nodes=None, level=1):
    """제목 노드 생성"""
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": text_nodes or []
    }

def create_mark(type_name, attrs=None):
    """마크 생성"""
    mark = {
        "type": type_name
    }
    if attrs:
        mark["attrs"] = attrs
    return mark

def create_bullet_list(list_items=None):
    """글머리 기호 목록 생성"""
    return {
        "type": "bulletList",
        "content": list_items or []
    }

def create_ordered_list(list_items=None):
    """번호 매기기 목록 생성"""
    return {
        "type": "orderedList",
        "content": list_items or []
    }

def create_list_item(content_nodes=None):
    """목록 항목 생성"""
    return {
        "type": "listItem",
        "content": content_nodes or []
    }

def create_code_block(text, language=""):
    """코드 블록 생성"""
    return {
        "type": "codeBlock",
        "attrs": {"language": language},
        "content": [create_text(text)]
    }

def create_panel(content_nodes=None, panel_type="info"):
    """패널 생성"""
    return {
        "type": "panel",
        "attrs": {"panelType": panel_type},
        "content": content_nodes or []
    }

# MCP를 통한 ADF 업데이트 함수
async def update_jira_issue_with_adf(client, issue_key, summary=None, description_adf=None):
    """ADF 형식을 사용하여 Jira 이슈 업데이트 (MCP 사용)"""
    fields = {}
    
    if summary:
        fields["summary"] = summary
    
    if description_adf:
        fields["description"] = description_adf
    
    # 요청 데이터 로깅
    print("MCP 요청 데이터:")
    print(json.dumps(fields, indent=2, ensure_ascii=False))
    
    try:
        # 딕셔너리를 직접 전달 (JSON 문자열로 변환하지 않음)
        update_result = await client.call_tool("jira_update_issue", {
            "issue_key": issue_key,
            "fields": fields  # 딕셔너리 직접 전달
        })
        return update_result
    except Exception as e:
        print(f"MCP 업데이트 실패: {e}")
        return None

# 직접 Jira API 호출을 통한 ADF 업데이트 함수
def update_jira_issue_with_adf_direct(issue_key, summary=None, description_adf=None):
    """ADF 형식을 사용하여 Jira 이슈 업데이트 (직접 API 호출)"""
    # .env 파일에서 로드된 환경 변수 사용
    jira_url = os.environ.get("JIRA_URL")
    jira_username = os.environ.get("JIRA_USERNAME")  # JIRA_EMAIL 대신 JIRA_USERNAME 사용
    jira_api_token = os.environ.get("JIRA_API_TOKEN")
    
    # 환경 변수 검증
    if not jira_url or not jira_username or not jira_api_token:
        print("오류: Jira API 접속 정보가 설정되지 않았습니다. .env 파일에 다음 변수를 설정하세요:")
        print(f"  JIRA_URL={jira_url or 'https://your-domain.atlassian.net'}")
        print(f"  JIRA_USERNAME={jira_username or 'your-username@example.com'}")
        print(f"  JIRA_API_TOKEN={jira_api_token and '***' or 'your-api-token'}")
        return False
    
    # API 엔드포인트
    api_url = f"{jira_url}/rest/api/3/issue/{issue_key}"
    
    # 인증 정보
    auth = HTTPBasicAuth(jira_username, jira_api_token)  # JIRA_EMAIL 대신 JIRA_USERNAME 사용
    
    # 헤더 설정
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # 요청 본문 생성
    payload = {"fields": {}}
    
    if summary:
        payload["fields"]["summary"] = summary
    
    if description_adf:
        payload["fields"]["description"] = description_adf
    
    # 요청 데이터 로깅
    print("직접 API 요청 데이터:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        # API 호출
        response = requests.put(api_url, json=payload, headers=headers, auth=auth)
        
        # 응답 확인
        if response.status_code == 204:  # 성공적인 업데이트는 204 No Content 반환
            print(f"티켓 {issue_key} 업데이트 성공")
            return True
        else:
            print(f"API 응답 코드: {response.status_code}")
            print(f"API 응답 내용: {response.text}")
            return False
    except Exception as e:
        print(f"직접 API 호출 실패: {e}")
        return False

# ---------- 테스트 함수들 ----------
async def test_jira_create():
    """Jira 티켓 생성 테스트 함수"""
    print("=== Jira 티켓 생성 테스트 ===")
    print("mcp-atlassian 서버에 연결 중...")
    async with Client("http://localhost:8000/mcp") as client:
        # 사용 가능한 도구 확인
        tools = await client.list_tools()
        print(f"사용 가능한 도구 수: {len(tools)}")
        
        # 프로젝트 키를 GRW로 고정
        project_key = "GRW"
        print(f"프로젝트 키: {project_key}")
        
        # 티켓 생성 시도
        print("새 티켓을 생성합니다...")
        try:
            create_result = await client.call_tool("jira_create_issue", {
                "project_key": project_key,
                "summary": "MCP 테스트 티켓",
                "issue_type": "결함"
            })
            
            # 응답 형식 확인 및 처리
            print(f"응답 타입: {type(create_result).__name__}")
            
            # 리스트 형식인 경우 첫 번째 항목의 텍스트를 가져와 JSON으로 파싱
            if isinstance(create_result, list) and len(create_result) > 0 and hasattr(create_result[0], 'text'):
                response_text = create_result[0].text
                response_json = json.loads(response_text)
                if 'issue' in response_json and 'key' in response_json['issue']:
                    issue_key = response_json['issue']['key']
                    print(f"티켓 생성 성공: {issue_key}")
                    return issue_key
                else:
                    print("티켓 생성 실패: 응답에서 키를 찾을 수 없습니다.")
                    print(f"응답 내용: {response_text}")
                    return None
            # 딕셔너리 형식인 경우 직접 키 추출
            elif isinstance(create_result, dict) and create_result.get("key"):
                issue_key = create_result.get("key")
                print(f"티켓 생성 성공: {issue_key}")
                return issue_key
            else:
                print("티켓 생성 실패: 응답에서 키를 찾을 수 없습니다.")
                print(f"응답 내용: {str(create_result)}")
                return None
        except Exception as e:
            print(f"티켓 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            return None

async def test_jira_update(issue_key):
    """Jira 티켓 업데이트 테스트 함수 (ADF 본문 사용)"""
    if not issue_key:
        print("=== Jira 티켓 업데이트 테스트 === [건너뜀: 티켓 키 없음]")
        return False
    
    print(f"=== Jira 티켓 업데이트 테스트 (티켓: {issue_key}) ===")
    print("mcp-atlassian 서버에 연결 중...")
    async with Client("http://localhost:8000/mcp") as client:
        # 도구 목록 확인
        tools = await client.list_tools()
        print("사용 가능한 도구 수:", len(tools))
        
        # Jira 업데이트 관련 도구 찾기
        jira_update_tools = [tool for tool in tools if hasattr(tool, 'name') and 'update' in tool.name and 'jira' in tool.name]
        if jira_update_tools:
            print("사용 가능한 Jira 업데이트 도구:")
            for tool in jira_update_tools:
                print(f"  - {tool.name}")
            
            # 적절한 도구 이름 선택
            tool_name = jira_update_tools[0].name
        else:
            tool_name = "jira_update_issue"  # 기본값
        
        print(f"선택된 도구 이름: {tool_name}")
        
        # 티켓 업데이트 시도
        print(f"티켓 {issue_key}를 업데이트합니다...")
        try:
            # ADF 문서 생성
            document = create_adf_document([
                create_heading([
                    create_text("ADF 본문으로 업데이트된 티켓")
                ], level=1),
                create_paragraph([
                    create_text("이 티켓은 "),
                    create_text("ADF", [create_mark("strong")]),
                    create_text(" 형식으로 업데이트되었습니다.")
                ]),
                create_bullet_list([
                    create_list_item([
                        create_paragraph([
                            create_text("ADF 업데이트 테스트")
                        ])
                    ]),
                    create_list_item([
                        create_paragraph([
                            create_text("본문이 ADF 객체임을 확인")
                        ])
                    ])
                ]),
                create_code_block("console.log('ADF update!');", "javascript")
            ])
            # 업데이트 필드 준비 (description에 ADF)
            update_fields = {
                "summary": "ADF 본문으로 업데이트된 MCP 테스트 티켓",
                "description": document
            }
            print(f"요청 데이터: issue_key={issue_key}, fields={update_fields}")
            # 도구 호출
            update_result = await client.call_tool(tool_name, {
                "issue_key": issue_key,
                "fields": update_fields
            })
            print(f"응답 타입: {type(update_result).__name__}")
            success = False
            if isinstance(update_result, list) and len(update_result) > 0 and hasattr(update_result[0], 'text'):
                response_text = update_result[0].text
                print(f"응답 내용: {response_text}")
                if "success" in response_text.lower() or "updated" in response_text.lower():
                    success = True
            elif update_result:
                success = True
                print(f"응답 내용: {update_result}")
            if success:
                print("티켓 업데이트 성공")
                return True
            else:
                print("티켓 업데이트 실패")
                return False
        except Exception as e:
            print(f"티켓 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

async def test_jira_comment(issue_key):
    """Jira 티켓에 코멘트 추가 테스트 함수"""
    if not issue_key:
        print("=== Jira 티켓 코멘트 추가 테스트 === [건너뜀: 티켓 키 없음]")
        return False
    
    print(f"=== Jira 티켓 코멘트 추가 테스트 (티켓: {issue_key}) ===")
    print("mcp-atlassian 서버에 연결 중...")
    async with Client("http://localhost:8000/mcp") as client:
        # 코멘트 추가 시도
        print(f"티켓 {issue_key}에 코멘트를 추가합니다...")
        try:
            comment_result = await client.call_tool("jira_add_comment", {
                "issue_key": issue_key,
                "comment": "MCP 테스트 코멘트"
            })
            
            if comment_result:
                print("코멘트 추가 성공")
                return True
            else:
                print("코멘트 추가 실패")
                return False
        except Exception as e:
            print(f"코멘트 추가 실패: {e}")
            return False

# ---------- ADF 테스트 함수 추가 ----------
async def test_jira_update_with_adf(issue_key):
    """Jira 티켓을 ADF 형식의 설명으로 업데이트하는 테스트 함수"""
    if not issue_key:
        print("=== Jira 티켓 ADF 업데이트 테스트 === [건너뜀: 티켓 키 없음]")
        return False
    
    print(f"=== Jira 티켓 ADF 업데이트 테스트 (티켓: {issue_key}) ===")
    
    # ADF 문서 생성 (내용을 완전히 새롭게 변경)
    document = create_adf_document([
        # 새로운 제목
        create_heading([
            create_text("MCP ADF 테스트 - 두 번째 시도")
        ], level=2),
        # 새로운 단락
        create_paragraph([
            create_text("이것은 두 번째 ADF 업데이트 테스트입니다. "),
            create_text("모든 내용이 새롭게 바뀌었습니다!", [create_mark("strong")])
        ]),
        # 번호 리스트
        create_ordered_list([
            create_list_item([
                create_paragraph([create_text("첫 번째 단계: 준비")])
            ]),
            create_list_item([
                create_paragraph([create_text("두 번째 단계: 실행")])
            ]),
            create_list_item([
                create_paragraph([create_text("세 번째 단계: 검증")])
            ])
        ]),
        # 코드블록
        create_code_block("for i in range(3):\n    print('Step', i+1)", "python"),
        # 정보 패널
        create_panel([
            create_paragraph([
                create_text("이 패널은 두 번째 ADF 업데이트 테스트 결과를 보여줍니다.")
            ])
        ], "info")
    ])
    
    # 1. MCP를 통한 업데이트 시도만 남김
    print("\n1. MCP를 통한 ADF 업데이트 시도:")
    async with Client("http://localhost:8000/mcp") as client:
        mcp_result = await update_jira_issue_with_adf(
            client,
            issue_key,
            summary="MCP로 ADF 업데이트된 티켓 (새로운 본문)",
            description_adf=document
        )
        
        if mcp_result:
            print("MCP를 통한 ADF 업데이트 성공")
            return True
        else:
            print("MCP를 통한 ADF 업데이트 실패")
            return False

async def run_tests():
    # 새 티켓 생성 및 기타 테스트는 생략하고, GRW-4701만 업데이트 (ADF)
    issue_key = 'GRW-4701'
    print(f'GRW-4701 이슈를 ADF 본문으로 업데이트하는 테스트를 시작합니다.')
    await test_jira_update_with_adf(issue_key)

if __name__ == "__main__":
    # run_tests 함수만 실행하여 GRW-4701 이슈를 ADF 본문으로 업데이트하는 테스트만 수행
    asyncio.run(run_tests())    