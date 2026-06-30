import os
import logging
# [수정] LangChain의 ChatOpenAI 클래스를 임포트합니다.
from langchain_openai import ChatOpenAI 
# CLAUDE: Claude를 사용하려면 'langchain_anthropic'에서 관련 클래스를 임포트해야 합니다.
# CLAUDE: from langchain_anthropic import ChatAnthropic
# GEMINI: Gemini를 사용하려면 'langchain_google_genai'에서 관련 클래스를 임포트해야 합니다.
# GEMINI: from langchain_google_genai import ChatGoogleGenerativeAI

# --- 0. 환경 설정: API 키 ---
# 실행 전에 실제 OpenAI API 키를 입력하거나 환경 변수에 설정해야 합니다.
# 예: os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# [수정] .env 파일에서 키를 로드하는 것이 더 안전합니다.
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY")

# LangChain의 ChatOpenAI 클래스를 LLM(두뇌)으로 초기화합니다.
llm = ChatOpenAI(model="gpt-5.1", reasoning={ "effort": "low" })
# CLAUDE: 클라이언트 초기화 방식이 다릅니다.
# CLAUDE: llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0.1)
# GEMINI: 클라이언트가 아닌 라이브러리 자체를 설정합니다.
# GEMINI: import google.generativeai as genai
# GEMINI: genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "YOUR_GEMINI_KEY"))
# GEMINI: llm = ChatGoogleGenerativeAI(model="gemini-3.0", temperature=0.1)


def get_ai_response(prompt: str) -> str:
    """
    LangChain 챗 모델에 프롬프트를 전달하고, 응답을 텍스트로 반환합니다.
    (Claude/Gemini 사용 시 이 함수 내부의 LLM 객체만 교체하면 됩니다.)
    """
    try:
        # --- LangChain (표준) ---
        # [수정] LangChain의 .invoke() 메서드를 사용합니다.
        #       입력은 OpenAI API와 동일한 'messages' 리스트 형식을 사용합니다.
        response = llm.invoke([{"role": "user", "content": prompt}])
        # [수정] LangChain의 응답 객체에서 .content 속성으로 텍스트를 추출합니다.
        if isinstance(response.content, list):
            # 리스트 일 경우
            # return "".join([str(block) for block in response.content]).strip()
            # 딕셔너리 구조일 경우 (예상)
            return "".join([
                block.get('text', '') if isinstance(block, dict) else str(block) 
                for block in response.content
            ]).strip()
        else:
            # 문자열인 경우 기존대로 처리
            return response.content.strip()

        # --- CLAUDE로 변경 시 (위 llm 객체만 변경하면, 이 함수는 수정 불필요) ---
        # CLAUDE: response = llm.invoke([{"role": "user", "content": prompt}])
        # CLAUDE: return response.content.strip()

        # --- GEMINI로 변경 시 (위 llm 객체만 변경하면, 이 함수는 수정 불필요) ---
        # GEMINI: response = llm.invoke([{"role": "user", "content": prompt}])
        # GEMINI: return response.content.strip()
        
    except Exception as e:
        return f"API 호출 중 오류 발생: {e}"

print("\n" + "="*50)
print("--- [사례 2] 컨텍스트를 주입한 요청 (The Solution) ---")
print("="*50)

# 8.3절에서 배울 '컨텍스트 번들'을 정의합니다.
project_context_bundle = """
### 우리 프로젝트의 코딩 규칙 (Context Bundle) ###
1.  **명명 규칙**: 모든 함수와 변수명은 PEP 8에 따라 `snake_case`를 사용합니다. (절대 `camelCase` 사용 금지)
2.  **로깅**: `print()` 함수를 절대 사용하지 않습니다. `import logging; logger = logging.getLogger(__name__)`를 통해 모듈 레벨 로거를 사용하고, 정보 로깅은 `logger.info(...)`를 사용합니다.
3.  **DB 연결**: 모든 데이터베이스 쿼리는 `from database.connection import db`를 임포트하여, `db.get_user(user_id)`와 같은 사전 정의된 객체의 메소드를 통해 실행해야 합니다.
4.  **예외 처리**: DB 조회 실패 시 `try...except` 구문을 사용하고, 예외 발생 시 `logger.error(...)`로 기록합니다.
5.  **반환 타입**: 사용자를 찾지 못하면 `None`을 반환합니다.
"""

# 동일한 요청을 컨텍스트 번들과 함께 전달합니다.
prompt_with_context = f"""
{project_context_bundle}

---
### 작업 요청
위의 코딩 규칙을 엄격히 준수하여, "데이터베이스에서 사용자 ID로 사용자 정보를 가져오는 파이썬 함수"를 만들어줘.
"""

print(f"[요청 프롬프트]\n(컨텍스트 번들이 포함된 긴 프롬프트...)\n")

# CLAUDE/GEMINI: 이 아랫부분은 'get_ai_response' 함수가
# CLAUDE/GEMINI: LangChain의 표준 인터페이스(.invoke)를 사용하므로 변경할 필요가 없습니다.
ai_response_2 = get_ai_response(prompt_with_context)
print(f"[AI의 응답 (컨텍스트 O)]\n{ai_response_2}")
