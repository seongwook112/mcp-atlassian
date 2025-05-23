import asyncio
import json
from fastmcp import Client
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


async def test_get_project():
    """프로젝트 정보 조회 테스트"""
    print("=== 프로젝트 정보 조회 테스트 ===")
    print("mcp-atlassian 서버에 연결 중...")

    async with Client("http://localhost:8000/mcp") as client:
        project_key = "GRW"
        print(f"프로젝트 키: {project_key}")

        try:
            # get_project 함수 호출
            result = await client.call_tool(
                "jira_get_project", {"project_key": project_key}
            )

            # 응답 처리
            if (
                isinstance(result, list)
                and len(result) > 0
                and hasattr(result[0], "text")
            ):
                response_text = result[0].text
                response_json = json.loads(response_text)

                if "error" in response_json:
                    print(f"❌ 에러: {response_json['error']}")
                    return None
                else:
                    print(f"✅ 프로젝트 정보 조회 성공!")
                    print(f"   - 프로젝트 이름: {response_json.get('name', 'N/A')}")
                    print(f"   - 프로젝트 ID: {response_json.get('id', 'N/A')}")
                    print(f"   - 프로젝트 키: {response_json.get('key', 'N/A')}")
                    return response_json

            else:
                print("❌ 응답 형식이 예상과 다릅니다.")
                return None

        except Exception as e:
            print(f"❌ 에러 발생: {str(e)}")
            return None


async def test_get_project_issue_types():
    """프로젝트 이슈 타입 조회 테스트"""
    print("\n=== 프로젝트 이슈 타입 조회 테스트 ===")

    async with Client("http://localhost:8000/mcp") as client:
        project_key = "GRW"
        print(f"프로젝트 키: {project_key}")

        try:
            # get_project_issue_types 함수 호출
            result = await client.call_tool(
                "jira_get_project_issue_types", {"project_key": project_key}
            )

            # 응답 처리
            if (
                isinstance(result, list)
                and len(result) > 0
                and hasattr(result[0], "text")
            ):
                response_text = result[0].text
                response_json = json.loads(response_text)

                if "error" in response_json:
                    print(f"❌ 에러: {response_json['error']}")
                    return None
                else:
                    print(f"✅ 이슈 타입 조회 성공! (총 {len(response_json)}개)")
                    for i, issue_type in enumerate(
                        response_json[:3]
                    ):  # 처음 3개만 출력
                        print(
                            f"   {i+1}. {issue_type.get('name', 'N/A')} (ID: {issue_type.get('id', 'N/A')})"
                        )
                    if len(response_json) > 3:
                        print(f"   ... 외 {len(response_json) - 3}개")
                    return response_json

            else:
                print("❌ 응답 형식이 예상과 다릅니다.")
                return None

        except Exception as e:
            print(f"❌ 에러 발생: {str(e)}")
            return None


async def test_get_project_components():
    """프로젝트 컴포넌트 조회 테스트"""
    print("\n=== 프로젝트 컴포넌트 조회 테스트 ===")

    async with Client("http://localhost:8000/mcp") as client:
        project_key = "GRW"
        print(f"프로젝트 키: {project_key}")

        try:
            # get_project_components 함수 호출
            result = await client.call_tool(
                "jira_get_project_components", {"project_key": project_key}
            )

            # 응답 처리
            if (
                isinstance(result, list)
                and len(result) > 0
                and hasattr(result[0], "text")
            ):
                response_text = result[0].text
                response_json = json.loads(response_text)

                if "error" in response_json:
                    print(f"❌ 오류: {response_json['error']}")
                else:
                    print(f"✅ 컴포넌트 조회 성공! (총 {len(response_json)}개)")
                    for i, component in enumerate(response_json[:3]):  # 처음 3개만 출력
                        print(
                            f"   {i+1}. {component.get('name', 'N/A')} (ID: {component.get('id', 'N/A')})"
                        )
                    if len(response_json) > 3:
                        print(f"   ... 외 {len(response_json) - 3}개")

            else:
                print("❌ 예상하지 못한 응답 형식")

        except Exception as e:
            print(f"❌ 예외 발생: {e}")


async def test_get_project_versions():
    """프로젝트 버전 조회 테스트"""
    print("\n=== 프로젝트 버전 조회 테스트 ===")

    async with Client("http://localhost:8000/mcp") as client:
        project_key = "GRW"
        print(f"프로젝트 키: {project_key}")

        try:
            # get_project_versions 함수 호출
            result = await client.call_tool(
                "jira_get_project_versions", {"project_key": project_key}
            )

            # 응답 처리
            if (
                isinstance(result, list)
                and len(result) > 0
                and hasattr(result[0], "text")
            ):
                response_text = result[0].text
                response_json = json.loads(response_text)

                if "error" in response_json:
                    print(f"❌ 오류: {response_json['error']}")
                else:
                    print(f"✅ 버전 조회 성공! (총 {len(response_json)}개)")
                    for i, version in enumerate(response_json[:3]):  # 처음 3개만 출력
                        print(
                            f"   {i+1}. {version.get('name', 'N/A')} (ID: {version.get('id', 'N/A')})"
                        )
                    if len(response_json) > 3:
                        print(f"   ... 외 {len(response_json) - 3}개")

            else:
                print("❌ 예상하지 못한 응답 형식")

        except Exception as e:
            print(f"❌ 예외 발생: {e}")


