import asyncio
import logging
from fastmcp import Client

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# 테스트할 프로젝트 키 (필요시 수정)
PROJECT_KEY = "GRW"
MCP_URL = "http://localhost:8000/mcp"


async def main():
    logger.info(f"MCP 서버에 연결: {MCP_URL}")
    async with Client(MCP_URL) as client:
        logger.info(f"get_all_project_members 호출: project_key={PROJECT_KEY}")
        try:
            # FastMCP tool 호출
            result = await client.call_tool(
                "jira_get_all_project_members", {"project_key": PROJECT_KEY}
            )
            logger.info(f"get_all_project_members 응답 타입: {type(result)}")
            logger.info(f"get_all_project_members 결과: {result}")
        except Exception as e:
            logger.error(f"오류 발생: {e}")


if __name__ == "__main__":
    asyncio.run(main())
