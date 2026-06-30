import os
from langchain_openai import ChatOpenAI
# CLAUDE: Claude를 사용하려면 'langchain_anthropic'에서 관련 클래스를 임포트해야 합니다.
# CLAUDE: from langchain_anthropic import ChatAnthropic
# GEMINI: Gemini를 사용하려면 'langchain_google_genai'에서 관련 클래스를 임포트해야 합니다.
# GEMINI: from langchain_google_genai import ChatGoogleGenerativeAI

# [수정] .env 파일 로드를 위한 라이브러리 임포트
from dotenv import load_dotenv

# --- 0. 환경 설정: API 키 ---
# [수정] .env 파일에서 키를 로드하고 환경 변수로 설정합니다.
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY")

# LangChain의 ChatOpenAI 클래스를 LLM(두뇌)으로 초기화합니다.
llm = ChatOpenAI(
    model="gpt-5.1",
    reasoning={ "effort": "low" }
)
# CLAUDE: 클라이언트 초기화 방식이 다릅니다. (LangChain 표준)
# CLAUDE: os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "YOUR_CLAUDE_KEY")
# CLAUDE: llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0.1)

# GEMINI: 클라이언트가 아닌 라이브러리 자체를 설정합니다. (LangChain 표준)
# GEMINI: import google.generativeai as genai
# GEMINI: os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "YOUR_GEMINI_KEY")
# GEMINI: genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
# GEMINI: llm = ChatGoogleGenerativeAI(model="gemini-3.0", temperature=0.1)


# --- 1. 외부 지식 검색(Retrieval) 시뮬레이션 ---
# 실제로는 이 부분이 벡터 DB(ChromaDB, FAISS 등) 검색 로직이 됩니다.
mock_product_manual_db = {
    "배터리 시간": "에코-드론의 최대 비행 시간은 45분이며, 고속 충전 시 30분 만에 80% 충전됩니다.",
    "카메라 사양": "에코-드론은 4K 60fps 촬영이 가능한 1인치 센서 카메라를 탑재했습니다.",
    "AS 정책": "제품 보증 기간은 1년이며, 고객 과실이 아닌 경우 무상 수리 또는 교환됩니다."
}

def retrieve_context(question: str) -> str:
    """
    질문과 가장 관련된 정보를 가상 DB에서 검색(Retrieval)합니다.
    (RAG의 'R' 담당)
    """
    # CLAUDE/GEMINI: 이 함수는 순수 Python 로직이므로 변경할 필요가 없습니다.
    if "배터리" in question:
        return mock_product_manual_db["배터리 시간"]
    elif "카메라" in question or "화질" in question:
        return mock_product_manual_db["카메라 사양"]
    elif "AS" in question or "수리" in question:
        return mock_product_manual_db["AS 정책"]
    else:
        return "" # 관련 컨텍스트 없음

# --- 2. AI 응답 생성(Generation) 함수 ---
def get_ai_response(prompt: str) -> str:
    """
    [수정] 컨텍스트로 보강된(Augmented) 프롬프트를 LangChain 챗 모델에 전달하여
    최종 응답을 생성(Generation)합니다.
    (RAG의 'G' 담당)
    """
    print("[AI에게 최종 프롬프트 전달...]\n")
    try:
        # --- LangChain (표준) ---
        # LangChain의 .invoke() 메서드를 사용합니다.
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

# --- 3. RAG 챗봇 실행 파이프라인 ---
print("--- RAG 챗봇 실행 ---")

# 3.1. 사용자 질문
question = "에코-드론 배터리 시간 알려주세요"
print(f"[고객 질문]\n{question}\n")

# 3.2. (R)etrieval: 외부 지식(컨텍스트) 검색
retrieved_context = retrieve_context(question)
print(f"[검색된 컨텍스트]\n{retrieved_context}\n")

# 3.3. (A)ugmented Generation: 프롬프트 구성
# 컨텍스트 엔지니어링의 핵심: 컨텍스트 + 지시 + 질문
final_prompt = f"""
[컨텍스트]
{retrieved_context}

[지시]
위 컨텍스트를 기반으로 고객의 질문에 친절하게 답변해주세요.
컨텍스트에 없는 내용은 절대로 추측해서 말하지 마세요.

[고객 질문]
{question}
"""
# CLAUDE/GEMINI: 이 final_prompt를 만드는 로직은 플랫폼과 상관없이 동일합니다.

# 3.4. (G)eneration: AI가 컨텍스트 기반으로 답변 생성
ai_response = get_ai_response(final_prompt)
# CLAUDE/GEMINI: 이 함수 호출 부분도 변경할 필요가 없습니다.
# CLAUDE/GEMINI: (get_ai_response 함수 내부가 이미 플랫폼별로 수정되었기 때문입니다.)

print(f"[최종 AI 답변 (RAG 적용)]\n{ai_response}")
