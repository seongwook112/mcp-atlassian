import asyncio

from fastmcp import Client


async def main():
    """프로젝트 컴포넌트 조회 테스트"""
    print("\n=== 프로젝트 컴포넌트 조회 테스트 ===")

    async with Client("http://localhost:8000/mcp") as client:
        project_key = "GRW"
        print(f"프로젝트 키: {project_key}")

        try:
            result = await client.call_tool(
                "jira_create_issue",
                {
                    "project_key": project_key,
                    "summary": "test",
                    "issue_type": "작업: 기술",
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {"type": "text", "text": "This is plain text."}
                                ],
                            }
                        ],
                    },
                },
            )
            print(result)
        except Exception as e:
            print(f"❌ 예외 발생: {e}")


if __name__ == "__main__":
    asyncio.run(main())