async def test_get_project_createmeta():
    """프로젝트 생성 메타데이터 조회 테스트"""
    print("\n=== 프로젝트 생성 메타데이터 조회 테스트 ===")

    async with Client("http://localhost:8000/mcp") as client:
        project_key = "GRW"
        print(f"프로젝트 키: {project_key}")

        try:
            # get_project_createmeta 함수 호출
            result = await client.call_tool(
                "jira_get_project_createmeta", {"project_key": project_key}
            )

            # 응답 처리
            if (
                isinstance(result, list)
                and len(result) > 0
                and hasattr(result[0], "text")
            ):
                response_text = result[0].text
                response_json = json.loads(response_text)

                if "error" in response_json:
                    print(f"❌ 에러: {response_json['error']}")
                    return None
                else:
                    print(f"✅ 생성 메타데이터 조회 성공!")

                    # projects 정보 출력
                    if "projects" in response_json:
                        projects = response_json["projects"]
                        print(f"   프로젝트 개수: {len(projects)}")

                        for project in projects:
                            print(
                                f"   프로젝트: {project.get('name', 'N/A')} ({project.get('key', 'N/A')})"
                            )

                            # 이슈타입 정보 출력
                            if "issuetypes" in project:
                                issue_types = project["issuetypes"]
                                print(f"     이슈타입 개수: {len(issue_types)}")

                                for issue_type in issue_types[:2]:  # 처음 2개만 출력
                                    print(
                                        f"     - {issue_type.get('name', 'N/A')} (ID: {issue_type.get('id', 'N/A')})"
                                    )

                                    # 필드 정보 출력
                                    if "fields" in issue_type:
                                        fields = issue_type["fields"]
                                        print(f"       필드 개수: {len(fields)}")
                                        field_names = list(fields.keys())[
                                            :5
                                        ]  # 처음 5개 필드명만
                                        print(
                                            f"       필드 예시: {', '.join(field_names)}"
                                        )

                    return response_json

            else:
                print("❌ 응답 형식이 예상과 다릅니다.")
                return None

        except Exception as e:
            print(f"❌ 에러 발생: {str(e)}")
            return None


async def test_get_issue_type_fields(issue_type_id):
    """특정 이슈타입의 필드 조회 테스트"""
    print(f"\n=== 특정 이슈타입 필드 조회 테스트 (이슈타입 ID: {issue_type_id}) ===")

    async with Client("http://localhost:8000/mcp") as client:
        project_key = "GRW"
        print(f"프로젝트 키: {project_key}")
        print(f"이슈타입 ID: {issue_type_id}")

        try:
            # get_issue_type_fields 함수 호출
            result = await client.call_tool(
                "jira_get_issue_type_fields",
                {"project_key": project_key, "issue_type_id": str(issue_type_id)},
            )

            # 응답 처리
            if (
                isinstance(result, list)
                and len(result) > 0
                and hasattr(result[0], "text")
            ):
                response_text = result[0].text
                response_json = json.loads(response_text)

                if "error" in response_json:
                    print(f"❌ 에러: {response_json['error']}")
                    return None
                else:
                    print(f"✅ 이슈타입 필드 조회 성공!")

                    if isinstance(response_json, list):
                        print(f"   필드 개수: {len(response_json)}")
                        for i, field in enumerate(response_json[:5]):  # 처음 5개만 출력
                            if isinstance(field, dict):
                                field_name = field.get("name", "N/A")
                                field_id = field.get("id", "N/A")
                                field_type = field.get("type", "N/A")
                                print(
                                    f"   {i+1}. {field_name} (ID: {field_id}, 타입: {field_type})"
                                )

                    return response_json

            else:
                print("❌ 응답 형식이 예상과 다릅니다.")
                return None

        except Exception as e:
            print(f"❌ 에러 발생: {str(e)}")
            return None


async def main():
    """메인 테스트 함수"""
    print("🚀 Jira 프로젝트 메타데이터 MCP 도구 테스트 시작\n")

    # 1. 프로젝트 정보 조회
    project_info = await test_get_project()

    # 2. 프로젝트 이슈타입 조회
    issue_types = await test_get_project_issue_types()

    # 3. 프로젝트 생성 메타데이터 조회
    createmeta = await test_get_project_createmeta()

    # 4. 특정 이슈타입의 필드 조회 (첫 번째 이슈타입 사용)
    if issue_types and isinstance(issue_types, list) and len(issue_types) > 0:
        first_issue_type = issue_types[0]
        issue_type_id = first_issue_type.get("id")
        if issue_type_id:
            await test_get_issue_type_fields(issue_type_id)
        else:
            print(
                "\n⚠️  이슈타입 ID를 찾을 수 없어 특정 이슈타입 필드 테스트를 건너뜁니다."
            )
    else:
        print(
            "\n⚠️  이슈타입 정보를 가져올 수 없어 특정 이슈타입 필드 테스트를 건너뜁니다."
        )

    print("\n🎉 모든 테스트 완료!")


if __name__ == "__main__":
    print("🚀 테스트 스크립트 실행 중...")
    print("⚠️  MCP 서버가 http://localhost:8000에서 실행 중인지 확인하세요!")
    print()

    asyncio.run(main())
